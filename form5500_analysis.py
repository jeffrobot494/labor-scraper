#!/usr/bin/env python3
"""
Form 5500 Data Analysis

This script downloads, extracts, and analyzes Form 5500 datasets
from the Department of Labor, focusing on finding matches for a specific sponsor.
"""

import os
import requests
import zipfile
import pandas as pd
from rapidfuzz import fuzz, process
import argparse

def download_file(url, output_path):
    """
    Download a file from URL to the specified output path
    
    Args:
        url (str): URL to download from
        output_path (str): Path where the file will be saved
    
    Returns:
        bool: True if download was successful, False otherwise
    """
    print(f"Downloading file from {url}...")
    
    try:
        # Stream the download to handle large files
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            
            # Get total file size for progress reporting
            total_size = int(response.headers.get('content-length', 0))
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write the file in chunks
            with open(output_path, 'wb') as f:
                downloaded = 0
                chunk_size = 8192  # 8KB chunks
                
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Print progress
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"Download progress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='\r')
            
            print("\nDownload completed successfully!")
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return False

def extract_zip(zip_path, extract_to_folder):
    """
    Extract a ZIP file to the specified folder
    
    Args:
        zip_path (str): Path to the ZIP file
        extract_to_folder (str): Folder to extract contents to
    
    Returns:
        list: List of extracted file paths
    """
    print(f"Extracting ZIP file: {zip_path}...")
    
    try:
        # Create extraction directory if it doesn't exist
        os.makedirs(extract_to_folder, exist_ok=True)
        
        extracted_files = []
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get list of files in the ZIP
            file_list = zip_ref.namelist()
            print(f"ZIP contains {len(file_list)} files")
            
            # Extract all files
            for file in file_list:
                print(f"Extracting: {file}")
                zip_ref.extract(file, extract_to_folder)
                extracted_files.append(os.path.join(extract_to_folder, file))
        
        print("Extraction completed successfully!")
        return extracted_files
        
    except zipfile.BadZipFile as e:
        print(f"Error: The file is not a valid ZIP file: {e}")
        return []
    except Exception as e:
        print(f"Error extracting ZIP file: {e}")
        return []

def find_matching_rows(csv_path, target_name, similarity_threshold=80):
    """
    Find rows in the CSV where sponsor name matches the target name using fuzzy matching
    
    Args:
        csv_path (str): Path to the CSV file
        target_name (str): Name to match against sponsor names
        similarity_threshold (int): Minimum similarity score (0-100) to consider a match
    
    Returns:
        DataFrame: Filtered dataframe containing matching rows
    """
    print(f"Processing CSV file: {csv_path}")
    print(f"Searching for sponsor names similar to: {target_name}")
    
    try:
        # Load the CSV file with appropriate settings for large files
        print("Loading CSV data (this may take a while for large files)...")
        df = pd.read_csv(csv_path, low_memory=False)
        
        print(f"Loaded {len(df)} rows. Starting fuzzy matching...")
        
        # Function to calculate similarity score for each sponsor name
        def calculate_similarity(name):
            if pd.isna(name):
                return 0
            return fuzz.ratio(name.upper(), target_name.upper())
        
        # Add a similarity score column
        df['similarity_score'] = df['SPONSOR_DFE_NAME'].apply(calculate_similarity)
        
        # Filter rows based on similarity threshold
        matches = df[df['similarity_score'] >= similarity_threshold]
        
        print(f"Found {len(matches)} matches with similarity ≥ {similarity_threshold}%")
        return matches
        
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return pd.DataFrame()

def main(zip_url=None, target_sponsor=None):
    """
    Main function to orchestrate the download, extraction, and analysis process
    
    Args:
        zip_url (str, optional): URL of the Form 5500 dataset ZIP file.
                                Defaults to 2023 dataset if not provided.
        target_sponsor (str, optional): Name of the sponsor to search for.
                                       Defaults to THE INTERSECT GROUP if not provided.
    """
    # Set default values if parameters not provided
    if zip_url is None:
        zip_url = "https://askebsa.dol.gov/FOIA%20Files/2023/Latest/F_5500_2023_Latest.zip"
    
    if target_sponsor is None:
        target_sponsor = "THE INTERSECT GROUP"
    
    # Define file paths
    data_dir = "data"
    
    # Extract filename from URL for the local save path
    filename = os.path.basename(zip_url)
    zip_path = os.path.join(data_dir, filename)
    extract_folder = os.path.join(data_dir, "extracted", filename.replace(".zip", ""))
    
    print(f"Starting Form 5500 data analysis")
    print(f"Target sponsor: {target_sponsor}")
    print(f"Dataset URL: {zip_url}")
    
    # Step 1: Download the ZIP file if it doesn't already exist
    if not os.path.exists(zip_path):
        if not download_file(zip_url, zip_path):
            print("Failed to download the ZIP file. Exiting.")
            return
    else:
        print(f"ZIP file already exists at {zip_path}, skipping download")
    
    # Step 2: Extract the ZIP file
    extracted_files = extract_zip(zip_path, extract_folder)
    if not extracted_files:
        print("Failed to extract any files from the ZIP. Exiting.")
        return
    
    # Find the CSV file in the extracted files
    csv_files = [f for f in extracted_files if f.lower().endswith('.csv')]
    if not csv_files:
        print("No CSV files found in the extracted ZIP. Exiting.")
        return
    
    csv_path = csv_files[0]  # Use the first CSV file
    print(f"Using CSV file: {csv_path}")
    
    # Step 3: Find matching rows in the CSV
    matches = find_matching_rows(csv_path, target_sponsor)
    
    # Step 4: Display the results
    if len(matches) > 0:
        print("\nMatching sponsor entries:")
        for index, row in matches.iterrows():
            print("\n" + "="*50)
            print(f"Sponsor Name: {row.get('SPONSOR_DFE_NAME', 'N/A')}")
            print(f"Filing ID: {row.get('ACK_ID', 'N/A')}")
            print(f"EIN: {row.get('EIN', 'N/A')}")
            print(f"Plan Year: {row.get('PLAN_YEAR', 'N/A')}")
            print(f"Similarity Score: {row.get('similarity_score', 'N/A')}%")
    else:
        print("\nNo matching sponsors found.")
    
    print("\nAnalysis completed.")

if __name__ == "__main__":
    # Create command line argument parser
    parser = argparse.ArgumentParser(description="Form 5500 Dataset Analysis Tool")
    parser.add_argument("--url", type=str, help="URL to the Form 5500 dataset ZIP file")
    parser.add_argument("--sponsor", type=str, help="Target sponsor name to search for")
    parser.add_argument("--threshold", type=int, default=80, 
                        help="Minimum similarity threshold (0-100) for name matching (default: 80)")
    
    # Parse command line arguments
    args = parser.parse_args()
    
    # Call main function with command line arguments
    main(zip_url=args.url, target_sponsor=args.sponsor)