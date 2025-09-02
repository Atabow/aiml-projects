#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple SPD + Census Data Join
"""

import argparse
import warnings
from pathlib import Path
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

warnings.filterwarnings('ignore')


def join_spd_with_census():
    """Join SPD crime data with census data using spatial joins."""
    
    print("Loading data...")
    
    # Find the SPD crime data file (name changes with download date)
    download_dir = Path("data/downloads/seattle")
    spd_files = list(download_dir.glob("SPD_Crime_Data__2008-Present_*.csv"))
    
    if not spd_files:
        raise FileNotFoundError("No SPD crime data file found. Run download script first.")
    elif len(spd_files) > 1:
        # Use the most recent file if multiple exist
        spd_file = max(spd_files, key=lambda x: x.stat().st_mtime)
        print(f"Multiple SPD files found, using most recent: {spd_file.name}")
    else:
        spd_file = spd_files[0]
    
    # Load data
    spd_data = pd.read_csv(spd_file)
    census_data = pd.read_csv("data/joined/king_county_census_combined.csv")
    census_data = census_data.rename(columns={'year': 'census_year'})
    
    # Load shapefiles
    shapefile_path = "data/downloads/seattle/census_shapefiles/2020/extracted/tl_2020_53_tract.shp"
    tracts = gpd.read_file(shapefile_path)
    king_county_tracts = tracts[tracts['COUNTYFP'] == '033']
    
    print(f"SPD records: {len(spd_data):,}")
    print(f"Census tracts: {len(king_county_tracts):,}")
    
    # Clean coordinates and filter to 2015+
    spd_data['Latitude'] = pd.to_numeric(spd_data['Latitude'], errors='coerce')
    spd_data['Longitude'] = pd.to_numeric(spd_data['Longitude'], errors='coerce') 
    spd_data['Offense Date'] = pd.to_datetime(spd_data['Offense Date'], errors='coerce')
    spd_data['crime_year'] = spd_data['Offense Date'].dt.year
    
    # Filter to 2015+ and valid coordinates
    spd_clean = spd_data[
        (spd_data['crime_year'] >= 2015) &
        (spd_data['Latitude'].notna()) & 
        (spd_data['Longitude'].notna()) &
        (spd_data['Latitude'] > 47.0) & (spd_data['Latitude'] < 48.0) &
        (spd_data['Longitude'] > -123.0) & (spd_data['Longitude'] < -121.0)
    ].copy()
    
    print(f"Clean records (2015+): {len(spd_clean):,}")
    
    # Spatial join
    print("Performing spatial join...")
    geometry = [Point(xy) for xy in zip(spd_clean['Longitude'], spd_clean['Latitude'])]
    spd_gdf = gpd.GeoDataFrame(spd_clean, geometry=geometry, crs='EPSG:4326')
    king_county_tracts = king_county_tracts.to_crs('EPSG:4326')
    
    # First attempt: exact match
    joined = gpd.sjoin(spd_gdf, king_county_tracts, how='left', predicate='within')
    
    # Second attempt: buffer for unmatched (improves match rate)
    unmatched = joined['GEOID'].isna()
    if unmatched.sum() > 0:
        print(f"Trying buffer for {unmatched.sum():,} unmatched records...")
        spd_buffered = spd_gdf.loc[unmatched].copy()
        spd_buffered['geometry'] = spd_buffered.geometry.buffer(0.0001)  # ~10m buffer
        buffered_matches = gpd.sjoin(spd_buffered, king_county_tracts, how='left', predicate='intersects')
        
        # Update main results with successful buffer matches
        buffer_matched = buffered_matches['GEOID'].notna()
        if buffer_matched.any():
            joined.loc[buffered_matches.index[buffer_matched], 'GEOID'] = buffered_matches.loc[buffer_matched, 'GEOID']
    
    matched_pct = (joined['GEOID'].notna().sum() / len(joined)) * 100
    print(f"Spatial match rate: {matched_pct:.1f}%")
    
    # Add census data
    print("Adding census demographics...")
    
    # Map crime year to nearest census year
    def map_census_year(year):
        if pd.isna(year): return 2020
        year = int(year)
        if year <= 2010: return 2010
        elif year >= 2023: return 2023
        else: return min([2010, 2015, 2020, 2023], key=lambda x: abs(x - year))
    
    joined['census_year'] = joined['crime_year'].apply(map_census_year)
    
    # Fix data types for merge - use tract codes instead of GEOID
    # The shapefile has TRACTCE (e.g., 102.0) and the census has tract (e.g., 102)
    joined['TRACTCE'] = joined['TRACTCE'].astype('Int64')  # Handle NaN values
    census_data['tract'] = census_data['tract'].astype('Int64')
    
    # Merge with census data using tract codes and census year
    final_data = joined.merge(
        census_data,
        left_on=['TRACTCE', 'census_year'],
        right_on=['tract', 'census_year'],
        how='left'
    )
    
    # Remove redundant and unwanted columns
    columns_to_drop = ['geometry', 'tract']  # Keep TRACTCE as primary tract identifier
    columns_to_drop = [col for col in columns_to_drop if col in final_data.columns]
    if columns_to_drop:
        final_data = final_data.drop(columns=columns_to_drop)
    
    print(f"Final dataset: {len(final_data):,} records, {len(final_data.columns)} columns")
    
    return final_data


def main(cleanup_downloads=False):
    """Main function."""
    
    # Check required files dynamically
    download_dir = Path("data/downloads/seattle")
    spd_files = list(download_dir.glob("SPD_Crime_Data__2008-Present_*.csv"))
    
    required_files = [
        "data/joined/king_county_census_combined.csv", 
        "data/downloads/seattle/census_shapefiles/2020/extracted/tl_2020_53_tract.shp"
    ]
    
    missing = [f for f in required_files if not Path(f).exists()]
    
    if not spd_files:
        missing.append("SPD_Crime_Data__2008-Present_*.csv (in data/downloads/seattle/)")
    
    if missing:
        print("Missing files:", missing)
        return
    
    # Run join
    joined_data = join_spd_with_census()
    
    # Export
    output_path = Path("data/joined/spd_census_joined.csv")
    joined_data.to_csv(output_path, index=False)
    print(f"Exported to: {output_path}")
    
    # Optional cleanup
    if cleanup_downloads:
        import shutil
        download_dir = Path("data/downloads")
        if download_dir.exists():
            shutil.rmtree(download_dir)
            print("Cleaned up download files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--cleanup', action='store_true')
    args = parser.parse_args()
    main(cleanup_downloads=args.cleanup)