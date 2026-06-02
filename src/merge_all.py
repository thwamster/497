import os
import re
from functools import reduce

import pandas as pd

base_dir = r"./data"


def to_snake_case(s):
    s = str(s).lower()
    s = re.sub(r'[^a-z0-9]+', '_', s)
    return s.strip('_')


def clean_geo_code(series, pad_length=5):
    return series.astype(str).str.replace(r'\.0$', '', regex=True) \
        .apply(lambda x: x.zfill(pad_length) if x.lower() != 'nan' and x != '' else pd.NA)


print("Started.")

df_cosd = pd.read_csv(os.path.join(base_dir, "COSD-Opioid.2010-2024.csv"))
df_cosd = df_cosd.rename(columns={'Zip Code': 'zip_code', 'Year': 'year'})
df_cosd['zip_code'] = clean_geo_code(df_cosd['zip_code'])
df_cosd['Full FIPS'] = clean_geo_code(df_cosd['Full FIPS'])
stability_map = {
    'Rate is unstable interpret with caution': 'unstable',
    'Rate is stable': 'stable',
    'Rate may be unstable': 'potentially_unstable',
    'Not applicable': 'not_applicable'
}
stability_cols = ['Death_Stability', 'ED_Stability', 'Hosp_Stability', 'Rx_Stability']

for col in stability_cols:
    if col in df_cosd.columns:
        df_cosd[col] = df_cosd[col].astype(str).str.strip().map(stability_map).fillna(df_cosd[col])

df_irs = pd.read_csv(os.path.join(base_dir, "IRS-CA-SOI.2013-2023.csv"))
df_irs = df_irs.rename(columns={'Zip Code': 'zip_code', 'Year': 'year'})
df_irs['zip_code'] = clean_geo_code(df_irs['zip_code'])
ca_zips = set(df_cosd['zip_code']).union(set(df_irs['zip_code']))
df_sdoh = pd.read_csv(os.path.join(base_dir, "Census-CA-SDOH.2012-2024.csv"))

if 'state' in df_sdoh.columns:
    df_sdoh = df_sdoh.drop(columns=['state'])

df_sdoh = df_sdoh.rename(columns={'Zip Code': 'zip_code', 'Year': 'year'})
df_sdoh = df_sdoh.replace([-666666666.0, -888888888.0, -999999999.0, -222222222.0, -333333333.0], pd.NA)
df_sdoh['zip_code'] = clean_geo_code(df_sdoh['zip_code'])
df_sdoh = df_sdoh[df_sdoh['zip_code'].isin(ca_zips)]
df_zbp = pd.read_csv(os.path.join(base_dir, "Census-CA-ZBP.2013-2023.csv"))
df_zbp = df_zbp.rename(columns={'Zip Code': 'zip_code', 'Year': 'year'})
df_zbp['zip_code'] = clean_geo_code(df_zbp['zip_code'])
df_zbp = df_zbp[df_zbp['zip_code'].isin(ca_zips)]
df_zhvi = pd.read_csv(os.path.join(base_dir, "Zillow-CA.2010-2024.csv"))
df_zhvi = df_zhvi.rename(columns={'Zip Code': 'zip_code', 'Year': 'year'})
df_zhvi['zip_code'] = clean_geo_code(df_zhvi['zip_code'])
df_zhvi = df_zhvi[df_zhvi['zip_code'].isin(ca_zips)]

df_mdcr = pd.read_csv(os.path.join(base_dir, "OMT-MDCR-GEO.2013-2023.csv"), low_memory=False)
df_mdcr = df_mdcr[(df_mdcr['Prscrbr_Geo_Lvl'] == 'ZIP') &
                  (df_mdcr['Breakout_Type'] == 'Totals') &
                  (df_mdcr['Breakout'] == 'Overall')].copy()
df_mdcr = df_mdcr[df_mdcr['Prscrbr_Geo_Desc'].astype(str).str.contains(r'\bCA\b|California', case=False, na=False)]
df_mdcr = df_mdcr.rename(columns={'Prscrbr_Geo_Cd': 'zip_code', 'Year': 'year'})
df_mdcr['zip_code'] = clean_geo_code(df_mdcr['zip_code'])
df_mdcr = df_mdcr[df_mdcr['zip_code'].isin(ca_zips)]
df_mdcr = df_mdcr.drop(columns=['Prscrbr_Geo_Lvl', 'Prscrbr_Geo_Desc', 'RUCA_Cd', 'Breakout_Type', 'Breakout'])
df_mdcr = df_mdcr.rename(columns={c: f"Medicare_{c}" for c in df_mdcr.columns if c not in ['zip_code', 'year']})
dataframes = [df_cosd, df_sdoh, df_zbp, df_irs, df_mdcr, df_zhvi]

for df in dataframes:
    df['year'] = df['year'].astype(int)

master_df = reduce(lambda left, right: pd.merge(left, right, on=['zip_code', 'year'], how='outer'), dataframes)
master_df.columns = [to_snake_case(c) for c in master_df.columns]
known_geos = master_df.dropna(subset=['county', 'full_fips']).drop_duplicates('zip_code')
county_map = dict(zip(known_geos['zip_code'], known_geos['county']))
fips_map = dict(zip(known_geos['zip_code'], known_geos['full_fips']))
master_df['county'] = master_df['zip_code'].map(county_map)
master_df['full_fips'] = master_df['zip_code'].map(fips_map)
master_df = master_df.sort_values('zip_code')
master_df['county'] = master_df['county'].ffill().bfill()
master_df['full_fips'] = master_df['full_fips'].ffill().bfill()
master_df['state'] = 'California'
id_cols = ['state', 'county', 'full_fips', 'zip_code', 'year']
id_cols = [c for c in id_cols if c in master_df.columns]
data_cols = [c for c in master_df.columns if c not in id_cols]
master_df = master_df[id_cols + data_cols]
master_df = master_df.sort_values(by=['zip_code', 'year']).reset_index(drop=True)
output_path = os.path.join(base_dir, "Master-CA-Opioid.2010-2024.csv")
master_df.to_csv(output_path, index=False)

print("Finished.")
