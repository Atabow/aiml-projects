#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seattle Police Department Crime Data Downloader

This module downloads the latest SPD crime data from the Seattle Open Data portal.
The dataset contains crime incident reports from 2008 to present.

Data Source: https://data.seattle.gov/Public-Safety/SPD-Crime-Data-2008-Present/tazs-3rd5
"""

import logging
import os
import sys
from datetime import datetime

import pandas as pd
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spd_download.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class SPDCrimeDownloader:
    """
    Downloads Seattle Police Department crime data from the City of Seattle Open Data portal.
    """

    def __init__(self, base_dir=None):
        """
        Initialize the downloader.

        Args:
            base_dir (str): Base directory for the project. If None, uses parent of current script location.
        """
        if base_dir is None:
            # Get the parent directory of the current script (assumes script is in src/)
            self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.base_dir = base_dir

        self.data_dir = os.path.join(self.base_dir, "data", "downloads", "seattle")

        # Seattle Open Data API endpoints
        self.base_url = "https://data.seattle.gov"

        # SPD Crime Data resource ID from Seattle Open Data
        # This is the dataset: "SPD Crime Data: 2008-Present"
        self.resource_id = "tazs-3rd5"

        # API endpoint for CSV download
        self.csv_url = f"{self.base_url}/api/views/{self.resource_id}/rows.csv?accessType=DOWNLOAD"

        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)

    def get_dataset_info(self):
        """
        Get information about the dataset from the API.

        Returns:
            dict: Dataset metadata
        """
        try:
            metadata_url = f"{self.base_url}/api/views/{self.resource_id}.json"
            response = requests.get(metadata_url, timeout=30)
            response.raise_for_status()

            metadata = response.json()

            info = {
                'name': metadata.get('name', 'Unknown'),
                'description': metadata.get('description', 'No description available'),
                'rows_updated_at': metadata.get('rowsUpdatedAt', 'Unknown'),
                'creation_date': metadata.get('createdAt', 'Unknown'),
                'row_count': metadata.get('totalCount', 'Unknown'),
                'columns': len(metadata.get('columns', [])),
                'tags': metadata.get('tags', [])
            }

            return info

        except requests.RequestException as e:
            logging.error("Failed to get dataset information: %s", e)
            return None

    def download_dataset(self, filename=None, chunk_size=8192):
        """
        Download the SPD crime dataset.

        Args:
            filename (str): Optional custom filename. If None, generates timestamp-based name.
            chunk_size (int): Size of chunks to download in bytes.

        Returns:
            str: Path to downloaded file, or None if download failed.
        """
        try:
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d")
                filename = f"SPD_Crime_Data__2008-Present_{timestamp}.csv"

            filepath = os.path.join(self.data_dir, filename)

            logging.info("Starting download of SPD Crime Data...")
            logging.info("URL: %s", self.csv_url)
            logging.info("Destination: %s", filepath)

            # Make the request with streaming enabled
            response = requests.get(self.csv_url, stream=True, timeout=60)
            response.raise_for_status()

            # Get the total file size if available
            total_size = int(response.headers.get('content-length', 0))

            # Download the file in chunks
            downloaded_size = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        # Show progress
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            logging.info("Download progress: %.1f%% (%s / %s bytes)",
                                       progress, f"{downloaded_size:,}", f"{total_size:,}")
                        else:
                            logging.info("Downloaded: %s bytes", f"{downloaded_size:,}")

            logging.info("Download completed successfully!")
            logging.info("File saved to: %s", filepath)
            logging.info("Final size: %s bytes", f"{downloaded_size:,}")

            return filepath

        except requests.RequestException as e:
            logging.error("Network error during download: %s", e)
            return None
        except IOError as e:
            logging.error("File system error during download: %s", e)
            return None
        except (ValueError, TypeError) as e:
            logging.error("Data processing error during download: %s", e)
            return None

    def validate_dataset(self, filepath):
        """
        Perform basic validation on the downloaded dataset.

        Args:
            filepath (str): Path to the downloaded CSV file.

        Returns:
            dict: Validation results
        """
        try:
            logging.info("Validating downloaded dataset...")

            # Check file exists and get size
            if not os.path.exists(filepath):
                return {'valid': False, 'error': 'File does not exist'}

            file_size = os.path.getsize(filepath)

            # Try to read the first few rows to validate CSV format
            df_sample = pd.read_csv(filepath, nrows=100)

            validation_results = {
                'valid': True,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'sample_rows': len(df_sample),
                'columns': list(df_sample.columns),
                'column_count': len(df_sample.columns)
            }

            logging.info("Validation successful!")
            logging.info("File size: %s MB", validation_results['file_size_mb'])
            logging.info("Columns found: %s", validation_results['column_count'])
            logging.info("Sample column names: %s...", validation_results['columns'][:5])

            return validation_results

        except (IOError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
            logging.error("Validation failed: %s", e)
            return {'valid': False, 'error': str(e)}

    def get_data_summary(self, filepath, sample_size=1000):
        """
        Get a summary of the downloaded data.

        Args:
            filepath (str): Path to the CSV file.
            sample_size (int): Number of rows to sample for summary.

        Returns:
            dict: Data summary
        """
        try:
            logging.info("Generating data summary (sampling %s rows)...", sample_size)

            # Read a sample of the data
            df = pd.read_csv(filepath, nrows=sample_size)

            summary = {
                'sample_size': len(df),
                'columns': list(df.columns),
                'dtypes': df.dtypes.to_dict(),
                'null_counts': df.isnull().sum().to_dict(),
                'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
            }

            # Add some basic statistics for key columns if they exist
            if 'Offense Start DateTime' in df.columns:
                try:
                    df['Offense Start DateTime'] = pd.to_datetime(df['Offense Start DateTime'])
                    summary['date_range'] = {
                        'earliest': str(df['Offense Start DateTime'].min()),
                        'latest': str(df['Offense Start DateTime'].max())
                    }
                except (ValueError, pd.errors.OutOfBoundsDatetime):
                    pass

            if 'Primary Offense Description' in df.columns:
                summary['top_offenses'] = df['Primary Offense Description'].value_counts().head(10).to_dict()

            return summary

        except (IOError, pd.errors.EmptyDataError, pd.errors.ParserError, MemoryError) as e:
            logging.error("Failed to generate data summary: %s", str(e))
            return None


def main():
    """
    Main function to download and validate SPD crime data.
    """
    logging.info("Starting SPD Crime Data Download Process")

    # Initialize downloader
    downloader = SPDCrimeDownloader()

    # Get dataset information
    logging.info("Fetching dataset information...")
    dataset_info = downloader.get_dataset_info()

    if dataset_info:
        logging.info("Dataset: %s", dataset_info['name'])
        logging.info("Description: %s...", dataset_info['description'][:200])
        logging.info("Last updated: %s", dataset_info['rows_updated_at'])
        logging.info("Estimated rows: %s", dataset_info['row_count'])
    else:
        logging.warning("Could not fetch dataset information, proceeding with download...")

    # Download the dataset
    filepath = downloader.download_dataset()

    if filepath:
        # Validate the download
        validation = downloader.validate_dataset(filepath)

        if validation['valid']:
            logging.info("Dataset validation passed!")

            # Generate summary
            summary = downloader.get_data_summary(filepath)
            if summary:
                logging.info("Data summary generated successfully")
                logging.info("Sampled %s rows", summary['sample_size'])
                if 'date_range' in summary:
                    logging.info("Date range: %s to %s",
                               summary['date_range']['earliest'], summary['date_range']['latest'])
        else:
            logging.error("Dataset validation failed: %s", validation.get('error', 'Unknown error'))

    else:
        logging.error("Dataset download failed!")
        sys.exit(1)

    logging.info("SPD Crime Data Download Process Completed")


if __name__ == "__main__":
    main()
