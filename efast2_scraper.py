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
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def take_debug_screenshot(driver, name="debug"):
    """Take a screenshot for debugging purposes"""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{name}_{timestamp}.png"
    driver.save_screenshot(filename)
    print(f"Screenshot saved: {filename}")
    return filename

def click_download_icon(driver):
    wait = WebDriverWait(driver, 20)
    
    # Take a screenshot before looking for the icon
    take_debug_screenshot(driver, "before_download_click")
    
    # Print the page title and URL for debugging
    print(f"Current page title: {driver.title}")
    print(f"Current URL: {driver.current_url}")
    
    # Try multiple approaches to find and click the download element
    # NEW APPROACH: Look for direct download link in the row of results
    try:
        print("Approach 0: Looking for direct download link...")
        # Try to find any link containing "Download" text
        download_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Download')]")
        if len(download_links) > 0:
            print(f"Found {len(download_links)} direct download links")
            
            # Click the first download link
            link = download_links[0]
            print(f"First link text: {link.text}, href: {link.get_attribute('href')}")
            
            # Try JavaScript click first
            try:
                driver.execute_script("arguments[0].click();", link)
                print("✅ JavaScript click on direct download link succeeded")
                return True
            except Exception as e:
                print(f"JavaScript click failed: {e}")
                
                # Try regular click
                try:
                    link.click()
                    print("✅ Regular click on direct download link succeeded")
                    return True
                except Exception as e2:
                    print(f"Regular click failed: {e2}")
    except Exception as e:
        print(f"Approach 0 failed: {e}")
    
    # Try finding the download button based on SPAN or Button text
    try:
        print("Approach 0.5: Looking for download button or span...")
        # Try buttons or spans with Download text
        elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Download') and (self::button or self::span)]")
        if len(elements) > 0:
            print(f"Found {len(elements)} elements with 'Download' text")
            
            # Click the first element
            element = elements[0]
            print(f"Element tag: {element.tag_name}, text: {element.text}")
            
            driver.execute_script("arguments[0].click();", element)
            print("✅ JavaScript click on element with 'Download' text succeeded")
            return True
    except Exception as e:
        print(f"Approach 0.5 failed: {e}")
        
    # Try to find any clickable element in the last cell of the result row
    try:
        print("Approach 1: Looking for interactive element in the last cell...")
        # Find the result table
        table = driver.find_element(By.CLASS_NAME, "usa-table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        if len(rows) > 1:  # Skip header
            row = rows[1]
            cells = row.find_elements(By.TAG_NAME, "td")
            
            if cells:
                # Focus on the last or second-to-last cell (often contains actions)
                for cell_index in [-1, -2]:  # Try last cell, then second-to-last
                    try:
                        cell = cells[cell_index]
                        print(f"Examining cell {cell_index}: {cell.text}")
                        
                        # Look for any interactive elements in this cell
                        for selector in ["a", "button", "svg", "span[role='button']", "span[onclick]", "div[onclick]", "i.fa"]:
                            elements = cell.find_elements(By.CSS_SELECTOR, selector)
                            if elements:
                                print(f"Found {len(elements)} {selector} elements in the cell")
                                element = elements[0]
                                
                                # Try JavaScript click
                                driver.execute_script("arguments[0].click();", element)
                                print(f"✅ JavaScript click on {selector} in cell {cell_index} succeeded")
                                return True
                    except IndexError:
                        print(f"Cell index {cell_index} out of range")
                        continue
    except Exception as e:
        print(f"Approach 1 failed: {e}")
    
    # Original approaches below
    try:
        # Look for any SVG with afs-cursor-pointer class
        print("Approach 2: Looking for SVG with afs-cursor-pointer class...")
        svg_elements = driver.find_elements(By.CSS_SELECTOR, "svg.afs-cursor-pointer")
        print(f"Found {len(svg_elements)} matching SVG elements")
        
        if len(svg_elements) > 0:
            svg = svg_elements[0]
            print(f"First SVG classes: {svg.get_attribute('class')}")
            
            # For SVG elements, we need a different approach since they might not have a click method
            # Try finding a parent element that's clickable
            try:
                # Find the parent or ancestor element that might be clickable
                clickable_parent = driver.execute_script(
                    "return arguments[0].closest('a') || arguments[0].closest('button') || arguments[0].parentElement", 
                    svg
                )
                
                if clickable_parent:
                    print(f"Found clickable parent: {clickable_parent.tag_name}")
                    driver.execute_script("arguments[0].click();", clickable_parent)
                    print("✅ JavaScript click on SVG parent succeeded")
                    
                    # Wait for download to start
                    time.sleep(5)
                    
                    # Check for any files in the download directory (including PDFs)
                    download_dir = os.path.abspath("./downloads")
                    for attempt in range(30):  # Check for 30 seconds
                        files = os.listdir(download_dir)
                        download_files = [f for f in files if f.endswith(('.zip', '.pdf')) and not f.endswith('.download')]
                        if download_files:
                            print(f"Download detected: {download_files}")
                            return True
                        print(f"Waiting for download to appear... {attempt+1}/30")
                        time.sleep(1)
                    
                    # If we get here, the click succeeded but no download appeared
                    print("Download may be in progress, return True to continue...")
                    return True
                    
                else:
                    print("No clickable parent found, falling back to ActionChains")
            except Exception as e:
                print(f"JavaScript parent click failed: {e}")
                
            # Fall back to ActionChains
            try:
                actions = ActionChains(driver)
                actions.move_to_element(svg).pause(0.5).click().perform()
                print("✅ ActionChains click on SVG succeeded")
                
                # Wait for download to start
                time.sleep(5)
                
                # Check for any files in the download directory (including PDFs)
                download_dir = os.path.abspath("./downloads")
                for attempt in range(30):  # Check for 30 seconds
                    files = os.listdir(download_dir)
                    download_files = [f for f in files if f.endswith(('.zip', '.pdf')) and not f.endswith('.download')]
                    if download_files:
                        print(f"Download detected: {download_files}")
                        return True
                    print(f"Waiting for download to appear... {attempt+1}/30")
                    time.sleep(1)
                
                # If we get here, the click succeeded but no download appeared
                print("Download may be in progress, return True to continue...")
                return True
            except Exception as e2:
                    print(f"ActionChains click failed: {e2}")
    except Exception as e:
        print(f"Approach 2 failed: {e}")
    
    # Try to find the TD containing the download icon
    try:
        print("Approach 3: Looking for TD with table-padding-spec class...")
        td_elements = driver.find_elements(By.CSS_SELECTOR, "td.table-padding-spec")
        print(f"Found {len(td_elements)} matching TD elements")
        
        if len(td_elements) > 0:
            td = td_elements[0]
            print(f"First TD classes: {td.get_attribute('class')}")
            
            driver.execute_script("arguments[0].click();", td)
            print("✅ JavaScript click on TD succeeded")
            return True
    except Exception as e:
        print(f"Approach 3 failed: {e}")
    
    # Look for any a tag with file_download in the href
    try:
        print("Approach 4: Looking for link with file_download...")
        links = driver.find_elements(By.XPATH, "//use[contains(@xlink:href, 'file_download')]")
        print(f"Found {len(links)} matching links")
        
        if len(links) > 0:
            link = links[0]
            print(f"Link href: {link.get_attribute('xlink:href')}")
            
            # Try to find the parent SVG and click that
            parent_svg = driver.execute_script("return arguments[0].closest('svg')", link)
            if parent_svg:
                driver.execute_script("arguments[0].click();", parent_svg)
                print("✅ JavaScript click on parent SVG succeeded")
                return True
    except Exception as e:
        print(f"Approach 4 failed: {e}")
    
    # Final desperate attempt: try to click anything that might be a download button
    try:
        print("Approach 5: Trying all potential download elements...")
        
        # Common selectors for download elements
        selectors = [
            "button[data-testid*='download']",
            "a[data-testid*='download']",
            "button[aria-label*='download']",
            "a[aria-label*='download']",
            "button[title*='download']",
            "a[title*='download']",
            "button.download",
            "a.download",
            "button.icon-download",
            "a.icon-download",
            "*[role='button'][aria-label*='download']",
            ".download-button",
            ".download-link"
        ]
        
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"Found {len(elements)} elements matching selector: {selector}")
                element = elements[0]
                driver.execute_script("arguments[0].click();", element)
                print(f"✅ JavaScript click on element with selector '{selector}' succeeded")
                return True
    except Exception as e:
        print(f"Approach 5 failed: {e}")
    
    # If all else fails, take a screenshot and dump the HTML
    take_debug_screenshot(driver, "download_icon_not_found")
    
    # Save HTML for inspection
    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved page source to page_source.html")
    
    print("❌ All approaches to find and click download icon failed")
    return False

def setup_browser(download_dir, headless=True):
    # Get absolute path to download directory
    download_path = os.path.abspath(download_dir)
    os.makedirs(download_path, exist_ok=True)
    print(f"Setting up Chrome browser with download directory: {download_path}")
    
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    if headless:
        chrome_options.add_argument("--headless=new")
    
    # Disable automation detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # Configure download behavior
    chrome_prefs = {
        "profile.default_content_settings.popups": 0,
        "download.default_directory": download_path,
        "download.directory_upgrade": True,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": True,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", chrome_prefs)

    driver = webdriver.Chrome(options=chrome_options)
    
    # Patch navigator.webdriver to False to avoid detection
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        },
    )
    
    # Set page load timeout
    driver.set_page_load_timeout(60)
    
    # Set window size explicitly
    driver.set_window_size(1920, 1080)
    
    # Enable downloads in headless Chrome
    if headless:
        driver.execute_cdp_cmd(
            "Page.setDownloadBehavior", 
            {
                "behavior": "allow",
                "downloadPath": download_path
            }
        )
    
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
    
    Note: This function MUST exit immediately after a successful download click
    to prevent any further page interactions that might interrupt the download.
    """
    # URL for DOL EFAST2 5500 Search portal
    efast2_url = "https://www.efast.dol.gov/5500Search/"
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt}/{max_retries} - Navigating to EFAST2 search portal...")
            driver.get(efast2_url)
            
            # Wait for page to load by checking for the presence of the search form
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.ID, "categoryType"))
            )
            
            print("Page loaded. Looking for popup close button...")
            
            # Look for and click the close button by its ID
            try:
                # Wait for the close button to be clickable
                close_button = WebDriverWait(driver, 2).until(
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
            submit_button = driver.find_element(By.XPATH, "//button[@class='usa-button' and @type='submit']")
            submit_button.click()
            
            # Wait for search results to appear
            print("Waiting for search results...")
            try:
                WebDriverWait(driver, 10).until(  # Increased timeout
                    EC.presence_of_element_located((By.CLASS_NAME, "usa-table"))
                )
                print("Search results table found")
                
                # Take a screenshot of the search results
                take_debug_screenshot(driver, "search_results")
                
                # Print some information about the table
                tables = driver.find_elements(By.CLASS_NAME, "usa-table")
                print(f"Found {len(tables)} tables with class 'usa-table'")
                
                if len(tables) > 0:
                    table = tables[0]
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    print(f"Table has {len(rows)} rows")
                    
                    # Print a sample of the first row content
                    if len(rows) > 1:  # Skip header row
                        first_row = rows[1]
                        cells = first_row.find_elements(By.TAG_NAME, "td")
                        print(f"First result row has {len(cells)} cells")
                        cell_texts = [cell.text for cell in cells]
                        print(f"First row content: {cell_texts}")
                        
                        # Attempt to click the download icon
                        print("Attempting to click download icon...")
                        download_success = click_download_icon(driver)
                        if download_success:
                            print("Download initiated successfully")
                            # We need to return immediately after a successful click to avoid interfering with the download
                            print("Download started - returning now to avoid interfering with the browser")
                            # IMPORTANT: Return immediately after successful download click
                            return True
                        else:
                            print("Failed to click download icon")
            except TimeoutException:
                print("❌ Search results table not found within timeout")
                take_debug_screenshot(driver, "no_search_results")
                
                # Check if there are any error messages
                error_elements = driver.find_elements(By.CLASS_NAME, "usa-alert--error")
                if len(error_elements) > 0:
                    print(f"Error message found: {error_elements[0].text}")
                
                if attempt < max_retries:
                    print(f"Retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)
                    continue
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
        filing_id = "20240924160451NAL0013030593001"  # Example filing ID
    
    # Ensure downloads directory exists
    downloads_dir = "./downloads"
    downloads_abs_path = os.path.abspath(downloads_dir)
    os.makedirs(downloads_abs_path, exist_ok=True)
    
    print(f"Starting EFAST2 scraper for filing ID: {filing_id}")
    print(f"Downloads will be saved to: {downloads_abs_path}")
    
    # Clear any existing files with the same name
    for extension in ['.zip', '.pdf']:
        potential_file_path = os.path.join(downloads_abs_path, f"{filing_id}{extension}")
        if os.path.exists(potential_file_path):
            print(f"Removing existing file: {potential_file_path}")
            try:
                os.remove(potential_file_path)
            except Exception as e:
                print(f"Error removing existing file: {e}")
    
    # Setup browser - using non-headless mode for better download handling
    driver = setup_browser(downloads_abs_path, False)
    
    try:
        # Search and download filing
        success = search_and_download_filing(driver, filing_id)
        
        if success:
            print("Download was initiated successfully")
            print("Waiting for download to complete...")

            # Wait longer for downloads to complete
            time.sleep(10)
            
            # Check for downloaded files
            downloaded_files = os.listdir(downloads_abs_path)
            print(f"Files in download directory: {downloaded_files}")
            
            # Filter downloaded files
            zip_files = [f for f in downloaded_files if f.endswith('.zip')]
            pdf_files = [f for f in downloaded_files if f.endswith('.pdf')]
            
            if zip_files:
                print(f"Found ZIP files: {zip_files}")
                # Process ZIP files
                for zip_file in zip_files:
                    zip_path = os.path.join(downloads_abs_path, zip_file)
                    extract_dir = os.path.join(downloads_abs_path, os.path.splitext(zip_file)[0])
                    print(f"Extracting {zip_file} to {extract_dir}")
                    extract_zip(zip_path, extract_dir)
                    
            elif pdf_files:
                print(f"Found PDF files: {pdf_files}")
                print("PDF files do not need extraction, they can be used directly.")
                for pdf_file in pdf_files:
                    print(f"Downloaded PDF: {os.path.join(downloads_abs_path, pdf_file)}")
                
            else:
                print("No ZIP or PDF files found in the download directory.")
                print(f"All files in directory: {downloaded_files}")
                
                # Check for incomplete downloads
                incomplete_downloads = [f for f in downloaded_files if f.endswith('.download')]
                if incomplete_downloads:
                    print(f"Found incomplete downloads: {incomplete_downloads}")
                    print("Download may still be in progress. Wait for downloads to complete manually.")
                    
        else:
            print("Failed to initiate file download")
    finally:
        # Take a final screenshot before closing
        if driver:
            take_debug_screenshot(driver, "final_state")
            
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