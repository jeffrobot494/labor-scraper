#!/usr/bin/env python3
"""
EFAST2 Form 5500 Scraper

Automates the download of Form 5500 filing ZIP files from the DOL EFAST2 5500 Search portal
using Selenium WebDriver.
"""

import os
import time
import zipfile
import argparse
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_browser(download_dir):
    """
    Set up Chrome browser with appropriate options for automated downloading
    
    Args:
        download_dir (str): Directory to save downloaded files
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """
    # Create download directory if it doesn't exist
    download_path = os.path.abspath(download_dir)
    os.makedirs(download_path, exist_ok=True)
    
    print(f"Setting up Chrome browser with download directory: {download_path}")
    
    # Configure Chrome options
    options = Options()
    #options.add_argument('--headless=new')  # Use 'new' headless mode for Chrome 109+
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Enable file downloads in headless mode
    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    
    # Create and return Chrome driver
    driver = webdriver.Chrome(options=options)
    
    # Set implicit wait time
    driver.implicitly_wait(10)
    
    return driver

def search_and_download_filing(driver, filing_id, max_retries=3):
    """
    Navigate to EFAST2 search portal, search for filing ID, and download ZIP
    
    Args:
        driver (webdriver.Chrome): Configured Chrome WebDriver instance
        filing_id (str): Filing ID (ACK_ID) to search for
        max_retries (int): Maximum number of retry attempts
    
    Returns:
        bool: True if download appears successful, False otherwise
    """
    # URL for DOL EFAST2 5500 Search portal
    efast2_url = "https://www.efast.dol.gov/5500Search/"
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt}/{max_retries} - Navigating to EFAST2 search portal...")
            driver.get(efast2_url)
            
            # Wait for page to load by checking for the presence of the search form
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "categoryType"))
            )
            
            print("Page loaded. Looking for popup close button...")
            
            # Look for and click the close button by its ID
            try:
                # Wait for the close button to be clickable
                close_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "button.closeXBtn"))
                )
                
                print("Found close button. Clicking to dismiss popup...")
                close_button.click()
                
                # Short pause to let the UI stabilize after closing popup
                time.sleep(1)
            except TimeoutException:
                print("No popup close button found or it wasn't clickable. Continuing...")
            except Exception as e:
                print(f"Error handling popup: {e}")
            
            print("Setting search criteria...")
            
            # Find and change the dropdown from default "Plan Name" to "ACK ID"
            category_dropdown = Select(driver.find_element(By.ID, "categoryType"))
            category_dropdown.select_by_visible_text("ACK ID")
            
            # Add a small delay after changing dropdown to let page update
            time.sleep(1)
            
            # Find the search input box using the correct ID and enter the filing ID
            try:
                # First try with the ID provided
                search_input = driver.find_element(By.ID, "search-field")
                print("Found search input with ID 'search-field'")
            except NoSuchElementException:
                # If that fails, try to find by other attributes or show all input fields for debugging
                print("Search field with ID 'search-field' not found. Looking for alternatives...")
                
                # Print all input elements on the page for debugging
                input_elements = driver.find_elements(By.TAG_NAME, "input")
                print(f"Found {len(input_elements)} input elements on the page:")
                for i, element in enumerate(input_elements):
                    element_id = element.get_attribute("id")
                    element_name = element.get_attribute("name")
                    element_type = element.get_attribute("type")
                    placeholder = element.get_attribute("placeholder")
                    print(f"  Input #{i+1} - ID: '{element_id}', Name: '{element_name}', Type: '{element_type}', Placeholder: '{placeholder}'")
                
                # Try to find by placeholder or other attributes commonly used for search fields
                try:
                    search_input = driver.find_element(By.XPATH, "//input[@type='text' and (@placeholder contains 'search' or @placeholder contains 'Search')]")
                    print("Found search input by placeholder text")
                except NoSuchElementException:
                    # If all else fails, just use the first visible text input
                    for input_element in input_elements:
                        if input_element.get_attribute("type") == "text" and input_element.is_displayed():
                            search_input = input_element
                            print(f"Using first visible text input: ID='{input_element.get_attribute('id')}'")
                            break
                    else:
                        raise Exception("Could not find any suitable search input field")
            
            # Clear and enter the filing ID
            search_input.clear()
            search_input.send_keys(filing_id)
            print(f"Filing ID entered in search field: {filing_id}")
            
            # Verify that the text was entered correctly
            entered_value = search_input.get_attribute("value")
            print(f"Verified text in search field: '{entered_value}'")
            
            # Click the Search button to submit the search
            search_button = driver.find_element(By.ID, "searchButton")
            search_button.click()
            
            # Wait for search results to appear
            print("Waiting for search results...")
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-table"))
            )
            
            # Look for the specific filing ID in the results table
            results_table = driver.find_element(By.CLASS_NAME, "search-table")
            rows = results_table.find_elements(By.TAG_NAME, "tr")
            
            # Skip header row
            download_button = None
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, "td")
                if cells and filing_id in cells[0].text:
                    # Find the download button in this row
                    download_button = row.find_element(By.XPATH, ".//a[contains(text(), 'Download Filing')]")
                    break
            
            if download_button:
                print("Found filing in search results. Clicking download button...")
                
                # Click to download the ZIP file
                download_button.click()
                
                # Wait for download to complete (timeout after 60 seconds)
                # We'll assume download is complete after a short wait
                # This could be improved by checking for the actual file
                print("Waiting for download to complete...")
                time.sleep(10)  # Simple wait for download to start/complete
                
                # Check if file exists
                expected_zip_path = os.path.join(os.path.abspath("downloads"), f"{filing_id}.zip")
                
                # Wait a bit longer for the file to appear
                wait_time = 0
                while not os.path.exists(expected_zip_path) and wait_time < 30:
                    time.sleep(1)
                    wait_time += 1
                
                if os.path.exists(expected_zip_path):
                    print(f"ZIP downloaded to: {expected_zip_path}")
                    return True
                else:
                    print(f"ZIP file not found at expected location: {expected_zip_path}")
                    if attempt < max_retries:
                        print(f"Retrying in {2 ** attempt} seconds...")
                        time.sleep(2 ** attempt)
                    continue
            else:
                print("Filing not found in search results.")
                return False
                
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error during attempt {attempt}: {str(e)}")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("Maximum retry attempts reached. Giving up.")
                return False
    
    return False

def extract_zip(zip_path, extract_to_dir):
    """
    Extract a ZIP file to the specified directory
    
    Args:
        zip_path (str): Path to the ZIP file
        extract_to_dir (str): Directory to extract contents to
    
    Returns:
        list: List of PDF files in the extracted directory
    """
    # Ensure the extraction directory exists
    os.makedirs(extract_to_dir, exist_ok=True)
    
    print(f"Extracting ZIP file: {zip_path} to {extract_to_dir}")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to_dir)
        
        # Get a list of extracted PDF files
        pdf_files = [f for f in os.listdir(extract_to_dir) if f.lower().endswith('.pdf')]
        
        print(f"Extracted {len(pdf_files)} PDF files")
        print(f"Extracted PDFs: {pdf_files}")
        
        return pdf_files
    except zipfile.BadZipFile:
        print(f"Error: {zip_path} is not a valid ZIP file")
        return []
    except Exception as e:
        print(f"Error extracting ZIP file: {e}")
        return []

def main(filing_id=None):
    """
    Main function to orchestrate the filing search, download, and extraction
    
    Args:
        filing_id (str, optional): Filing ID to search for and download
    """
    # Default filing ID if none provided
    if not filing_id:
        filing_id = "20230924160904NAL0004813043001"  # Example filing ID
    
    # Ensure downloads directory exists
    downloads_dir = "./downloads"
    os.makedirs(downloads_dir, exist_ok=True)
    
    print(f"Starting EFAST2 scraper for filing ID: {filing_id}")
    
    # Setup browser
    driver = setup_browser(downloads_dir)
    
    try:
        # Search and download filing
        success = search_and_download_filing(driver, filing_id)
        
        if success:
            # Define ZIP path and extraction directory
            zip_path = os.path.join(downloads_dir, f"{filing_id}.zip")
            extract_dir = os.path.join(downloads_dir, filing_id)
            
            # Extract the ZIP file
            extract_zip(zip_path, extract_dir)
        else:
            print("Failed to download filing ZIP file")
    finally:
        # Clean up WebDriver instance
        print("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="EFAST2 Form 5500 Filing Scraper")
    parser.add_argument("--filing-id", type=str, help="Filing ID (ACK_ID) to search for and download")
    
    args = parser.parse_args()
    
    # Call main function with command line arguments
    main(filing_id=args.filing_id)