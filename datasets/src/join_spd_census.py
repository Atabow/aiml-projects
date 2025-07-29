#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Practical SPD + Census Data Join Implementation
==============================================

This script provides a ready-to-use implementation for joining SPD crime data
with census demographic data using spatial joins.
"""

import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)


def join_spd_with_census(sample_size=None):
    """
    Join SPD crime data with census data using spatial joins.
    
    Args:
        sample_size (int): Number of crime records to process (None for all records)
    
    Returns:
        pandas.DataFrame: Joined dataset with crime and census data
    """
    
    print("JOINING SPD CRIME DATA WITH CENSUS DATA")
    print("="*60)
    
    # 1. Load SPD crime data
    print("Loading SPD crime data...")
    spd_data = pd.read_csv("data/downloads/seattle/SPD_Crime_Data__2008-Present_20250727.csv", 
                          nrows=sample_size)
    print(f"   Loaded {len(spd_data):,} crime records")
    
    # 2. Load census demographic data
    print("Loading census demographic data...")
    census_data = pd.read_csv("data/joined/king_county_census_combined.csv")
    # Rename year column to census_year for clarity
    if 'year' in census_data.columns:
        census_data = census_data.rename(columns={'year': 'census_year'})
    print(f"   Loaded {len(census_data):,} census tract records")
    
    # 3. Load census tract shapefiles
    print("Loading census tract boundaries...")
    shapefile_path = "data/downloads/seattle/census_shapefiles/2020/extracted/tl_2020_53_tract.shp"
    census_tracts = gpd.read_file(shapefile_path)
    king_county_tracts = census_tracts[census_tracts['COUNTYFP'] == '033'].copy()
    print(f"   Loaded {len(king_county_tracts):,} King County tract polygons")
    
    # 4. Clean SPD data - remove invalid coordinates
    print("Cleaning crime data...")
    
    # Convert coordinates to numeric, handling any non-numeric values
    spd_data['Latitude'] = pd.to_numeric(spd_data['Latitude'], errors='coerce')
    spd_data['Longitude'] = pd.to_numeric(spd_data['Longitude'], errors='coerce')
    
    # Keep ALL records, just mark invalid coordinates for spatial join
    print(f"   Total SPD records loaded: {len(spd_data):,}")
    
    # Create a subset for spatial operations (valid coordinates only)
    spd_for_spatial = spd_data[
        (spd_data['Latitude'] != -1.0) & 
        (spd_data['Longitude'] != -1.0) &
        (spd_data['Latitude'].notna()) & 
        (spd_data['Longitude'].notna()) &
        (spd_data['Latitude'] > 47.0) &  # Reasonable bounds for Seattle
        (spd_data['Latitude'] < 48.0) &
        (spd_data['Longitude'] > -123.0) &
        (spd_data['Longitude'] < -121.0)
    ].copy()
    
    print(f"   Records with valid coordinates for spatial join: {len(spd_for_spatial):,}")
    print(f"   Records with invalid/missing coordinates (will be preserved): {len(spd_data) - len(spd_for_spatial):,}")
    
    # 5. Convert subset to GeoDataFrame for spatial join
    print("Converting valid coordinates to spatial data...")
    geometry = [Point(xy) for xy in zip(spd_for_spatial['Longitude'], spd_for_spatial['Latitude'])]
    spd_gdf = gpd.GeoDataFrame(spd_for_spatial, geometry=geometry, crs='EPSG:4326')
    
    # Ensure both datasets use the same coordinate system
    king_county_tracts = king_county_tracts.to_crs('EPSG:4326')
    
    # 6. Perform spatial join on valid coordinates only
    print("Performing spatial join on records with valid coordinates...")
    joined_spatial = gpd.sjoin(spd_gdf, king_county_tracts, how='left', predicate='within')
    
    # Debug: Check what columns were created
    print(f"   Columns after spatial join: {list(joined_spatial.columns)}")
    
    # 7. Merge spatial results back with ALL original SPD data
    print("Merging spatial results back with all original SPD records...")
    
    # Extract year from offense date for all records
    spd_data['Offense Date'] = pd.to_datetime(spd_data['Offense Date'], errors='coerce')
    spd_data['crime_year'] = spd_data['Offense Date'].dt.year
    
    # Create spatial results lookup - use the actual columns that exist
    spatial_columns = ['Offense ID']  # Use Offense ID as the unique identifier
    if 'GEOID' in joined_spatial.columns:
        spatial_columns.append('GEOID')
        spatial_results = joined_spatial[spatial_columns].copy()
        spatial_results = spatial_results.rename(columns={'GEOID': 'tract_geoid'})
    elif 'tract_from_census' in joined_spatial.columns:
        spatial_columns.append('tract_from_census')
        spatial_results = joined_spatial[spatial_columns].copy()
    else:
        # Find the tract identifier column
        tract_cols = [col for col in joined_spatial.columns if 'tract' in col.lower() or 'geoid' in col.lower()]
        if tract_cols:
            spatial_columns.append(tract_cols[0])
            spatial_results = joined_spatial[spatial_columns].copy()
            spatial_results = spatial_results.rename(columns={tract_cols[0]: 'tract_geoid'})
        else:
            print("   Warning: No tract identifier found in spatial join results")
            spatial_results = joined_spatial[['Offense ID']].copy()
            spatial_results['tract_geoid'] = None
    
    # Merge all SPD data with spatial results (left join to keep all SPD records)
    all_data_with_spatial = spd_data.merge(spatial_results, on='Offense ID', how='left')
    
    # 8. Add census demographic data based on crime year
    print("Adding census demographic data based on crime year...")
    
    # Map crime years to available census years (use nearest available year)
    print("   Mapping crime years to available census years...")
    available_census_years = sorted(census_data['census_year'].unique())
    print(f"   Available census years: {available_census_years}")
    
    def map_to_census_year(crime_year):
        """Map crime year to nearest available census year."""
        if pd.isna(crime_year):
            return 2020  # Default to 2020 for missing dates
        
        crime_year = int(crime_year)
        
        # Find the closest available census year
        if crime_year <= 2010:
            return 2010
        elif crime_year >= 2023:
            return 2023
        else:
            # Find the closest year
            closest_year = min(available_census_years, key=lambda x: abs(x - crime_year))
            return closest_year
    
    # Perform direct merge using GEOID from spatial join and year matching
    print("   Merging all SPD data with census demographics...")
    
    # Create temporary columns only for the merge operation
    temp_census_year = all_data_with_spatial['crime_year'].apply(map_to_census_year)
    
    # Extract tract code from GEOID for matching
    if 'tract_geoid' in all_data_with_spatial.columns:
        temp_tract_code = pd.to_numeric(
            all_data_with_spatial['tract_geoid'].astype(str).str[-6:], errors='coerce'
        ).astype('Int64')
    else:
        temp_tract_code = None
        
    temp_census_tract = pd.to_numeric(
        census_data['GEOID'].astype(str).str.zfill(11).str[:6], errors='coerce'
    ).astype('Int64')
    
    # Create temporary DataFrames for the merge
    spd_for_merge = all_data_with_spatial.copy()
    spd_for_merge['_temp_tract'] = temp_tract_code  
    spd_for_merge['_temp_year'] = temp_census_year
    
    census_for_merge = census_data.copy()
    census_for_merge['_temp_tract'] = temp_census_tract
    
    try:
        final_data = spd_for_merge.merge(
            census_for_merge, 
            left_on=['_temp_tract', '_temp_year'],
            right_on=['_temp_tract', 'census_year'],
            how='left',
            suffixes=('', '_census')
        )
        # Remove temporary columns
        final_data = final_data.drop(columns=['_temp_tract', '_temp_year'], errors='ignore')
        
    except ValueError as e:
        print(f"   Warning: Error during merge operation: {e}")
        print("   Attempting fallback merge without year matching...")
        final_data = spd_for_merge.merge(
            census_for_merge[census_for_merge['census_year'] == 2020], 
            left_on='_temp_tract',
            right_on='_temp_tract',
            how='left',
            suffixes=('', '_census')
        )
        # Remove temporary columns
        final_data = final_data.drop(columns=['_temp_tract', '_temp_year'], errors='ignore')
    
    # Keep ALL original SPD columns plus added census data
    print("Preserving all original SPD columns plus census demographics...")
    
    # Don't filter columns - keep everything except temporary merge columns
    final_clean = final_data.copy()
    
    # Remove any remaining temporary or duplicate columns
    temp_cols_to_remove = [col for col in final_clean.columns if col.startswith('_temp') or col.endswith('_census')]
    if temp_cols_to_remove:
        final_clean = final_clean.drop(columns=temp_cols_to_remove, errors='ignore')
        print(f"   Removed temporary columns: {temp_cols_to_remove}")
    
    # Filter out records before 2015 for better data quality and census alignment
    print("Filtering records to 2015 and later for better data quality...")
    before_filter = len(final_clean)
    final_clean = final_clean[final_clean['crime_year'] >= 2015].copy()
    after_filter = len(final_clean)
    print(f"   Filtered out {before_filter - after_filter:,} records before 2015")
    print(f"   Keeping {after_filter:,} records from 2015 onwards")
    
    # 9. Report results
    total_crimes = len(final_clean)
    
    # Check for geographic identifier columns from the original data
    geo_columns = ['GEOID', 'tract_geoid']
    matched_crimes = 0
    geo_col_used = None
    
    for col in geo_columns:
        if col in final_clean.columns:
            matched_count = len(final_clean[final_clean[col].notna()])
            if matched_count > matched_crimes:
                matched_crimes = matched_count
                geo_col_used = col
    
    print("\nJOIN RESULTS:")
    print(f"   Total crimes (2015+): {total_crimes:,}")
    print(f"   Successfully matched with census data: {matched_crimes:,} ({matched_crimes/total_crimes*100:.1f}%)")
    print(f"   Records without census match: {total_crimes - matched_crimes:,}")
    print(f"   Total columns in final dataset: {len(final_clean.columns)}")
    print("   All original SPD columns preserved plus census demographics")
    
    if matched_crimes > 0 and geo_col_used:
        # Show tract coverage
        tract_counts = final_clean[final_clean[geo_col_used].notna()][geo_col_used].value_counts()
        print(f"   Tracts with crimes: {len(tract_counts):,}")
        print(f"   Average crimes per tract: {tract_counts.mean():.1f}")
    
    return final_clean


def export_for_analysis(joined_data, filename="spd_census_joined.csv"):
    """Export the joined dataset for analysis."""
    output_path = Path("data/joined") / filename
    joined_data.to_csv(output_path, index=False)
    print(f"\nData exported to: {output_path}")
    print(f"   Rows: {len(joined_data):,}")
    print(f"   Columns: {len(joined_data.columns):,}")
    return output_path


def sample_analysis(joined_data):
    """Show sample analysis possibilities with the joined data."""
    print("\nSAMPLE ANALYSIS OPPORTUNITIES")
    print("="*50)
    print("Note: Analysis includes crime data from 2015 onwards for better data quality")
    
    # Filter to successfully matched records
    matched_data = joined_data[joined_data['GEOID'].notna()].copy()
    
    if len(matched_data) == 0:
        print("No matched data for analysis")
        return
    
    # Crime by income level (using year-matched census data)
    print("CRIME BY INCOME LEVEL (Year-Matched Census Data):")
    if 'MedianHouseholdIncome' in matched_data.columns:
        matched_data['income_category'] = pd.cut(
            matched_data['MedianHouseholdIncome'], 
            bins=[0, 50000, 75000, 100000, float('inf')],
            labels=['Low (<$50k)', 'Medium ($50-75k)', 'High ($75-100k)', 'Very High (>$100k)']
        )
        
        income_crimes = matched_data.groupby('income_category').size()
        for category, count in income_crimes.items():
            print(f"   {category}: {count:,} crimes")
    else:
        print("   MedianHouseholdIncome column not available")
    
    # Simple temporal analysis by crime year
    print("\nTEMPORAL ANALYSIS:")
    if 'crime_year' in matched_data.columns:
        year_analysis = matched_data.groupby('crime_year').agg({
            'MedianHouseholdIncome': 'mean' if 'MedianHouseholdIncome' in matched_data.columns else lambda x: 0,
            'TotalPopulation': 'mean' if 'TotalPopulation' in matched_data.columns else lambda x: 0,
            'Offense ID': 'count'  # Count unique offenses, not reports
        }).round(0)
        print("   Crime counts by year:")
        print(year_analysis.head().to_string())
    else:
        print("   crime_year column not available")
    
    # Crime by race/ethnicity
    print("\nAVERAGE DEMOGRAPHICS OF CRIME LOCATIONS:")
    avg_demographics = matched_data.groupby('Offense Category')[
        ['TotalPopulation', 'MedianHouseholdIncome', 'WhiteAlone', 'AsianAlone', 'BlackAfricanAmericanAlone']
    ].mean()
    
    print(avg_demographics.round(0).head())
    
    # Neighborhood analysis
    print("\nTOP NEIGHBORHOODS BY CRIME COUNT:")
    neighborhood_crimes = matched_data['Neighborhood'].value_counts().head()
    for neighborhood, count in neighborhood_crimes.items():
        if pd.notna(neighborhood):
            print(f"   {neighborhood}: {count:,} crimes")


def cleanup_downloaded_files():
    """Clean up downloaded raw files after successful join."""
    print("\nCleaning up downloaded files...")
    
    download_dir = Path("data/downloads")
    if download_dir.exists():
        import shutil
        try:
            shutil.rmtree(download_dir)
            print(f"✓ Removed download directory: {download_dir}")
            print("  This saves disk space while preserving the final joined dataset")
        except OSError as e:
            print(f"Warning: Could not remove download directory: {e}")
    else:
        print("No download directory found to clean up")


def main(cleanup_downloads=False):
    """
    Main function to run the join process.
    
    Args:
        cleanup_downloads (bool): Whether to delete downloaded files after successful join
    """
    
    # Check if required files exist
    required_files = [
        "data/downloads/seattle/SPD_Crime_Data__2008-Present_20250727.csv",
        "data/joined/king_county_census_combined.csv",
        "data/downloads/seattle/census_shapefiles/2020/extracted/tl_2020_53_tract.shp"
    ]
    
    missing_files = [f for f in required_files if not Path(f).exists()]
    if missing_files:
        print("Missing required files:")
        for f in missing_files:
            print(f"   {f}")
        print("\nRun download_seattle_census.py first to download census data and shapefiles.")
        return
    
    # Perform the join
    try:
        joined_data = join_spd_with_census(sample_size=None)  # Process all records
        
        # Export results
        output_path = export_for_analysis(joined_data)
        
        # Show sample analysis
        sample_analysis(joined_data)
        
        print("\nSUCCESS! Your data is ready for analysis.")
        print(f"Output file: {output_path}")
        print("\nNext steps:")
        print("   1. Open the output CSV in Excel or Python")
        print("   2. Analyze crime patterns by demographics")
        print("   3. Create visualizations and maps")
        print("   4. Build predictive models")
        
        # Optional cleanup of downloaded files
        if cleanup_downloads:
            cleanup_downloaded_files()
        
    except FileNotFoundError as e:
        print(f"Error: Required file not found: {e}")
        print("Check that all required files exist and are accessible.")
    except pd.errors.EmptyDataError as e:
        print(f"Error: Data file is empty or corrupted: {e}")
        print("Re-run the download scripts to get fresh data.")
    except Exception as e:
        print(f"Error during join process: {e}")
        print("Check that all required files exist and are accessible.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Join SPD crime data with census demographics")
    parser.add_argument('--cleanup', action='store_true',
                       help='Delete downloaded files after successful join to save disk space')
    
    args = parser.parse_args()
    main(cleanup_downloads=args.cleanup)