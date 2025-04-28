from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

def setup_browser(download_dir="./downloads", headless=False):
    options = webdriver.ChromeOptions()
    
    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "plugins.always_open_pdf_externally": True,  # Disable Chrome PDF Viewer
    }
    options.add_experimental_option("prefs", prefs)
    
    if headless:
        #options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=options)
    return driver

def search_and_download(driver, ack_id):
    driver.get("https://www.efast.dol.gov/5500Search/")
    
    wait = WebDriverWait(driver, 15)

    # Change the search category to ACK ID
    category_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "categoryType")))
    select = Select(category_dropdown)
    select.select_by_visible_text("ACK ID")

    # Enter the ACK ID
    search_box = driver.find_element(By.ID, "searchVal")
    search_box.clear()
    search_box.send_keys(ack_id)
    search_box.send_keys(Keys.RETURN)

    # Wait for results to load
    result_download_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Download Filing')]")))
    
    time.sleep(1)  # Small extra wait to avoid race conditions

    # Click the Download Filing button
    result_download_button.click()

    print(f"✅ Download triggered for ACK_ID: {ack_id}")

def main():
    ack_id = "20240924160451NAL0013030593001"  # Replace with your real Filing ID
    download_folder = "./downloads"

    os.makedirs(download_folder, exist_ok=True)

    driver = setup_browser(download_dir=download_folder, headless=False)

    try:
        search_and_download(driver, ack_id)
        
        # Give it time to finish downloading (adjust if needed)
        print("⏳ Waiting for download to complete...")
        time.sleep(10)
        
    finally:
        driver.quit()
        print("✅ Browser closed.")

if __name__ == "__main__":
    main()
