import csv
import os
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from flask import Flask, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Setup Selenium WebDriver
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    return webdriver.Chrome(options=options)

# URL of the page
url = "https://www.5paisa.com/commodity-trading/mcx-aluminium-price"

def get_contract_months():
    today = datetime.today()
    contract_months = {}
    
    for i in range(3):
        future_date = today.replace(day=1) + timedelta(days=32 * i)  # Jump to next month
        future_date = future_date.replace(day=30)  # Always set to the 30th
        month_year_str = future_date.strftime("%B %d %Y")  # Format: "April 30 2025"
        xpath = f"//input[@name='toggle-comm' and contains(@value, '{future_date.month}-30-{future_date.year}')]"
        contract_months[month_year_str] = xpath
    
    return contract_months

contract_months = get_contract_months()

# CSV filename
csv_filename = "scraped_csv/mcx_aluminium_prices.csv"

# Ensure directory exists
os.makedirs(os.path.dirname(csv_filename), exist_ok=True)

def extract_data():
    driver = get_driver()
    driver.get(url)
    try:
        # Extract date & time
        date_time_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "commodity-page__date"))
        )
        date_time_text = date_time_element.text.replace("As on ", "").strip()
        date_obj = datetime.strptime(date_time_text, "%d %B, %Y | %H:%M")
        date_str, time_str = date_obj.strftime("%Y-%m-%d"), date_obj.strftime("%H:%M")
        
        row_data = {"date": date_str, "time": time_str, "prices": {}}
        
        # Extract contract prices and rate changes
        for month, xpath in contract_months.items():
            try:
                radio_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                driver.execute_script("arguments[0].click();", radio_button)
                time.sleep(3)  # Allow time for the price to update

                price_element = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "commodity-page__value"))
                )
                price = price_element.text.strip().replace("₹", "")
                
                rate_element = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "commodity-page__percentage"))
                )
                rate_change = rate_element.text.strip()
                
                row_data["prices"][month] = {"price": price, "rate_change": rate_change}
            except Exception:
                row_data["prices"][month] = {"price": "N/A", "rate_change": "N/A"}
        
        driver.quit()
        save_to_csv(row_data)
        return row_data
    except Exception as e:
        driver.quit()
        return {"error": str(e)}

def save_to_csv(data):
    headers = ["Date", "Time"] + list(contract_months.keys())
    row = [data["date"], data["time"]] + [f'{data["prices"][month]["price"]} ({data["prices"][month]["rate_change"]})' for month in contract_months]
    
    file_exists = os.path.exists(csv_filename)
    with open(csv_filename, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)

# Background scraper thread
def scraper_thread():
    while True:
        print("\n🚀 Scraping started!")
        extract_data()
        print("✅ Data scraped and saved.")
        time.sleep(10)  # Scrape every 5 minutes

@app.route("/scrape", methods=["GET"])
def scrape():
    data = extract_data()
    return jsonify(data)

@app.route("/download", methods=["GET"])
def download_csv():
    if os.path.exists(csv_filename):
        return send_file(csv_filename, as_attachment=True)
    return jsonify({"error": "CSV file not found"}), 404

if __name__ == "__main__":
    thread = threading.Thread(target=scraper_thread, daemon=True)
    thread.start()
    app.run(debug=True, port=5000)











# # Alternative code to scrape and save data without Flask

# import csv
# import os
# import time
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from datetime import datetime, timedelta

# # Setup Selenium WebDriver
# options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(options=options)

# # URL of the page
# url = "https://www.5paisa.com/commodity-trading/mcx-aluminium-price"
# driver.get(url)

# # Wait for page to load fully
# driver.implicitly_wait(5)

# # Generate the next 3 contract months dynamically, always ending on the 30th
# def get_contract_months():
#     today = datetime.today()
#     contract_months = {}
    
#     for i in range(3):
#         future_date = today.replace(day=1) + timedelta(days=32 * i)  # Jump to the next month
#         future_date = future_date.replace(day=30)  # Always set to the 30th
#         month_year_str = future_date.strftime("%B %d %Y")  # Format: "April 30 2025"
#         xpath = f"//input[@name='toggle-comm' and contains(@value, '{future_date.month}-30-{future_date.year}')]"
#         contract_months[month_year_str] = xpath
    
#     return contract_months

# contract_months = get_contract_months()

# # CSV filename
# csv_filename = "scaped_csv/mcx_aluminium_prices.csv"

# # Read existing CSV data to check headers
# existing_data = []
# if os.path.exists(csv_filename):
#     with open(csv_filename, "r", newline="", encoding="utf-8") as file:
#         reader = csv.reader(file)
#         existing_data = list(reader)

# # Extract existing headers (if file exists)
# headers = existing_data[0] if existing_data else ["Date"]

# # Function to extract price after clicking the contract month radio button
# def extract_price(month, xpath):
#     try:
#         # Wait for the radio button to be present
#         radio_button = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, xpath))
#         )

#         # Scroll into view and click
#         driver.execute_script("arguments[0].scrollIntoView();", radio_button)
#         driver.execute_script("arguments[0].click();", radio_button)

#         # Small delay to allow price update
#         time.sleep(3)

#         # Wait until the price is visible
#         price_element = WebDriverWait(driver, 10).until(
#             EC.visibility_of_element_located((By.CLASS_NAME, "commodity-page__value"))
#         )

#         # Extract price text
#         price = price_element.text.strip().replace("₹", "")
#         return price

#     except Exception as e:
#         print(f"❌ Error extracting data for {month}: {e}")
#         return None  # Return None if extraction fails

# # Get today's date
# today_date = datetime.today().strftime("%Y-%m-%d")

# # Extract prices for each month
# row_data = [today_date]
# new_headers = ["Date"]
# for month, xpath in contract_months.items():
#     price = extract_price(month, xpath)
#     row_data.append(price if price else "N/A")
#     new_headers.append(month)

# # Merge new headers with existing ones
# for header in new_headers:
#     if header not in headers:
#         headers.append(header)

# os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
# # Open CSV in append mode
# with open(csv_filename, mode="a", newline="", encoding="utf-8") as file:
#     writer = csv.writer(file)

#     # Write header if the file is empty
#     if not existing_data:
#         writer.writerow(headers)

#     # Append new row
#     writer.writerow(row_data)

# print(f"\n📁 Data successfully saved to {csv_filename}")

# # Close the driver
# driver.quit()





# import csv
# import os
# import time
# import threading
# import logging
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from datetime import datetime, timedelta
# from flask import Flask, jsonify, send_file
# from flask_cors import CORS

# # Setup logging
# logging.basicConfig(level=logging.INFO, 
#                     format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# app = Flask(__name__)
# CORS(app)

# # Setup Selenium WebDriver with improved error handling
# def get_driver():
#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless=new")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--window-size=1920,1080")  # Set window size
    
#     # Additional options to avoid detection
#     options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option("useAutomationExtension", False)
    
#     for attempt in range(3):
#         try:
#             logger.info(f"Initializing WebDriver (Attempt {attempt+1}/3)")
#             # Use specific ChromeDriver version if needed
#             # service = Service(ChromeDriverManager(version="114.0.5735.90").install())
#             service = Service(ChromeDriverManager().install())
#             driver = webdriver.Chrome(service=service, options=options)
            
#             # Execute CDP commands to avoid detection
#             driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#                 "source": """
#                 Object.defineProperty(navigator, 'webdriver', {
#                     get: () => undefined
#                 })
#                 """
#             })
            
#             logger.info("WebDriver initialized successfully")
#             return driver
#         except Exception as e:
#             logger.error(f"WebDriver Error (Attempt {attempt+1}/3): {str(e)}")
#             time.sleep(2)
    
#     raise Exception("Failed to initialize WebDriver after multiple attempts")

# # URL of the page
# url = "https://www.5paisa.com/commodity-trading/mcx-aluminium-price"

# def get_contract_months():
#     today = datetime.today()
#     contract_months = {}

#     for i in range(3):
#         future_date = today.replace(day=1) + timedelta(days=32 * i)
#         future_date = future_date.replace(day=30)
#         month_year_str = future_date.strftime("%B %d %Y")
        
#         # Improved XPath with more flexibility
#         xpath = f"//input[@name='toggle-comm' and contains(@value, '{future_date.month}-') and contains(@value, '{future_date.year}')]"
#         contract_months[month_year_str] = xpath

#     logger.info(f"Generated contract months: {contract_months}")
#     return contract_months

# contract_months = get_contract_months()

# # CSV filename
# csv_filename = "scraped_csv/mcx_aluminium_prices.csv"

# # Ensure directory exists
# os.makedirs(os.path.dirname(csv_filename), exist_ok=True)

# def extract_data():
#     driver = None
#     try:
#         logger.info("Starting data extraction")
#         driver = get_driver()
        
#         # Add explicit wait before loading the page
#         driver.get(url)
#         logger.info(f"Navigated to URL: {url}")
        
#         # Take screenshot for debugging
#         screenshot_path = "debug_screenshot.png"
#         driver.save_screenshot(screenshot_path)
#         logger.info(f"Saved debug screenshot to {screenshot_path}")
        
#         # Wait for page to fully load
#         WebDriverWait(driver, 15).until(
#             EC.presence_of_element_located((By.TAG_NAME, "body"))
#         )
#         time.sleep(3)  # Additional wait for dynamic content
        
#         try:
#             # Extract date & time with improved error handling
#             date_time_element = WebDriverWait(driver, 15).until(
#                 EC.visibility_of_element_located((By.CLASS_NAME, "commodity-page__date"))
#             )
#             date_time_text = date_time_element.text.replace("As on ", "").strip()
#             logger.info(f"Extracted date/time text: '{date_time_text}'")
            
#             try:
#                 date_obj = datetime.strptime(date_time_text, "%d %B, %Y | %H:%M")
#             except ValueError:
#                 # Try alternative format if the first fails
#                 date_obj = datetime.strptime(date_time_text, "%d %b, %Y | %H:%M")
            
#             date_str, time_str = date_obj.strftime("%Y-%m-%d"), date_obj.strftime("%H:%M")
#         except Exception as e:
#             logger.error(f"Error extracting date/time: {str(e)}")
#             date_str, time_str = datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M")
            
#         row_data = {"date": date_str, "time": time_str, "prices": {}}
        
#         # Print page source for debugging
#         logger.debug(f"Page source: {driver.page_source[:500]}...")  # First 500 chars
        
#         # Extract contract prices and rate changes
#         for month, xpath in contract_months.items():
#             try:
#                 logger.info(f"Attempting to extract data for contract month: {month}")
                
#                 # Find radio button with more robust approach
#                 try:
#                     radio_button = WebDriverWait(driver, 10).until(
#                         EC.element_to_be_clickable((By.XPATH, xpath))
#                     )
#                     logger.info(f"Found radio button for {month}")
#                 except Exception as e:
#                     logger.warning(f"Could not find radio button with original XPath for {month}: {str(e)}")
#                     # Try alternative XPath
#                     month_num = datetime.strptime(month.split()[0], "%B").month
#                     year = month.split()[2]
#                     alt_xpath = f"//input[contains(@value, '{month_num}') and contains(@value, '{year}')]"
#                     radio_button = WebDriverWait(driver, 10).until(
#                         EC.element_to_be_clickable((By.XPATH, alt_xpath))
#                     )
                
#                 # Click with JavaScript as it's more reliable
#                 driver.execute_script("arguments[0].click();", radio_button)
#                 logger.info(f"Clicked on radio button for {month}")
#                 time.sleep(3)  # Wait for data to load
                
#                 # Extract price with more robust approach
#                 try:
#                     price_element = WebDriverWait(driver, 10).until(
#                         EC.visibility_of_element_located((By.CLASS_NAME, "commodity-page__value"))
#                     )
#                     price = price_element.text.strip().replace("₹", "")
#                 except Exception as e:
#                     logger.warning(f"Error finding price with original selector: {str(e)}")
#                     # Try alternative selector
#                     price_element = driver.find_element(By.XPATH, "//div[contains(@class, 'value') and contains(text(), '₹')]")
#                     price = price_element.text.strip().replace("₹", "")
                
#                 logger.info(f"Extracted price for {month}: {price}")
                
#                 # Extract rate change with more robust approach
#                 try:
#                     rate_element = WebDriverWait(driver, 10).until(
#                         EC.visibility_of_element_located((By.CLASS_NAME, "commodity-page__percentage"))
#                     )
#                     rate_change = rate_element.text.strip()
#                 except Exception as e:
#                     logger.warning(f"Error finding rate change with original selector: {str(e)}")
#                     # Try alternative selector
#                     rate_element = driver.find_element(By.XPATH, "//div[contains(@class, 'percentage')]")
#                     rate_change = rate_element.text.strip()
                
#                 logger.info(f"Extracted rate change for {month}: {rate_change}")
                
#                 row_data["prices"][month] = {"price": price, "rate_change": rate_change}
#             except Exception as e:
#                 logger.error(f"Error extracting data for {month}: {str(e)}")
#                 row_data["prices"][month] = {"price": "N/A", "rate_change": "N/A"}
        
#         save_to_csv(row_data)
#         logger.info("Data extraction completed successfully")
#         return row_data
#     except Exception as e:
#         logger.error(f"Error in extract_data: {str(e)}")
#         return {"error": str(e)}
#     finally:
#         if driver:
#             driver.quit()
#             logger.info("WebDriver closed")

# def save_to_csv(data):
#     try:
#         headers = ["Date", "Time"] + list(contract_months.keys())
#         row = [data["date"], data["time"]] + [f'{data["prices"][month]["price"]} ({data["prices"][month]["rate_change"]})' for month in contract_months]
        
#         file_exists = os.path.exists(csv_filename)
#         with open(csv_filename, "a", newline="", encoding="utf-8") as file:
#             writer = csv.writer(file)
#             if not file_exists:
#                 writer.writerow(headers)
#             writer.writerow(row)
#         logger.info(f"Data saved to CSV: {csv_filename}")
#     except Exception as e:
#         logger.error(f"Error saving to CSV: {str(e)}")

# # Background scraper thread
# def scraper_thread():
#     while True:
#         try:
#             logger.info("Starting scheduled scraping")
#             extract_data()
#             logger.info("Scheduled scraping completed")
#         except Exception as e:
#             logger.error(f"Error in scheduled scraping: {str(e)}")
        
#         # Wait for next scraping
#         time.sleep(3600)  # Scrape every hour instead of every 10 seconds

# @app.route("/3_months_LME", methods=["GET"])
# def scrape():
#     try:
#         logger.info("API scrape endpoint called")
#         data = extract_data()
#         return jsonify(data)
#     except Exception as e:
#         logger.error(f"Error in API scrape endpoint: {str(e)}")
#         return jsonify({"error": str(e)}), 500

# @app.route("/download", methods=["GET"])
# def download_csv():
#     try:
#         logger.info("API download endpoint called")
#         if os.path.exists(csv_filename):
#             return send_file(csv_filename, as_attachment=True)
#         logger.warning("CSV file not found")
#         return jsonify({"error": "CSV file not found"}), 404
#     except Exception as e:
#         logger.error(f"Error in API download endpoint: {str(e)}")
#         return jsonify({"error": str(e)}), 500

# @app.route("/", methods=["GET"])
# def home():
#     return """
#     <html>
#         <head>
#             <title>MCX Aluminium Price Scraper</title>
#             <style>
#                 body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
#                 .container { max-width: 800px; margin: 0 auto; }
#                 h1 { color: #333; }
#                 .btn { display: inline-block; background: #4CAF50; color: white; padding: 10px 15px; 
#                        text-decoration: none; border-radius: 4px; margin-right: 10px; }
#                 .info { background: #f8f8f8; padding: 15px; border-radius: 4px; margin-top: 20px; }
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <h1>MCX Aluminium Price Scraper</h1>
#                 <p>Use the buttons below to access the scraper functionality:</p>
#                 <a href="/3_months_LME" class="btn">Scrape Latest Data</a>
#                 <a href="/download" class="btn">Download CSV</a>
                
#                 <div class="info">
#                     <h3>API Endpoints:</h3>
#                     <ul>
#                         <li><strong>/3_months_LME</strong> - Scrape latest MCX Aluminium prices</li>
#                         <li><strong>/download</strong> - Download the CSV with all scraped data</li>
#                     </ul>
#                 </div>
#             </div>
#         </body>
#     </html>
#     """

# if __name__ == "__main__":
#     # Create a dedicated thread for background scraping
#     if os.environ.get("ENABLE_BACKGROUND_SCRAPING", "false").lower() == "true":
#         thread = threading.Thread(target=scraper_thread, daemon=True)
#         thread.start()
#         logger.info("Background scraping thread started")
    
#     # Run the Flask app
#     port = int(os.environ.get("PORT", 5002))
#     logger.info(f"Starting Flask app on port {port}")
#     app.run(host="0.0.0.0", debug=False, port=port)
