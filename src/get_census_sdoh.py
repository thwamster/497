import os
import time

import pandas as pd
import requests

API_KEY = "25a2e5c93d7c029c48c56d18bfefeb111fd77abd"
base_dir = r"./data"

variables = {
    "B01003_001E": "Total Population",
    "B01002_001E": "Median Age",
    "B02001_002E": "Pop: White Alone",
    "B02001_003E": "Pop: Black or African American",
    "B02001_004E": "Pop: American Indian and Alaska Native",
    "B02001_005E": "Pop: Asian",
    "B03002_012E": "Pop: Hispanic or Latino",
    "B19013_001E": "Median Household Income",
    "B19083_001E": "Income Inequality: Gini Index",
    "B17001_001E": "Poverty: Total Pop Universe",
    "B17001_002E": "Poverty: Pop Below Poverty Level",
    "B23025_003E": "Employment: Civilian Labor Force",
    "B23025_005E": "Employment: Unemployed",
    "B22003_001E": "SNAP: Total Households",
    "B22003_002E": "SNAP: Households Receiving SNAP",
    "B19057_001E": "Public Assistance: Total Households",
    "B19057_002E": "Public Assistance: Receiving Cash Assistance",
    "B15003_001E": "Education: Pop 25+ Universe",
    "B15003_002E": "Education: No Schooling Completed",
    "B15003_017E": "Education: High School Diploma",
    "B15003_022E": "Education: Bachelor's Degree",
    "B25003_001E": "Housing: Total Occupied Units",
    "B25003_002E": "Housing: Owner Occupied",
    "B25003_003E": "Housing: Renter Occupied",
    "B25064_001E": "Housing: Median Gross Rent",
    "B25047_001E": "Plumbing: Total Units",
    "B25047_003E": "Plumbing: Lacking Complete Plumbing",
    "B08201_001E": "Vehicles: Total Households",
    "B08201_002E": "Vehicles: No Vehicle Available",
    "B28002_001E": "Internet: Total Households",
    "B28002_013E": "Internet: No Internet Access",
    "B08301_001E": "Commute: Total Workers 16+",
    "B08301_010E": "Commute: Public Transportation",
    "B05002_013E": "Social: Foreign Born Population",
    "B11001_001E": "Households: Total Universe",
    "B11001_006E": "Households: Female Single-Parent with Kids",
    "B11001_008E": "Households: Living Alone",
    "B27010_001E": "Health Insurance: Total Population",
    "B27010_017E": "Health Insurance: Under 19 Uninsured",
    "B27010_033E": "Health Insurance: 19 to 34 Uninsured",
    "B27010_050E": "Health Insurance: 35 to 64 Uninsured"
}

years = range(2012, 2025)
df_list = []

print("Started.")

for year in years:
    print(f"Year: {year}")
    req_vars = [
        k for k in variables
        if not (year < 2017 and k in ["B28002_001E", "B28002_013E"])
           and not (year < 2013 and k in ["B27010_001E", "B27010_017E", "B27010_033E", "B27010_050E"])
    ]

    url = f"https://api.census.gov/data/{year}/acs/acs5?get={','.join(req_vars)}&for=zip%20code%20tabulation%20area:*&key={API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        headers, *rows = response.json()
        df = pd.DataFrame(rows, columns=headers)
        df['Year'] = year
        df_list.append(df)
    else:
        print(f"Error Code {response.status_code}: {response.text[:100]}")

    time.sleep(1)

master_demo_df = pd.concat(df_list, ignore_index=True)
master_demo_df = master_demo_df.rename(columns={"zip code tabulation area": "Zip Code"})
ca_prefixes = ('90', '91', '92', '93', '94', '95', '96')
ca_demo_df = master_demo_df[master_demo_df['Zip Code'].str.startswith(ca_prefixes)].copy()
ca_demo_df = ca_demo_df.rename(columns=variables)
demo_columns = list(variables.values())
ca_demo_df[demo_columns] = ca_demo_df[demo_columns].apply(pd.to_numeric, errors='coerce')
output_path = os.path.join(base_dir, "Census-CA-SDOH.2012-2024.csv")
ca_demo_df.to_csv(output_path, index=False)

print("Ended.")
