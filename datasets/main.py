#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seattle Crime & Census Data Pipeline
====================================

This script runs the complete data pipeline to download, process, and join
Seattle Police Department crime data with US Census demographic data.

Pipeline Steps:
1. Download SPD crime data from Seattle Open Data Portal
2. Download US Census demographic data for King County
3. Join crime data with census data using spatial analysis
4. Generate final dataset for analysis

Usage:
    python main.py [--skip-downloads]
    
Arguments:
    --skip-downloads: Skip download steps if data already exists
"""

import sys
import subprocess
import argparse
from pathlib import Path
import time

def print_banner(title):
    """Print a formatted banner for each pipeline step."""
    print("\n" + "="*80)
    print(f">> {title}")
    print("="*80)

def run_script(script_path, description):
    """Run a Python script and handle errors."""
    print(f"\n=> Running: {description}")
    print(f"   Script: {script_path}")
    
    start_time = time.time()
    
    try:
        # Split script path and arguments if present
        script_parts = script_path.split()
        script_file = script_parts[0]
        script_args = script_parts[1:] if len(script_parts) > 1 else []
        
        # Run the script using subprocess
        cmd = [sys.executable, script_file] + script_args
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd(), check=False)
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"SUCCESS! Completed in {elapsed_time:.1f} seconds")
            if result.stdout:
                # Show key output lines
                output_lines = result.stdout.strip().split('\n')
                important_lines = [line for line in output_lines if any(
                    keyword in line for keyword in ['SUCCESS', 'Downloaded', 'Saved', 'Total', 'Loaded', 'Exported']
                )]
                if important_lines:
                    print("Key Results:")
                    for line in important_lines[-5:]:  # Show last 5 important lines
                        print(f"   {line}")
            return True
        else:
            print(f"FAILED! Error code: {result.returncode}")
            print("Error details:")
            if result.stderr:
                for line in result.stderr.strip().split('\n')[-10:]:  # Show last 10 error lines
                    print(f"   {line}")
            return False
            
    except subprocess.SubprocessError as e:
        print(f"FAILED! Exception: {e}")
        return False

def check_file_exists(file_path, description):
    """Check if a required file exists."""
    if Path(file_path).exists():
        file_size = Path(file_path).stat().st_size / (1024*1024)  # MB
        print(f"FOUND: {description} ({file_size:.1f} MB)")
        return True
    else:
        print(f"MISSING: {description}")
        return False

def main():
    """Main pipeline execution function."""
    parser = argparse.ArgumentParser(description="Seattle Crime & Census Data Pipeline")
    parser.add_argument('--skip-downloads', action='store_true',
                       help='Skip download steps if data already exists')
    parser.add_argument('--cleanup', action='store_true',
                       help='Delete downloaded files after successful join to save disk space')
    
    args = parser.parse_args()
    
    print_banner("SEATTLE CRIME & CENSUS DATA PIPELINE")
    print("Purpose: Download and join SPD crime data with census demographics")
    print("Output: Complete dataset ready for analysis and modeling")
    
    if args.skip_downloads:
        print("SKIP MODE: Will skip downloads if data exists")
    
    if args.cleanup:
        print("CLEANUP MODE: Will delete downloaded files after successful join")
    
    # Define pipeline steps
    pipeline_steps = []
    
    # Step 1: Download SPD Crime Data
    spd_file = "data/downloads/seattle/SPD_Crime_Data__2008-Present_20250727.csv"
    if args.skip_downloads and check_file_exists(spd_file, "SPD Crime Data"):
        print("=> Skipping SPD crime data download - file exists")
    else:
        pipeline_steps.append({
            'script': 'src/download_spd_crime.py',
            'title': 'Download SPD Crime Data',
            'description': 'Downloading Seattle Police Department crime data from city portal'
        })
    
    # Step 2: Download Census Data
    census_file = "data/joined/king_county_census_combined.csv"
    if args.skip_downloads and check_file_exists(census_file, "Census Combined Data"):
        print("=> Skipping census data download - file exists")
    else:
        pipeline_steps.append({
            'script': 'src/download_seattle_census.py',
            'title': 'Download Census Demographics',
            'description': 'Downloading US Census demographic data for King County'
        })
    
    # Step 3: Join Data
    join_script = 'src/join_spd_census.py'
    if args.cleanup:
        join_script += ' --cleanup'
    
    pipeline_steps.append({
        'script': join_script,
        'title': 'Join Crime & Census Data',
        'description': 'Performing spatial join of crime locations with census demographics'
    })
    
    # Execute pipeline
    print(f"\nPipeline has {len(pipeline_steps)} steps to execute")
    
    total_start_time = time.time()
    failed_steps = []
    
    for i, step in enumerate(pipeline_steps, 1):
        print_banner(f"STEP {i}/{len(pipeline_steps)}: {step['title']}")
        
        success = run_script(step['script'], step['description'])
        
        if not success:
            failed_steps.append(step['title'])
            print(f"\nStep {i} failed, but continuing with pipeline...")
    
    # Final results
    total_elapsed = time.time() - total_start_time
    
    print_banner("PIPELINE SUMMARY")
    
    if not failed_steps:
        print("SUCCESS! All pipeline steps completed successfully!")
    else:
        print(f"Pipeline completed with {len(failed_steps)} failed steps:")
        for step in failed_steps:
            print(f"   FAILED: {step}")
    
    print(f"Total execution time: {total_elapsed/60:.1f} minutes")
    
    # Check final outputs
    print("\nFinal Output Files:")
    output_files = [
        ("data/downloads/seattle/SPD_Crime_Data__2008-Present_20250727.csv", "SPD Crime Data"),
        ("data/joined/king_county_census_combined.csv", "Combined Census Data"),
        ("data/joined/spd_census_joined.csv", "Final Joined Dataset"),
    ]
    
    all_outputs_exist = True
    for file_path, description in output_files:
        if not check_file_exists(file_path, description):
            all_outputs_exist = False
    
    if all_outputs_exist:
        print("\nREADY FOR ANALYSIS!")
        print("Next steps:")
        print("   1. Load data/joined/spd_census_joined.csv in Python/R")
        print("   2. Explore crime patterns by demographics")
        print("   3. Create maps and visualizations")
        print("   4. Build predictive models")
        print("   5. Generate insights and reports")
    else:
        print("\nSome output files are missing. Check the logs above for errors.")

if __name__ == "__main__":
    main()
