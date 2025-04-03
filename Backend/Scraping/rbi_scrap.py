

from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

CSV_FILE_PATH = "scraped_csv/rbi_reference_rates.csv"

# Function to scrape data
def scrape_rbi_rates():
    url = "https://www.msei.in/markets/currency/historical-data/rbireferenceratearchives"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")

        data = []
        if table:
            rows = table.find_all("tr")
            for row in rows[:3]:  # Extract first 3 rows
                columns = row.find_all("td")
                if len(columns) > 2:
                    date = columns[0].text.strip()
                    rate = columns[1].text.strip()
                    data.append({"date": date, "rate": rate})

            # # Convert to DataFrame
            # df = pd.DataFrame(data)

            # # Ensure the directory exists
            # os.makedirs("scraped_csv", exist_ok=True)

            # # Check if file exists to write the header only once
            # write_header = not os.path.exists(CSV_FILE_PATH)

            # # Append data to CSV
            # df.to_csv(CSV_FILE_PATH, mode="a", index=False, header=write_header)

            return data
        else:
            return None
    return None

# API route to fetch & store data
@app.route('/scrape', methods=['GET'])
def get_rbi_rates():
    data = scrape_rbi_rates()
    if data:
        return jsonify({"success": True, "data": data, "message": "Data scraped and saved to CSV"})
    else:
        return jsonify({"error": "Failed to scrape data or table not found"}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)




# Alternartive code to scrape and save data without Flask
# # This code is a standalone script to scrape RBI reference rates and save them to a CSV file.    
# import os
# import requests
# from bs4 import BeautifulSoup
# import pandas as pd

# # URL of the RBI reference rate page
# url = "https://www.msei.in/markets/currency/historical-data/rbireferenceratearchives"

# # Headers to avoid being blocked
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
# }

# # Send GET request
# r = requests.get(url, headers=headers)

# # Check if request is successful
# if r.status_code == 200:
#     # Parse the HTML content
#     soup = BeautifulSoup(r.text, "html.parser")

#     # print(soup.prettify())

#     # Find the table
#     table = soup.find("table")

#     # Extract table data
#     data = []
#     if table:
#         rows = table.find_all("tr")
        
#         for row in rows[:3]:
#             columns = row.find_all("td")

#             if len(columns) > 2:
#                 column_1 = columns[0].text.strip()
#                 column_2 = columns[1].text.strip()
                
#                 data.append([column_1, column_2])
            
#         # for row in rows:
#         #     columns = row.find_all("td")
#         #     # if len(columns) > 2:  # Ensure there are enough columns
#         #     # data.append(columns[0].text.strip() )  # Extract only column 2 (Index 1)
#         #     data.append([col.text.strip() for col in columns])
#     else :
#         print("Table not found")          
#     # Convert to DataFrame and save as CSV
#     os.makedirs("scraped_csv", exist_ok=True)
#     df = pd.DataFrame(data, columns=["Date", "Rbi Reference Rate"])
#     write_header = not os.path.exists("scraped_csv/rbi_reference_rates.csv")  # Write header only if file does not exist

#     df.to_csv("scraped_csv/rbi_reference_rates.csv", mode="a", index=False, header=write_header)
    
#     print("Scraping completed! Data saved to 'rbi_reference_rates.csv'.")
# else:
#     print(f"Failed to fetch the page. Status Code: {r.status_code}")
