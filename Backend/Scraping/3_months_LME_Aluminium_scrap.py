import os
import time
import threading
import pandas as pd
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, jsonify, send_file, Response, render_template

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
    "Time span": None,
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

def get_browser_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # Use headless mode for server environment
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-logging")
    options.add_argument("--log-level=3")
    options.add_argument("--blink-settings=imagesEnabled=false")
    # Add user agent to reduce detection chances
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return options

def create_driver():
    """Create and return a new WebDriver instance"""
    try:
        service = Service(ChromeDriverManager().install())
        options = get_browser_options()
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)
        return driver
    except Exception as e:
        print(f"❌ Error creating driver: {e}")
        latest_data["error"] = str(e)
        return None

def scrape_data():
    """Scrape data and store it in the latest_data dict and CSV"""
    global latest_data
    driver = None
    try:
        driver = create_driver()
        if not driver:
            print("Failed to create WebDriver")
            return False
        
        # Navigate to the page
        driver.get(URL)
        
        # Wait for main price element to be visible
        wait = WebDriverWait(driver, 20)
        wait.until(EC.visibility_of_element_located((By.XPATH, XPATH_PRICE)))
        
        # Extract data
        value = driver.find_element(By.XPATH, XPATH_PRICE).text
        rate_change_value = driver.find_element(By.XPATH, XPATH_CHANGE_VALUE).text
        rate_change_percent = driver.find_element(By.XPATH, XPATH_CHANGE_PERCENT).text
        time_span = driver.find_element(By.XPATH, XPATH_TIME).text
        
        # Combine absolute & percentage change
        rate_change = f"{rate_change_value} ({rate_change_percent})"
        
        # Current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Update the latest data
        latest_data = {
            "Value": value,
            "Time span": time_span,
            "Rate of Change": rate_change,
            "Timestamp": timestamp,
            "error": None
        }
        
        # Save to CSV for historical records
        data = pd.DataFrame([[value, time_span, rate_change, timestamp]], 
                            columns=["Value", "Time Span", "Rate of Change", "Timestamp"])
        data.to_csv(csv_path, mode="a", index=False, header=False)
        
        # Set the event to trigger updates to connected clients
        new_data_event.set()
        new_data_event.clear()
        
        print(f"✅ Data scraped at {timestamp}: {value} | {rate_change} | {time_span}")
        return True
    
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        latest_data["error"] = str(e)
        return False
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def continuous_scraping(interval=1):
    """Function to continuously scrape data at regular intervals"""
    max_retries = 3  # Maximum retries per attempt
    
    while True:
        try:
            # Try to scrape data with retries
            success = False
            for retry in range(max_retries):
                success = scrape_data()
                if success:
                    break
                else:
                    print(f"Retry {retry+1}/{max_retries}...")
                    time.sleep(2)
            
            # Sleep for the specified interval between scrapes
            print(f"Waiting {interval} seconds before next scrape...")
            time.sleep(interval)
            
        except Exception as e:
            print(f"❌ Unexpected error in scraping thread: {e}")
            time.sleep(5)


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
                    "data": csv_latest,
                    "note": "Using latest available data from CSV"
                })
    except Exception as e:
        pass
    
    # No data available
    return jsonify({
        "success": False,
        "error": latest_data["error"] or "No data available"
    })

@app.route('/stream')
def stream():
    """SSE endpoint for pushing updates to connected clients"""
    def generate():
        while True:
            # Wait for the new data event to be set
            new_data_event.wait(timeout=120)
            
            # Send the latest data
            if latest_data["Value"] is not None:
                data_str = json.dumps(latest_data)
                yield f"data: {data_str}\n\n"
            
            # If no update in 30 seconds, send a heartbeat to keep connection alive
            else:
                yield f"data: {json.dumps({'heartbeat': True})}\n\n"
                
            time.sleep(5)  # Small delay to prevent CPU overload
    
    return Response(generate(), mimetype="text/event-stream")

@app.route('/download')
def download_csv():
    """Download the complete CSV file"""
    if os.path.exists(csv_path):
        return send_file(csv_path, as_attachment=True)
    else:
        return jsonify({
            "success": False,
            "error": "CSV file not found"
        }), 404

if __name__ == "__main__":
    # Start the background scraping thread
    print("Starting background scraping thread...")
    scraper_thread = threading.Thread(target=continuous_scraping, daemon=True)
    scraper_thread.start()
    
    port = 5003
    print(f"Starting Flask server on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)






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

