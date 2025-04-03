

from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

CSV_FILE_PATH_SBI = "scraped_csv/sbitt.csv"

# Function to scrape SBI TT Sell rate
def scrape_sbi_tt_sell():
    url = "https://officialforexrates.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        data = []

        if table:
            thead = table.find("thead")
            if thead:
                date_row = thead.find("tr")
                date_cells = date_row.find_all("th")
                Date = date_cells[1].text.strip() if len(date_cells) > 0 else "N/A"
            else:
                Date = "N/A"

            tbody = table.find("tbody")
            if tbody:
                rows = tbody.find_all("tr")
                for row in rows[:1]:  # Get first row
                    columns = row.find_all("td")
                    sbi_tt_sell = columns[1].text.strip() if len(columns) > 1 else "N/A"
                    data.append({"date": Date, "sbi_tt_sell": sbi_tt_sell})

            # Save to CSV
            df = pd.DataFrame(data)
            os.makedirs("scraped_csv", exist_ok=True)
            write_header = not os.path.exists(CSV_FILE_PATH_SBI)
            df.to_csv(CSV_FILE_PATH_SBI, mode="a", index=False, header=write_header)

            return data
        else:
            return None
    return None

# API route to get SBI TT Sell rate
@app.route('/scrape-sbi-tt', methods=['GET'])
def get_sbi_tt_sell():
    data = scrape_sbi_tt_sell()
    
    if data:
        return jsonify({"success": True, "data": data, "message": "SBI TT Sell rate scraped successfully"})
    else:
        return jsonify({"error": "Failed to scrape data or table not found"}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)  # Change port to 5001



    
# import os
# import requests
# from bs4 import BeautifulSoup
# import pandas as pd

# # URL of the website
# url = "https://officialforexrates.com/"

# # Headers to avoid blocking
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
# }

# # Send GET request
# r = requests.get(url, headers=headers)

# # Check if request is successful
# if r.status_code == 200:
#     # Parse HTML content
#     soup = BeautifulSoup(r.text, "html.parser")

#     # Find the table
#     table = soup.find("table")
#     data = []

#     if table:
#         # Extract Date from <thead>
#         thead = table.find("thead")
#         if thead:
#             date_row = thead.find("tr")
#             date_cells = date_row.find_all("th")

#             if len(date_cells) > 0:  # Ensure there is at least one <th>
#                 Date = date_cells[1].text.strip()
#             else:
#                 Date = "N/A"
#         else:
#             Date = "N/A"

#         # Extract SBI TT Sell from <tbody> (2nd column)
#         tbody = table.find("tbody")
#         if tbody:
#             rows = tbody.find_all("tr")  # Get all rows

#             for row in rows[:1]:  # Get first 3 rows
#                 columns = row.find_all("td")  # Get all columns in the row

#                 if len(columns) > 2:  # Ensure the 3rd column exists
#                     sbi_tt_sell = columns[1].text.strip()
#                 else:
#                     sbi_tt_sell = "N/A"

#                 data.append([Date, sbi_tt_sell])

#     # Convert to DataFrame and save as CSV
#     df = pd.DataFrame(data, columns=["Date", "SBI TT Sell"])
#     write_header = not os.path.exists("sbitt.csv")  # Write header only if file does not exist

#     df.to_csv("scraped_csv/sbitt.csv", mode = "a" , index=False, header=write_header)

#     print("Scraping completed! Data saved to 'scraped_csv/sbitt.csv'.")
# else:
#     print(f"Failed to fetch the page. Status Code: {r.status_code}")


