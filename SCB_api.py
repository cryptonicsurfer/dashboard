import requests
import pandas as pd

# URL
url = 'https://api.scb.se/OV0104/v1/doris/sv/ssd/START/PR/PR0101/PR0101A/KPItotM'

# Request body
data = {
    "query": [
        {
            "code": "ContentsCode",
            "selection": {
                "filter": "item",
                "values": ["000004VU"]
            }
        }
    ],
    "response": {
        "format": "json"
    }
}

# Make the POST request
response = requests.post(url, json=data)
response_data = response.json()

# Extract data and convert to dataframe
data_list = response_data['data']

# Process the data to convert to desired format
processed_data = []
for item in data_list:
    date_str = item['key'][0]
    year = date_str[:4]
    month = date_str[5:7]
    formatted_date = f"{year}-{month}-01"  # Using the first day of the month
    value = item['values'][0]
    processed_data.append([formatted_date, year, value])

df = pd.DataFrame(processed_data, columns=['date', 'year', 'value'])

print(df)
