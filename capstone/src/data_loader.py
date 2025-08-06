"""
Data loading utilities for CSV datasets.

This module provides simple functions for loading, preprocessing, and analyzing CSV datasets,
including data quality assessment and preparation for analysis.

Features:
- Simple CSV dataset loading
- Comprehensive data quality analysis
- Date column detection and conversion
- Coordinate column identification
- Data preparation and cleaning utilities

Author: Capstone Project
Date: July 2025
"""

# pylint: disable=invalid-name
from typing import Dict

import pandas as pd


# ============================================================================
# DATA LOADING AND ANALYSIS FUNCTIONS
# ============================================================================


def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Load a single CSV dataset.

    Args:
        file_path (str): Path to the CSV file

    Returns:
        pd.DataFrame: Loaded dataset

    Raises:
        FileNotFoundError: If file doesn't exist
        pd.errors.EmptyDataError: If file is empty
        pd.errors.ParserError: If file cannot be parsed as CSV

    Examples:
        # Load a specific CSV file
        df = load_dataset("data/SPD_Crime_Data.csv")
    """
    return pd.read_csv(file_path)


def analyze_data_quality(df: pd.DataFrame) -> Dict:
    """
    Perform comprehensive data quality analysis on any dataset.

    Args:
        df (pd.DataFrame): Dataset to analyze
        dataset_name (str): Name of the dataset for reporting

    Returns:
        Dict: Dictionary containing data quality metrics
    """
    # Basic metrics
    quality_report = {
        "shape": df.shape,
        "duplicates": df.duplicated().sum(),
        "missing_values": {},
        "data_types": df.dtypes.value_counts().to_dict(),
        "categorical_columns": {},
        "date_columns": [],
        "coordinate_columns": [],
    }

    # Missing values analysis
    missing_values = df.isnull().sum()
    missing_percent = (missing_values / len(df)) * 100
    quality_report["missing_values"] = {
        col: {"count": int(count), "percentage": round(percent, 2)}
        for col, count, percent in zip(
            missing_values.index, missing_values.values, missing_percent.values
        )
        if count > 0
    }

    # Categorical columns analysis
    categorical_cols = df.select_dtypes(include=["object"]).columns
    for col in categorical_cols:
        unique_count = df[col].nunique()
        quality_report["categorical_columns"][col] = {
            "unique_count": unique_count,
            "top_values": (
                df[col].value_counts().head(5).to_dict() if unique_count <= 100 else {}
            ),
        }

    # Identify special column types (more flexible detection)
    quality_report["date_columns"] = [
        col
        for col in df.columns
        if any(
            keyword in col.lower()
            for keyword in ["date", "time", "created", "updated", "timestamp"]
        )
    ]
    quality_report["coordinate_columns"] = [
        col
        for col in df.columns
        if any(
            coord in col.lower()
            for coord in ["lat", "lon", "x", "y", "coord", "longitude", "latitude"]
        )
    ]

    # Essential summary only
    print(f"Shape: {quality_report['shape']}")
    print(f"Duplicates: {quality_report['duplicates']:,}")
    print(f"Missing values: {len(quality_report['missing_values'])} columns affected")

    return quality_report


def load_spd_census_joined(file_path: str = "data/spd_census_joined.csv") -> pd.DataFrame:
    """
    Load the SPD crime data joined with census demographics.

    This function loads the enriched dataset that contains SPD crime incidents
    with census tract demographic information including population, income,
    race/ethnicity, and housing data.

    Args:
        file_path (str): Path to the joined CSV file

    Returns:
        pd.DataFrame: SPD crime data with census demographics

    Raises:
        FileNotFoundError: If file doesn't exist
        pd.errors.EmptyDataError: If file is empty
        pd.errors.ParserError: If file cannot be parsed as CSV

    Examples:
        # Load the joined dataset
        df = load_spd_census_joined()
        
        # Load from custom path
        df = load_spd_census_joined("data/custom_spd_census.csv")
    """
    df = pd.read_csv(file_path)
    
    # Convert date columns to datetime
    if 'Offense Date' in df.columns:
        df['Offense Date'] = pd.to_datetime(df['Offense Date'], errors='coerce')
    
    # Convert coordinate columns to numeric
    for coord_col in ['Latitude', 'Longitude']:
        if coord_col in df.columns:
            df[coord_col] = pd.to_numeric(df[coord_col], errors='coerce')
    
    print(f"[SUCCESS] Loaded SPD-Census joined dataset: {len(df):,} records")
    print(f"Records with census demographics: {df['TotalPopulation'].notna().sum():,}")
    print(f"Records with geographic coordinates: {df[['Latitude', 'Longitude']].notna().all(axis=1).sum():,}")
    
    return df


def prepare_data_for_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic preparation of any dataset for analysis.

    Args:
        df (pd.DataFrame): Raw dataset

    Returns:
        pd.DataFrame: Prepared dataset with cleaned dates and removed duplicates
    """
    prepared_df = df.copy()

    # Convert date columns to datetime (expanded detection)
    date_cols = [
        col
        for col in prepared_df.columns
        if any(
            keyword in col.lower()
            for keyword in ["date", "time", "created", "updated", "timestamp"]
        )
    ]

    for col in date_cols:
        try:
            prepared_df[col] = pd.to_datetime(prepared_df[col], errors="coerce")
        except (TypeError, ValueError):
            continue

    # Remove exact duplicates
    prepared_df = prepared_df.drop_duplicates()

    return prepared_df


if __name__ == "__main__":
    # Simple test when run directly
    print("Data Loader Library - Available Functions:")
    print("- load_dataset()")
    print("- load_spd_census_joined()")
    print("- analyze_data_quality()")
    print("- prepare_data_for_analysis()")
