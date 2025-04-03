# import csv
# import os
# import time
# import threading
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from datetime import datetime, timedelta
# from flask import Flask, jsonify, send_file
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)

# # Setup Selenium WebDriver
# def get_driver():
#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless")  # Run in headless mode
#     return webdriver.Chrome(options=options)

# # URL of the page
# url = "https://www.5paisa.com/commodity-trading/mcx-aluminium-price"

# def get_contract_months():
#     today = datetime.today()
#     contract_months = {}
    
#     for i in range(3):
#         future_date = today.replace(day=1) + timedelta(days=32 * i)  # Jump to next month
#         future_date = future_date.replace(day=30)  # Always set to the 30th
#         month_year_str = future_date.strftime("%B %d %Y")  # Format: "April 30 2025"
#         xpath = f"//input[@name='toggle-comm' and contains(@value, '{future_date.month}-30-{future_date.year}')]"
#         contract_months[month_year_str] = xpath
    
#     return contract_months

# contract_months = get_contract_months()

# # CSV filename
# csv_filename = "scraped_csv/mcx_aluminium_prices.csv"

# # Ensure directory exists
# os.makedirs(os.path.dirname(csv_filename), exist_ok=True)

# def extract_data():
#     driver = get_driver()
#     driver.get(url)
#     try:
#         # Extract date & time
#         date_time_element = WebDriverWait(driver, 10).until(
#             EC.visibility_of_element_located((By.CLASS_NAME, "commodity-page__date"))
#         )
#         date_time_text = date_time_element.text.replace("As on ", "").strip()
#         date_obj = datetime.strptime(date_time_text, "%d %B, %Y | %H:%M")
#         date_str, time_str = date_obj.strftime("%Y-%m-%d"), date_obj.strftime("%H:%M")
        
#         row_data = {"date": date_str, "time": time_str, "prices": {}}
        
#         # Extract contract prices and rate changes
#         for month, xpath in contract_months.items():
#             try:
#                 radio_button = WebDriverWait(driver, 10).until(
#                     EC.presence_of_element_located((By.XPATH, xpath))
#                 )
#                 driver.execute_script("arguments[0].click();", radio_button)
#                 time.sleep(3)  # Allow time for the price to update

#                 price_element = WebDriverWait(driver, 10).until(
#                     EC.visibility_of_element_located((By.CLASS_NAME, "commodity-page__value"))
#                 )
#                 price = price_element.text.strip().replace("₹", "")
                
#                 rate_element = WebDriverWait(driver, 10).until(
#                     EC.visibility_of_element_located((By.CLASS_NAME, "commodity-page__percentage"))
#                 )
#                 rate_change = rate_element.text.strip()
                
#                 row_data["prices"][month] = {"price": price, "rate_change": rate_change}
#             except Exception:
#                 row_data["prices"][month] = {"price": "N/A", "rate_change": "N/A"}
        
#         driver.quit()
#         save_to_csv(row_data)
#         return row_data
#     except Exception as e:
#         driver.quit()
#         return {"error": str(e)}

# def save_to_csv(data):
#     headers = ["Date", "Time"] + list(contract_months.keys())
#     row = [data["date"], data["time"]] + [f'{data["prices"][month]["price"]} ({data["prices"][month]["rate_change"]})' for month in contract_months]
    
#     file_exists = os.path.exists(csv_filename)
#     with open(csv_filename, "a", newline="", encoding="utf-8") as file:
#         writer = csv.writer(file)
#         if not file_exists:
#             writer.writerow(headers)
#         writer.writerow(row)

# # Background scraper thread
# def scraper_thread():
#     while True:
#         print("\n🚀 Scraping started!")
#         extract_data()
#         print("✅ Data scraped and saved.")
#         time.sleep(5)  # Scrape every 2 seconds

# @app.route("/scrape", methods=["GET"])
# def scrape():
#     data = extract_data()
#     return jsonify(data)

# @app.route("/download", methods=["GET"])
# def download_csv():
#     if os.path.exists(csv_filename):
#         return send_file(csv_filename, as_attachment=True)
#     return jsonify({"error": "CSV file not found"}), 404

# if __name__ == "__main__":
#     thread = threading.Thread(target=scraper_thread, daemon=True)
#     thread.start()
#     app.run(debug=True, port=5000)



# older version without flask 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import sys
import signal

def signal_handler(sig, frame):
    print("User interrupted the process. Closing browser and exiting...")
    if 'driver' in globals() and driver:
        try:
            driver.quit()
        except:
            pass
    sys.exit(0)

# Register signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Initialize CSV file with headers if it doesn't exist
try:
    with open("scraped_csv/3_months_LME_scrap.csv", "r") as f:
        pass
except FileNotFoundError:
    pd.DataFrame(columns=["Value", "Time Span", "Rate of Change"]).to_csv("scraped_csv/3_months_LME_scrap.csv", index=False)

# Define constants
URL = "https://in.investing.com/commodities/aluminum"
XPATH_PRICE = "//div[@data-test='instrument-price-last']"
XPATH_CHANGE_VALUE = "//span[@data-test='instrument-price-change']"
XPATH_CHANGE_PERCENT = "//span[@data-test='instrument-price-change-percent']"
XPATH_TIME = "//time[@data-test='trading-time-label']"

def get_browser_options():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Uncomment for production
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-logging")
    options.add_argument("--log-level=3")
    options.add_argument("--blink-settings=imagesEnabled=false")
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
        return None

def scrape_data(driver):
    """Scrape data with the given driver"""
    try:
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
        
        # Create and save dataframe (append mode)
        data = pd.DataFrame([[value, time_span, rate_change]], columns=["Value", "Time Span", "Rate of Change"])
        data.to_csv("scraped_csv/3_months_LME_scrap.csv", mode="a", index=False, header=False)
        
        print(f"✅ Data scraped at {time.strftime('%H:%M:%S')}: {value} | {rate_change} | {time_span}")
        return True
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return False

print("Starting continuous data scraping. Press Ctrl+C to stop.")

max_retries = 3  # Maximum retries per attempt

while True:
    driver = None
    try:
        # Create a new browser instance for each scrape
        driver = create_driver()
        if not driver:
            print("Failed to create driver, retrying in 5 seconds...")
            time.sleep(5)
            continue
            
        # Try to scrape data with retries
        success = False
        for retry in range(max_retries):
            success = scrape_data(driver)
            if success:
                break
            else:
                print(f"Retry {retry+1}/{max_retries}...")
                time.sleep(2)
        
        # Close the driver after each successful scrape
        driver.quit()
        driver = None
        
        # Sleep for 3 seconds between scrapes
        print(f"Waiting 3 seconds before next scrape...")
        time.sleep(3)
        
    except KeyboardInterrupt:
        print("Scraping stopped by user.")
        if driver:
            try:
                driver.quit()
            except:
                pass
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if driver:
            try:
                driver.quit()
            except:
                pass
        # Wait before retrying
        print("Waiting 5 seconds before retrying...")
        time.sleep(5)



