# Seattle Crime & Census Data Pipeline

A data pipeline that downloads Seattle Police Department crime data and US Census demographics, then joins them spatially for analysis.

## Quick Start

```bash
# Run complete pipeline (downloads + joins data)
python main.py

# Skip downloads if data already exists
python main.py --skip-downloads

# Clean up downloaded files after joining (saves ~70MB)
python main.py --cleanup
```

## What This Pipeline Does

### 1. Downloads Crime Data
- **Source**: Seattle Police Department via Open Data Portal
- **Data**: ~1.47M crime records from 2008-present
- **File**: `SPD_Crime_Data__2008-Present_YYYYMMDD.csv` (296MB)
- **Location**: `data/downloads/seattle/`

### 2. Downloads Census Demographics  
- **Source**: US Census Bureau API (ACS 5-Year estimates)
- **Data**: King County demographics for years 2010-2023
- **Files**: Individual year files + combined dataset
- **Location**: `data/downloads/seattle/` (individual) + `data/joined/` (combined)

### 3. Downloads Census Boundaries
- **Source**: US Census TIGER/Line Shapefiles  
- **Data**: 2020 census tract boundaries for spatial matching
- **Location**: `data/downloads/seattle/census_shapefiles/`

### 4. Joins Data Spatially
- **Process**: Matches crime locations to census tracts using coordinates
- **Filtering**: Only includes crime records from 2015+ for better data quality
- **Output**: `spd_census_joined.csv` (~155MB, 726K records)
- **Location**: `data/joined/`

## Final Dataset

The joined dataset contains crime records with demographic information:

**Crime Columns**: Report Number, Date, Category, Address, Coordinates, Neighborhood, Beat
**Demographics**: Population, Income, Home Value, Race/Ethnicity breakdowns  
**Geography**: Census tract ID, tract name, shapefile boundaries

## Data Dictionary

### `spd_census_joined.csv` - Final Joined Dataset (40 columns, ~900K records)

#### Crime Data (from Seattle Police Department)
| Column | Type | Description |
|--------|------|-------------|
| `Report Number` | String | SPD internal report identifier |
| `Report DateTime` | DateTime | When the crime was reported to police |
| `Offense ID` | String | **Unique identifier** for each offense (primary key) |
| `Offense Date` | DateTime | When the crime actually occurred |
| `NIBRS Group AB` | String | FBI crime classification (Group A/B) |
| `NIBRS Crime Against Category` | String | Crime target (Person, Property, Society) |
| `Offense Sub Category` | String | Detailed crime subcategory |
| `Shooting Type Group` | String | Shooting-related classification (if applicable) |
| `Block Address` | String | Approximate street address (privacy protected) |
| `Latitude` | Float | Geographic latitude (WGS84) |
| `Longitude` | Float | Geographic longitude (WGS84) |
| `Beat` | String | SPD patrol beat identifier |
| `Precinct` | String | SPD precinct (North, South, East, West, Southwest) |
| `Sector` | String | SPD sector within precinct |
| `Neighborhood` | String | Seattle neighborhood name |
| `Reporting Area` | String | SPD reporting area code |
| `Offense Category` | String | High-level crime category (Violent, Property, Other) |
| `NIBRS Offense Code Description` | String | Detailed FBI offense description |
| `NIBRS_offense_code` | String | FBI NIBRS offense code |
| `crime_year` | Integer | Year when crime occurred (extracted from Offense Date) |

#### Geographic Linkage
| Column | Type | Description |
|--------|------|-------------|
| `tract_geoid` | String | Census tract GEOID for spatial matching |
| `NAME` | String | Census tract name/description |
| `state` | String | State code (53 for Washington) |
| `county` | String | County code (033 for King County) |
| `tract` | String | Census tract code |
| `GEOID` | String | Full 11-digit census tract identifier |

#### Demographics (from US Census Bureau ACS 5-Year Estimates)
| Column | Type | Description |
|--------|------|-------------|
| `TotalPopulation` | Integer | Total population in census tract |
| `MedianHouseholdIncome` | Integer | Median household income (dollars) |
| `MedianHomeValue` | Integer | Median home value (dollars) |
| `TotalRaceEthnicityPop` | Integer | Total population for race/ethnicity data |
| `NotHispanicLatino` | Integer | Non-Hispanic/Latino population |
| `WhiteAlone` | Integer | White alone population |
| `BlackAfricanAmericanAlone` | Integer | Black or African American alone |
| `AmericanIndianAlaskaNativeAlone` | Integer | American Indian and Alaska Native alone |
| `AsianAlone` | Integer | Asian alone population |
| `NativeHawaiianPacificIslanderAlone` | Integer | Native Hawaiian and Pacific Islander alone |
| `SomeOtherRaceAlone` | Integer | Some other race alone |
| `TwoOrMoreRaces` | Integer | Two or more races population |
| `HispanicLatino` | Integer | Hispanic or Latino population |
| `census_year` | Integer | Year of census data (2010-2023, matched to crime year) |

#### Data Quality Notes
- **Coverage**: 899,227 crime records from 2015-2024 (filtered for data quality)
- **Spatial Match Rate**: ~80.8% of crimes successfully matched to census tracts
- **Missing Values**: Records without valid coordinates or census matches preserved with NULL demographic values
- **Temporal Matching**: Crime years mapped to nearest available census year for demographic consistency
- **Unique Identifier**: Use `Offense ID` for deduplication (not `Report Number` which can have duplicates)

## Requirements

```bash
pip install -r requirements.txt
```

Set Census API key (free at https://api.census.gov/data/key_signup.html):
```bash
export CENSUS_API_KEY="your_key_here"
```

## File Structure

```
datasets/
├── main.py                     # Pipeline runner
├── src/
│   ├── download_spd_crime.py   # Downloads SPD crime data
│   ├── download_seattle_census.py  # Downloads census data
│   └── join_spd_census.py      # Spatial join processing
└── data/
    ├── downloads/seattle/      # Raw data (ignored by git)
    └── joined/                 # Final datasets (tracked with Git LFS)
```
