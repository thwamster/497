import os
import time

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_KEY = "25a2e5c93d7c029c48c56d18bfefeb111fd77abd"
base_dir = r"./data"
years = range(2010, 2024)
df_list = []

session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

print("Started.")

for year in years:
    print(f"Year: {year}")

    if year < 2019:
        url = f"https://api.census.gov/data/{year}/zbp?get=ESTAB,EMP,PAYANN&for=zipcode:*&key={API_KEY}"
    else:
        url = f"https://api.census.gov/data/{year}/cbp?get=ESTAB,EMP,PAYANN&for=zip%20code:*&key={API_KEY}"

    try:
        response = session.get(url, timeout=45)

        if response.status_code == 200:
            headers, *rows = response.json()
            df = pd.DataFrame(rows, columns=headers)
            df['Year'] = year

            df = df.rename(columns={"zipcode": "Zip Code", "zip code": "Zip Code"})
            df_list.append(df)
        else:
            print(f"Error Code: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(2)

if df_list:
    ca_zbp = pd.concat(df_list, ignore_index=True)
    ca_prefixes = ('90', '91', '92', '93', '94', '95', '96')
    ca_zbp = ca_zbp[ca_zbp['Zip Code'].astype(str).str.startswith(ca_prefixes)].copy()

    ca_zbp = ca_zbp.rename(columns={
        "ESTAB": "ZBP_Total_Establishments",
        "EMP": "ZBP_Total_Employees",
        "PAYANN": "ZBP_Annual_Payroll_Thousands"
    })

    metrics = ["ZBP_Total_Establishments", "ZBP_Total_Employees", "ZBP_Annual_Payroll_Thousands"]
    ca_zbp[metrics] = ca_zbp[metrics].apply(pd.to_numeric, errors='coerce')

    os.makedirs(base_dir, exist_ok=True)

    output_path = os.path.join(base_dir, "Census-CA-ZBP.2013-2023.csv")
    ca_zbp[['Zip Code', 'Year'] + metrics].to_csv(output_path, index=False)
    print("Success.")
else:
    print("Error.")

print("Ended.")
