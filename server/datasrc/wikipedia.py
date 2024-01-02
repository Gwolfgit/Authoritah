import requests
from bs4 import BeautifulSoup
import json


def fetch_table_data(url):
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the table
    table = soup.find("table", class_="wikitable sortable jquery-tablesorter")

    # Extract column headers
    column_headers = [th.text.strip() for th in table.find("thead").find_all("th")]

    # Extract rows
    data_rows = []
    for tr in table.find("tbody").find_all("tr"):
        row_data = {}
        for td, th in zip(tr.find_all("td"), column_headers):
            row_data[th] = td.text.strip()
        data_rows.append(row_data)

    return data_rows


def main():
    # URL of the page containing the table
    url = "YOUR_URL_HERE"  # Replace with the actual URL

    # Fetch table data
    table_data = fetch_table_data(url)

    # Convert table data to JSON
    json_data = json.dumps(table_data, indent=4)

    # Output the JSON data
    print(json_data)


if __name__ == "__main__":
    main()
