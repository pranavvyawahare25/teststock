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