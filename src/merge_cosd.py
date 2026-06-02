import glob
import os
from functools import reduce

import pandas as pd

base_dir = r"./data"

folders = {
    "Death": "All_Any Opioid-Related Overdose_Death_by Zip Code_2010-2024_06.01.2026",
    "ED": "All_Any Opioid-Related Overdose_ED Visit_by Zip Code_2010-2024_06.01.2026",
    "Hosp": "All_Any Opioid-Related Overdose_Hosp_by Zip Code_2010-2024_06.01.2026",
    "Rx": "All_Opioid Prescriptions by Patient LocationbyZip Code_2010-2024_06.01.2026"
}

ca_fips_dict = {
    "Alameda": "001", "Alpine": "003", "Amador": "005", "Butte": "007", "Calaveras": "009",
    "Colusa": "011", "Contra Costa": "013", "Del Norte": "015", "El Dorado": "017", "Fresno": "019",
    "Glenn": "021", "Humboldt": "023", "Imperial": "025", "Inyo": "027", "Kern": "029",
    "Kings": "031", "Lake": "033", "Lassen": "035", "Los Angeles": "037", "Madera": "039",
    "Marin": "041", "Mariposa": "043", "Mendocino": "045", "Merced": "047", "Modoc": "049",
    "Mono": "051", "Monterey": "053", "Napa": "055", "Nevada": "057", "Orange": "059",
    "Placer": "061", "Plumas": "063", "Riverside": "065", "Sacramento": "067", "San Benito": "069",
    "San Bernardino": "071", "San Diego": "073", "San Francisco": "075", "San Joaquin": "077",
    "San Luis Obispo": "079", "San Mateo": "081", "Santa Barbara": "083", "Santa Clara": "085",
    "Santa Cruz": "087", "Shasta": "089", "Sierra": "091", "Siskiyou": "093", "Solano": "095",
    "Sonoma": "097", "Stanislaus": "099", "Sutter": "101", "Tehama": "103", "Trinity": "105",
    "Tulare": "107", "Tuolumne": "109", "Ventura": "111", "Yolo": "113", "Yuba": "115"
}


def process_folder(prefix, folder_name):
    files = glob.glob(os.path.join(base_dir, folder_name, "*.csv"))
    if not files:
        return pd.DataFrame()

    df_list = []
    for f in files:
        if "(1).csv" in f:
            continue

        county, *_, year, _ = os.path.basename(f).split('_')

        try:
            df = pd.read_csv(f, skiprows=2)
            df = df[df['Zip Code'].astype(str).str.isnumeric()].copy()
            df['Zip Code'] = df['Zip Code'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(5)
            df['County'], df['Year'] = county, int(year)
            df = df.rename(columns={c: f"{prefix}_{c}" for c in df.columns if c not in ['Zip Code', 'Year', 'County']})
            df_list.append(df)
        except:
            pass

    return pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()


print("Started.")

df_death = process_folder("Death", folders["Death"])
df_ed = process_folder("ED", folders["ED"])
df_hosp = process_folder("Hosp", folders["Hosp"])
df_rx = process_folder("Rx", folders["Rx"])

dataframes = [df for df in [df_death, df_ed, df_hosp, df_rx] if not df.empty]

if dataframes:
    master_df = reduce(lambda l, r: pd.merge(l, r, on=['Zip Code', 'Year', 'County'], how='outer'), dataframes)
    master_df['State'] = 'CA'
    master_df['Full FIPS'] = '06' + master_df['County'].map(ca_fips_dict).fillna("000")
    cols = ['Zip Code', 'Year', 'County', 'State', 'Full FIPS']
    master_df = master_df[cols + [c for c in master_df.columns if c not in cols]]
    out_path = os.path.join(base_dir, "COSD-Opioid.2010-2024.csv")
    master_df.to_csv(out_path, index=False)

    print("Success.")
else:
    print("Error.")

print("Ended.")
