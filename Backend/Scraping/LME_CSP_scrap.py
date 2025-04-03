import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Al_cash"

# Headers to avoid being blocked
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

# Send GET request
r = requests.get(url, headers=headers)

if r.status_code ==200:
    # Parse the HTML content
    soup = BeautifulSoup(r.text, "html.parser")

# Find the table
    table = soup.find("table")

    # Extract table data
    data = []
    if table:
        tbody = table.find("tbody")

        if tbody:
            rows = tbody.find_all("tr")
            for row in rows[:1]:
                columns = row.find_all("td")
            if len(columns) > 1:
                Date = columns[0].text.strip()
                LME_Aluminium_Cash = columns[1].text.strip()
                data.append([Date, LME_Aluminium_Cash])

    df = pd.DataFrame(data, columns=["Date", "LME_Aluminium_Cash"])
    write_header = not os.path.exists("scraped_csv/LME_Aluminium_Cash.csv")  # Write header only if file does not exist
    df.to_csv("scraped_csv/LME_CSP_Scarp.csv", mode="a", index=False, header=write_header)

    print("Scraping completed! Data saved to 'scraped_csv/LME_Aluminium_Cash.csv'.") 

else:
    print(f"Failed to fetch the page. Status Code: {r.status_code}")          