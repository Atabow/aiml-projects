#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
US Census Data Downloader for King County

This module downloads demographic data from the US Census Bureau API
for King County census tracts and related shapefiles.
"""

import os
import urllib.request
import urllib.error
import zipfile
from pathlib import Path

import pandas as pd
from census import Census
from us import states

# Your Census API Key
CENSUS_API_KEY = os.getenv('CENSUS_API_KEY')
if not CENSUS_API_KEY:
    raise ValueError("Census API key not found. Please set the CENSUS_API_KEY environment variable")

census_client = Census(CENSUS_API_KEY)

def get_census_data_dir() -> Path:
    """Get the directory path for storing census data."""
    # Get the project root directory (assuming this file is in data_src/)
    project_root = Path(__file__).parent.parent
    data_directory = project_root / "data" / "downloads" / "seattle"
    
    # Create directory if it doesn't exist
    data_directory.mkdir(parents=True, exist_ok=True)
    
    return data_directory

def save_census_data(dataframe: pd.DataFrame, data_year: int) -> str:
    """
    Save census data to a CSV file.
    
    Args:
        dataframe: DataFrame containing census data
        data_year: Year of the data
        
    Returns:
        Path to the saved file
    """
    if dataframe.empty:
        return ""
    
    data_directory = get_census_data_dir()
    filename = f"king_county_census_{data_year}.csv"
    filepath = data_directory / filename
    
    # Save to CSV
    dataframe.to_csv(filepath, index=False)
    print(f"Saved {len(dataframe)} records to: {filepath}")
    
    return str(filepath)

def download_tract_shapefiles(shapefile_year: int = 2020) -> str:
    """
    Download Census tract shapefiles for Washington state.
    
    Args:
        shapefile_year: Year for the shapefiles (default 2020)
        
    Returns:
        Path to the extracted shapefile directory
    """
    data_directory = get_census_data_dir()
    shp_directory = data_directory / "census_shapefiles" / str(shapefile_year)
    shp_directory.mkdir(parents=True, exist_ok=True)
    
    # Census Bureau FTP URL for tract shapefiles
    base_url = f"https://www2.census.gov/geo/tiger/TIGER{shapefile_year}/TRACT/"
    filename = f"tl_{shapefile_year}_53_tract.zip"  # 53 is Washington state FIPS
    zip_url = base_url + filename
    zip_path = shp_directory / filename
    
    print(f"Downloading tract shapefiles for {shapefile_year}...")
    
    try:
        # Download the shapefile zip
        if not zip_path.exists():
            urllib.request.urlretrieve(zip_url, zip_path)
            print(f"Downloaded: {zip_path}")
        else:
            print(f"Shapefile already exists: {zip_path}")
        
        # Extract the zip file
        extract_dir = shp_directory / "extracted"
        extract_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        print(f"Extracted shapefiles to: {extract_dir}")
        
        # List the extracted files
        extracted_files = list(extract_dir.glob("*"))
        print(f"Extracted files: {[f.name for f in extracted_files]}")
        
        return str(extract_dir)
        
    except (urllib.error.URLError, zipfile.BadZipFile, OSError) as e:
        print(f"Error downloading shapefiles: {e}")
        return ""

# FIPS codes for King County, WA
# Using hardcoded values since us.counties lookup can be unreliable
state_fips = states.WA.fips  # '53'
county_fips = '033'  # King County FIPS code

# List of years for which you want data (e.g., for 2010 crime data, you'd want 2010 estimates)
# If you want 2015 onwards, list them here:
years_to_fetch = [2010, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023] # 2023 is for 2019-2023 ACS 5-Year

# Dictionary to store dataframes for each year
all_demographics = {}

# Define the variables you need. These are widely available across years.
# 'NAME' is always good to include for the geographic name.
census_variables = (
    "NAME",
    "B01003_001E",  # Total Population
    "B19013_001E",  # Median Household Income
    "B25077_001E",  # Median Home Value
    # Race and Ethnicity (B03002 - Hispanic or Latino Origin by Race)
    "B03002_001E",  # Total Population (Race/Ethnicity universe)
    "B03002_002E",  # Not Hispanic or Latino
    "B03002_003E",  # Not Hispanic or Latino: White alone
    "B03002_004E",  # Not Hispanic or Latino: Black or African American alone
    "B03002_005E",  # Not Hispanic or Latino: American Indian and Alaska Native alone
    "B03002_006E",  # Not Hispanic or Latino: Asian alone
    "B03002_007E",  # Not Hispanic or Latino: Native Hawaiian and Other Pacific Islander alone
    "B03002_008E",  # Not Hispanic or Latino: Some other race alone
    "B03002_009E",  # Not Hispanic or Latino: Two or more races
    "B03002_012E",  # Hispanic or Latino
)

for year in years_to_fetch:
    print(f"Fetching ACS 5-Year data for year ending {year}...")
    try:
        # The .acs5.get method is correct for ACS 5-Year Detailed Tables
        data = census_client.acs5.get(
            census_variables,
            {"for": "tract:*", "in": f'state:{state_fips} county:{county_fips}'},
            year=year,
        )
        df = pd.DataFrame(data)

        # Clean GEOID for merging
        # The 'GEO_ID' column in the data from the API will usually be like '1400000US53033000100'
        df['GEOID'] = df['tract'] + df['county'] + df['state'] # Construct GEOID from components
        # Or more reliably, if 'GEO_ID' is returned:
        # df['GEOID'] = df['GEO_ID'].str.replace('1400000US', '') # This might not be present from API directly

        # Rename variables for clarity
        df.rename(columns={
            "B01003_001E": "TotalPopulation",
            "B19013_001E": "MedianHouseholdIncome",
            "B25077_001E": "MedianHomeValue",
            # Race and Ethnicity columns
            "B03002_001E": "TotalRaceEthnicityPop",
            "B03002_002E": "NotHispanicLatino",
            "B03002_003E": "WhiteAlone",
            "B03002_004E": "BlackAfricanAmericanAlone",
            "B03002_005E": "AmericanIndianAlaskaNativeAlone", 
            "B03002_006E": "AsianAlone",
            "B03002_007E": "NativeHawaiianPacificIslanderAlone",
            "B03002_008E": "SomeOtherRaceAlone",
            "B03002_009E": "TwoOrMoreRaces",
            "B03002_012E": "HispanicLatino",
        }, inplace=True)

        # Add the 'year' to the DataFrame for identification
        df['year'] = year
        
        # Save data locally to seattle folder (raw data)
        save_census_data(df, year)
        
        all_demographics[year] = df
        print(f"Successfully fetched {len(df)} records for {year}.")

    except (ValueError, ConnectionError, KeyError) as e:
        print(f"Error fetching data for year {year}: {e}")
        # Consider adding a time.sleep(1) here if you hit rate limits

# Concatenate all dataframes into one and save to joined folder
if all_demographics:
    df_all_demographics = pd.concat(all_demographics.values(), ignore_index=True)
    
    # Save the combined dataset to the joined folder (processed data)
    project_root = Path(__file__).parent.parent
    joined_dir = project_root / "data" / "joined"
    joined_dir.mkdir(parents=True, exist_ok=True)
    
    combined_filepath = joined_dir / "king_county_census_combined.csv"
    df_all_demographics.to_csv(combined_filepath, index=False)
    print(f"Saved combined dataset to: {combined_filepath}")
    
    print("\nCombined Demographics Data Head:")
    print(df_all_demographics.head())
    print(f"Total combined records: {len(df_all_demographics)}")
    
    # Keep individual year files - they are preserved for reference in seattle folder
    print("\nIndividual year files preserved in seattle folder:")
    raw_data_dir = get_census_data_dir()  # This is the seattle folder
    for year in years_to_fetch:
        year_file = raw_data_dir / f"king_county_census_{year}.csv"
        if year_file.exists():
            file_size = round(year_file.stat().st_size / 1024, 1)  # Size in KB
            print(f"  Kept: {year_file.name} ({file_size} KB)")
    
    print("All individual year files have been preserved for reference.")
    
    # Show where files are stored
    print(f"\nRaw census data files stored in: {get_census_data_dir()}")
    print(f"Combined census data stored in: {joined_dir}")
    
    # Download tract shapefiles for geographic data (raw data in seattle folder)
    print("\nDownloading tract shapefiles...")
    shapefile_dir = download_tract_shapefiles(2020)  # Use 2020 shapefiles as they're most current
    if shapefile_dir:
        print(f"Shapefiles available at: {shapefile_dir}")
    
else:
    print("No demographic data was fetched.")
