import os
import time

import pandas as pd

base_dir = r"./data"
years = range(2013, 2024)
df_list = []

print("Started.")

for year in years:
    yy = str(year)[2:]
    url = f"https://www.irs.gov/pub/irs-soi/{yy}zpallnoagi.csv"
    print(f"Year: {year}.")

    try:
        df = pd.read_csv(url, encoding='latin-1')
        df.columns = df.columns.str.upper()
        df = df[df['STATE'] == 'CA'].copy()
        df['ZIPCODE'] = pd.to_numeric(df['ZIPCODE'], errors='coerce')
        df = df[df['ZIPCODE'].notna() & (df['ZIPCODE'] > 0) & (df['ZIPCODE'] < 99999)]
        df['Zip Code'] = df['ZIPCODE'].astype(int).astype(str).str.zfill(5)
        target_metrics = {
            'N1': 'IRS_Total_Tax_Returns',
            'N2': 'IRS_Total_Individuals_Count',
            'NUMDEP': 'IRS_Dependents_Count',
            'PREP': 'IRS_Paid_Preparer_Returns_Count',
            'MARS1': 'IRS_Single_Returns_Count',
            'MARS2': 'IRS_Joint_Returns_Count',
            'MARS4': 'IRS_Head_Of_Household_Returns_Count',
            'A00100': 'IRS_Adjusted_Gross_Income',
            'N00200': 'IRS_Salaries_Wages_Returns_Count',
            'A00200': 'IRS_Salaries_Wages_Dollars',
            'N00300': 'IRS_Taxable_Interest_Returns_Count',
            'A00300': 'IRS_Taxable_Interest_Dollars',
            'N00900': 'IRS_Business_Income_Returns_Count',
            'A00900': 'IRS_Business_Income_Dollars',
            'N01000': 'IRS_Capital_Gains_Returns_Count',
            'A01000': 'IRS_Capital_Gains_Dollars',
            'N01400': 'IRS_IRA_Distributions_Returns_Count',
            'A01400': 'IRS_IRA_Distributions_Dollars',
            'N01700': 'IRS_Pensions_Annuities_Returns_Count',
            'A01700': 'IRS_Pensions_Annuities_Dollars',
            'N02300': 'IRS_Unemployment_Returns_Count',
            'A02300': 'IRS_Unemployment_Compensation_Dollars',
            'N02500': 'IRS_Social_Security_Benefits_Returns_Count',
            'A02500': 'IRS_Social_Security_Benefits_Dollars',
            'N10500': 'IRS_Earned_Income_Credit_Returns_Count',
            'A10500': 'IRS_Earned_Income_Credit_Dollars',
            'N07180': 'IRS_Child_Tax_Credit_Returns_Count',
            'A07180': 'IRS_Child_Tax_Credit_Dollars',
            'N10960': 'IRS_Refundable_Child_Tax_Credit_Returns_Count',
            'A10960': 'IRS_Refundable_Child_Tax_Credit_Dollars',
            'N04470': 'IRS_Itemized_Deductions_Returns_Count',
            'A04470': 'IRS_Itemized_Deductions_Dollars',
            'N11901': 'IRS_Tax_Owed_At_Filing_Returns_Count',
            'A11901': 'IRS_Tax_Owed_At_Filing_Dollars',
            'N11902': 'IRS_Refund_Returns_Count',
            'A11902': 'IRS_Refund_Dollars'
        }
        valid_cols = {k: v for k, v in target_metrics.items() if k in df.columns}
        df = df[['Zip Code'] + list(valid_cols.keys())].copy()
        df[list(valid_cols.keys())] = df[list(valid_cols.keys())].apply(pd.to_numeric, errors='coerce')
        zip_totals = df.groupby('Zip Code').sum().reset_index()
        zip_totals = zip_totals.rename(columns=valid_cols)
        zip_totals['Year'] = year
        df_list.append(zip_totals)

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(1)

if df_list:
    ca_irs = pd.concat(df_list, ignore_index=True)

    core_cols = ['Zip Code', 'Year']
    ca_irs = ca_irs[core_cols + [c for c in ca_irs.columns if c not in core_cols]]

    output_path = os.path.join(base_dir, "IRS-CA-SOI.2013-2023.csv")
    ca_irs.to_csv(output_path, index=False)
    print("Success.")
else:
    print("Error.")

print("Ended    .")
