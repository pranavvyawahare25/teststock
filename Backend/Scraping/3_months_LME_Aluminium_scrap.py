import os
import time
import threading
import pandas as pd
import json
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, jsonify, send_file, Response, render_template
from concurrent.futures import ThreadPoolExecutor
import logging
import shutil

# Set up logging to console only (no file logging)
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Ensure the 'scraped_csv' directory exists
csv_dir = "scraped_csv"
os.makedirs(csv_dir, exist_ok=True)

csv_path = os.path.join(csv_dir, "3_months_LME_scrap.csv")

# Initialize CSV file with headers if it doesn't exist
if not os.path.exists(csv_path):
    pd.DataFrame(columns=["Value", "Time Span", "Rate of Change", "Timestamp"]).to_csv(csv_path, index=False)

# Track the latest data for quick access
latest_data = {
    "Value": None,
    "Date": None,
    "Rate of Change": None,
    "Timestamp": None,
    "error": None
}

# Create an event to notify when new data is available
new_data_event = threading.Event()

# Define constants
URL = "https://in.investing.com/commodities/aluminum"
XPATH_PRICE = "//div[@data-test='instrument-price-last']"
XPATH_CHANGE_VALUE = "//span[@data-test='instrument-price-change']"
XPATH_CHANGE_PERCENT = "//span[@data-test='instrument-price-change-percent']"
XPATH_TIME = "//time[@data-test='trading-time-label']"

# Track driver creation time to force recreation periodically
driver_created_time = 0
driver = None

# Track consecutive error count
error_count = 0
MAX_ERRORS = 5  # Maximum consecutive errors before forcing driver recreation

# Track last successful scrape time
last_successful_scrape = 0

# Create a temp directory for WebDriver
webdriver_temp_dir = "webdriver_temp"
os.makedirs(webdriver_temp_dir, exist_ok=True)

def cleanup_temp_files():
    """Clean up temporary files created by WebDriver"""
    try:
        for filename in os.listdir():
            if filename.endswith(".png") or filename.endswith(".log"):
                os.remove(filename)
                logger.info(f"Removed temporary file: {filename}")
    except Exception as e:
        logger.warning(f"Error cleaning temp files: {e}")

def get_browser_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-logging")
    options.add_argument("--log-level=3")
    
    # Set download preferences to prevent file downloads
    prefs = {
        "download.default_directory": webdriver_temp_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        "browser.download.manager.showWhenStarting": False,
        "profile.default_content_settings.popups": 0
    }
    options.add_experimental_option("prefs", prefs)
    
    # Performance optimizations
    options.add_argument("--disable-animations")
    options.add_argument("--disable-web-security")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.page_load_strategy = 'eager'  # Don't wait for all resources to load
    
    # Prevent detection
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    return options

def create_driver():
    """Create and return a new WebDriver instance"""
    global driver, driver_created_time
    
    # Close any existing driver
    if driver:
        try:
            driver.quit()
        except Exception as e:
            logger.warning(f"Error closing existing driver: {e}")
    
    try:
        logger.info("Creating new WebDriver instance")
        
        # Set cache_path to our temp directory to contain files
        cache_path = os.path.join(os.getcwd(), webdriver_temp_dir)
        
        # Custom ChromeDriverManager to control where files are downloaded
        service = Service(ChromeDriverManager(path=cache_path, log_level=0).install())
        options = get_browser_options()
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(15)
        driver_created_time = time.time()
        
        # Clean up any temporary files that might have been created
        cleanup_temp_files()
        
        return driver
    except Exception as e:
        logger.error(f"Failed to create WebDriver: {e}")
        return None

def try_api_fetch():
    """Try to fetch data from alternative sources first"""
    # List of URLs to try
    api_urls = [
        "https://in.investing.com/commodities/aluminum",  # Main URL as fallback
        
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/html, */*',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    for url in api_urls:
        try:
            logger.info(f"Trying to fetch data from {url}")
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                # This is a simplified approach - in production you would
                # parse the response properly based on the data format
                if "application/json" in response.headers.get("Content-Type", ""):
                    # Process JSON response
                    data = response.json()
                    # You would need to adapt this to match the actual API response structure
                    return {
                        "Value": str(data.get("last", "")),
                        "Date": data.get("date", ""),
                        "Rate of Change": f"{data.get('change', '')} ({data.get('change_percent', '')}%)",
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Source": "API"
                    }
                else:
                    # For now, just log that we got a response but continue with browser scraping
                    logger.info("Got non-JSON response, continuing with browser scraping")
        except Exception as e:
            logger.warning(f"API fetch attempt failed for {url}: {e}")
    
    return None

def get_cached_data(max_age=300):  # 5 minutes max age
    """Get cached data from CSV if recent enough"""
    try:
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if not df.empty:
                last_row = df.iloc[-1]
                
                # Check if timestamp is in the expected format
                try:
                    timestamp = last_row.get("Timestamp")
                    if timestamp and isinstance(timestamp, str):
                        last_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                        now = datetime.now()
                        age = (now - last_time).total_seconds()
                        
                        if age < max_age:
                            logger.info(f"Using cached data from {timestamp} (age: {age:.1f} seconds)")
                            return {
                                "Value": last_row.get("Value"),
                                "Date": last_row.get("Time Span"),
                                "Rate of Change": last_row.get("Rate of Change"),
                                "Timestamp": timestamp,
                                "Source": "Cache"
                            }
                except Exception as e:
                    logger.warning(f"Error parsing cached timestamp: {e}")
    except Exception as e:
        logger.warning(f"Error reading cached data: {e}")
    
    return None

def scrape_data_browser():
    """Scrape data using Selenium browser automation"""
    global driver, error_count, last_successful_scrape
    
    # Check if driver needs to be recreated due to age or errors
    driver_age = time.time() - driver_created_time if driver_created_time > 0 else float('inf')
    if driver is None or driver_age > 600 or error_count >= MAX_ERRORS:  # 10 minutes or max errors
        logger.info(f"Creating new driver. Age: {driver_age:.1f}s, Errors: {error_count}")
        driver = create_driver()
        error_count = 0
    
    if driver is None:
        logger.error("Failed to create WebDriver")
        return None
    
    try:
        # Navigate to the page
        logger.info(f"Navigating to {URL}")
        driver.get(URL)
        
        # Wait for main price element
        wait = WebDriverWait(driver, 10)
        price_element = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH_PRICE)))
        
        # Extract data
        value = price_element.text
        rate_change_value = driver.find_element(By.XPATH, XPATH_CHANGE_VALUE).text
        rate_change_percent = driver.find_element(By.XPATH, XPATH_CHANGE_PERCENT).text
        time_span = driver.find_element(By.XPATH, XPATH_TIME).text
        
        # Combine absolute & percentage change
        rate_change = f"{rate_change_value} ({rate_change_percent})"
        
        # Reset error count on success
        error_count = 0
        last_successful_scrape = time.time()
        
        logger.info(f"Successfully scraped: {value} | {rate_change} | {time_span}")
        
        # Clean up any temporary files
        cleanup_temp_files()
        
        return {
            "Value": value,
            "Date": time_span,
            "Rate of Change": rate_change,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Source": "Browser"
        }
        
    except Exception as e:
        error_count += 1
        logger.error(f"Browser scraping error ({error_count}/{MAX_ERRORS}): {e}")
        
        # If too many consecutive errors, try to recreate driver next time
        if error_count >= MAX_ERRORS:
            try:
                driver.quit()
            except:
                pass
            driver = None
        
        return None

def update_data(data):
    """Update the latest data and notify clients"""
    global latest_data
    
    # Update in-memory data
    latest_data = {
        "Value": data["Value"],
        "Date": data["Date"],
        "Rate of Change": data["Rate of Change"],
        "Timestamp": data["Timestamp"],
        "error": None
    }
    
    # Save to CSV in a thread to avoid blocking
    def save_to_csv():
        try:
            # Create DataFrame for new data
            data_df = pd.DataFrame([[
                data["Value"], 
                data["Date"], 
                data["Rate of Change"], 
                data["Timestamp"]
            ]], columns=["Value", "Time Span", "Rate of Change", "Timestamp"])
            
            # Check if file exists and has content
            if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
                # Read existing data
                try:
                    existing_df = pd.read_csv(csv_path)
                    # Append new data
                    combined_df = pd.concat([existing_df, data_df], ignore_index=True)
                    # Save combined data (overwrite file)
                    combined_df.to_csv(csv_path, index=False)
                    logger.info(f"Appended data to CSV: {data['Value']}")
                except Exception as e:
                    # If there's an error with existing file, overwrite with just the new data
                    logger.error(f"Error appending to CSV: {e}, overwriting file")
                    data_df.to_csv(csv_path, index=False)
            else:
                # File doesn't exist or is empty, write with headers
                data_df.to_csv(csv_path, index=False)
                logger.info(f"Created new CSV with data: {data['Value']}")
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
    
    # Use ThreadPoolExecutor for non-blocking CSV write
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(save_to_csv)
    
    # Notify connected clients
    new_data_event.set()
    new_data_event.clear()
    
    return True

def scrape_data():
    """Main data scraping function with multiple fallback mechanisms"""
    # First, try API approach
    api_data = try_api_fetch()
    if api_data:
        logger.info(f"API data fetch successful: {api_data['Value']}")
        return update_data(api_data)
    
    # Second, try browser scraping
    browser_data = scrape_data_browser()
    if browser_data:
        logger.info(f"Browser scraping successful: {browser_data['Value']}")
        return update_data(browser_data)
    
    # Last resort: use cached data if available and not too old
    time_since_last_success = time.time() - last_successful_scrape
    cached_data = get_cached_data(max_age=300 if time_since_last_success < 600 else 3600)
    if cached_data:
        logger.info(f"Using cached data: {cached_data['Value']}")
        return update_data(cached_data)
    
    logger.error("All data fetch methods failed")
    return False

def continuous_scraping(interval=5):
    """Function to continuously scrape data at regular intervals"""
    global error_count
    
    # Initial scrape to populate data
    scrape_data()
    
    while True:
        try:
            start_time = time.time()
            
            # Attempt to scrape data
            success = scrape_data()
            
            # Calculate time spent
            elapsed = time.time() - start_time
            logger.info(f"Scraping {'succeeded' if success else 'failed'} in {elapsed:.2f} seconds")
            
            # Clean up any temporary files
            cleanup_temp_files()
            
            # Dynamically adjust sleep time based on scrape duration
            adjusted_interval = max(0.5, interval - elapsed)
            logger.info(f"Waiting {adjusted_interval:.2f} seconds before next scrape")
            time.sleep(adjusted_interval)
            
        except Exception as e:
            logger.error(f"Unexpected error in scraping thread: {str(e)}")
            time.sleep(max(1, interval / 2))  # Shorter sleep on error

@app.route('/data')
def get_data():
    """Return the latest scraped data as JSON"""
    # If we have latest data already
    if latest_data["Value"] is not None:
        return jsonify({
            "success": True,
            "data": latest_data
        })
    
    # If no data has been scraped yet, try to scrape now
    if scrape_data():
        return jsonify({
            "success": True,
            "data": latest_data
        })
    
    # If scraping failed, try to return the latest data from CSV
    try:
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if not df.empty:
                csv_latest = df.iloc[-1].to_dict()
                return jsonify({
                    "success": True,
                    "data": {
                        "Value": csv_latest.get("Value"),
                        "Date": csv_latest.get("Time Span"),
                        "Rate of Change": csv_latest.get("Rate of Change"),
                        "Timestamp": csv_latest.get("Timestamp"),
                        "note": "Using latest available data from CSV"
                    }
                })
    except Exception as e:
        logger.error(f"Error retrieving CSV data: {e}")
    
    # No data available
    return jsonify({
        "success": False,
        "error": latest_data["error"] or "No data available"
    })

@app.route('/stream')
def stream():
    """SSE endpoint for pushing updates to connected clients"""
    def generate():
        last_data = None
        
        while True:
            # Wait for the new data event to be set or timeout
            new_data_event.wait(timeout=10)
            
            # Only send data if it's changed or first time
            current_data_str = json.dumps(latest_data) if latest_data["Value"] else None
            
            if current_data_str and current_data_str != last_data:
                yield f"data: {current_data_str}\n\n"
                last_data = current_data_str
            else:
                # Send heartbeat with current timestamp
                heartbeat = {"heartbeat": True, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                yield f"data: {json.dumps(heartbeat)}\n\n"
            
            time.sleep(1)
    
    return Response(generate(), mimetype="text/event-stream")

@app.route('/download')
def download_csv():
    """Download the complete CSV file"""
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
        # Ensure all pending writes are complete
        time.sleep(0.5)
        return send_file(
            csv_path, 
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"aluminum_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
    else:
        return jsonify({
            "success": False,
            "error": "CSV file not found or empty"
        }), 404

def cleanup():
    """Cleanup function to close browser when app exits"""
    global driver
    if driver:
        try:
            driver.quit()
        except:
            pass
        driver = None
    
    # Clean up any temporary files and directories
    cleanup_temp_files()
    
    try:
        # Clean up the temp directory completely
        if os.path.exists(webdriver_temp_dir):
            shutil.rmtree(webdriver_temp_dir, ignore_errors=True)
            logger.info(f"Removed temporary directory: {webdriver_temp_dir}")
    except Exception as e:
        logger.warning(f"Error removing temp directory: {e}")

# Register cleanup function
import atexit
atexit.register(cleanup)

if __name__ == "__main__":
    # Clean up any old files before starting
    cleanup_temp_files()
    
    # Create dedicated temp directory
    if os.path.exists(webdriver_temp_dir):
        shutil.rmtree(webdriver_temp_dir, ignore_errors=True)
    os.makedirs(webdriver_temp_dir, exist_ok=True)
    
    # Start the background scraping thread
    logger.info("Starting background scraping thread...")
    scraper_thread = threading.Thread(target=continuous_scraping, daemon=True)
    scraper_thread.start()
    
    port = 5003
    logger.info(f"Starting Flask server on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)







# older version without flask 
# import os
# import sys
# import time
# import signal
# import pandas as pd
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# # Ensure the 'scraped_csv' directory exists
# csv_dir = "scraped_csv"
# os.makedirs(csv_dir, exist_ok=True)

# csv_path = os.path.join(csv_dir, "3_months_LME_scrap.csv")

# # Initialize CSV file with headers if it doesn't exist
# if not os.path.exists(csv_path):
#     pd.DataFrame(columns=["Value", "Time Span", "Rate of Change"]).to_csv(csv_path, index=False)

# def signal_handler(sig, frame):
#     print("User interrupted the process. Closing browser and exiting...")
#     if 'driver' in globals() and driver:
#         try:
#             driver.quit()
#         except:
#             pass
#     sys.exit(0)

# # Register signal handler for Ctrl+C
# signal.signal(signal.SIGINT, signal_handler)

# # Define constants
# URL = "https://in.investing.com/commodities/aluminum"
# XPATH_PRICE = "//div[@data-test='instrument-price-last']"
# XPATH_CHANGE_VALUE = "//span[@data-test='instrument-price-change']"
# XPATH_CHANGE_PERCENT = "//span[@data-test='instrument-price-change-percent']"
# XPATH_TIME = "//time[@data-test='trading-time-label']"

# def get_browser_options():
#     options = webdriver.ChromeOptions()
#     # options.add_argument("--headless")  # Uncomment for production
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--disable-logging")
#     options.add_argument("--log-level=3")
#     options.add_argument("--blink-settings=imagesEnabled=false")
#     return options

# def create_driver():
#     """Create and return a new WebDriver instance"""
#     try:
#         service = Service(ChromeDriverManager().install())
#         options = get_browser_options()
#         driver = webdriver.Chrome(service=service, options=options)
#         driver.set_page_load_timeout(60)
#         return driver
#     except Exception as e:
#         print(f"\u274c Error creating driver: {e}")
#         return None

# def scrape_data(driver):
#     """Scrape data with the given driver"""
#     try:
#         # Navigate to the page
#         driver.get(URL)
        
#         # Wait for main price element to be visible
#         wait = WebDriverWait(driver, 20)
#         wait.until(EC.visibility_of_element_located((By.XPATH, XPATH_PRICE)))
        
#         # Extract data
#         value = driver.find_element(By.XPATH, XPATH_PRICE).text
#         rate_change_value = driver.find_element(By.XPATH, XPATH_CHANGE_VALUE).text
#         rate_change_percent = driver.find_element(By.XPATH, XPATH_CHANGE_PERCENT).text
#         time_span = driver.find_element(By.XPATH, XPATH_TIME).text
        
#         # Combine absolute & percentage change
#         rate_change = f"{rate_change_value} ({rate_change_percent})"
        
#         # Create and save dataframe (append mode)
#         data = pd.DataFrame([[value, time_span, rate_change]], columns=["Value", "Time Span", "Rate of Change"])
#         data.to_csv(csv_path, mode="a", index=False, header=False)
        
#         print(f"\u2705 Data scraped at {time.strftime('%H:%M:%S')}: {value} | {rate_change} | {time_span}")
#         return True
#     except Exception as e:
#         print(f"\u274c Error during scraping: {e}")
#         return False

# print("Starting continuous data scraping. Press Ctrl+C to stop.")

# max_retries = 3  # Maximum retries per attempt

# while True:
#     driver = None
#     try:
#         # Create a new browser instance for each scrape
#         driver = create_driver()
#         if not driver:
#             print("Failed to create driver, retrying in 5 seconds...")
#             time.sleep(5)
#             continue
            
#         # Try to scrape data with retries
#         success = False
#         for retry in range(max_retries):
#             success = scrape_data(driver)
#             if success:
#                 break
#             else:
#                 print(f"Retry {retry+1}/{max_retries}...")
#                 time.sleep(2)
        
#         # Close the driver after each successful scrape
#         driver.quit()
#         driver = None
        
#         # Sleep for 3 seconds between scrapes
#         print(f"Waiting 3 seconds before next scrape...")
#         time.sleep(3)
        
#     except KeyboardInterrupt:
#         print("Scraping stopped by user.")
#         if driver:
#             try:
#                 driver.quit()
#             except:
#                 pass
#         sys.exit(0)
#     except Exception as e:
#         print(f"\u274c Unexpected error: {e}")
#         if driver:
#             try:
#                 driver.quit()
#             except:
#                 pass
#         # Wait before retrying
#         print("Waiting 5 seconds before retrying...")
#         time.sleep(5)

