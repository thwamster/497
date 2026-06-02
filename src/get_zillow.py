import os

import pandas as pd

base_dir = r"./data"
os.makedirs(base_dir, exist_ok=True)

zillow_datasets = {
    "zhvi_mid_tier": "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "zhvi_bottom_tier": "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.0_0.33_sm_sa_month.csv",
    "zhvi_top_tier": "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.67_1.0_sm_sa_month.csv",
    "zori_rent_index": "https://files.zillowstatic.com/research/public_csvs/zori/Zip_zori_uc_sfrcondomfr_sm_sa_month.csv",
    "zhvi_sfr_only": "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfr_tier_0.33_0.67_sm_sa_month.csv",
    "zhvi_condo_only": "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_condo_tier_0.33_0.67_sm_sa_month.csv",
    "zhvi_1_bed": "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_bdrmcnt_1_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "zhvi_3_bed": "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_bdrmcnt_3_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "zhvi_5plus_bed": "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_bdrmcnt_5_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
    "perc_listings_price_cut": "https://files.zillowstatic.com/research/public_csvs/perc_listings_price_cut/Zip_perc_listings_price_cut_uc_sfrcondo_sm_month.csv",
    "med_listings_price_cut_perc": "https://files.zillowstatic.com/research/public_csvs/med_listings_price_cut_perc/Zip_med_listings_price_cut_perc_uc_sfrcondo_sm_month.csv",
    "med_doz_pending": "https://files.zillowstatic.com/research/public_csvs/med_doz_pending/Zip_med_doz_pending_uc_sfrcondo_sm_month.csv",
    "market_temp_index": "https://files.zillowstatic.com/research/public_csvs/market_temp_index/Zip_market_temp_index_uc_sfrcondo_month.csv",
    "pct_sold_above_list": "https://files.zillowstatic.com/research/public_csvs/pct_sold_above_list/Zip_pct_sold_above_list_uc_sfrcondo_sm_month.csv",
    "pct_sold_below_list": "https://files.zillowstatic.com/research/public_csvs/pct_sold_below_list/Zip_pct_sold_below_list_uc_sfrcondo_sm_month.csv",
    "median_sale_to_list": "https://files.zillowstatic.com/research/public_csvs/median_sale_to_list/Zip_median_sale_to_list_uc_sfrcondo_sm_month.csv",
    "for_sale_inventory": "https://files.zillowstatic.com/research/public_csvs/invt_fs/Zip_invt_fs_uc_sfrcondo_sm_month.csv",
    "new_listings": "https://files.zillowstatic.com/research/public_csvs/new_listings/Zip_new_listings_uc_sfrcondo_sm_month.csv"
}

print("Started.")

compiled_matrix = None

for metric_name, url in zillow_datasets.items():
    try:
        df = pd.read_csv(url)
        state_col = [c for c in df.columns if c.lower() in ['state', 'statename']][0]
        region_col = [c for c in df.columns if c.lower() in ['regionname', 'zipcode']][0]
        df = df[df[state_col].astype(str).str.upper() == 'CA'].copy()
        df['Zip Code'] = df[region_col].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(5)
        date_cols = [c for c in df.columns if c.startswith('20')]
        df_melt = df.melt(id_vars=['Zip Code'], value_vars=date_cols, var_name='Date', value_name=metric_name)
        df_melt['Year'] = df_melt['Date'].str[:4].astype(int)
        df_melt = df_melt[(df_melt['Year'] >= 2010) & (df_melt['Year'] <= 2024)]
        annual_avg = df_melt.groupby(['Zip Code', 'Year'])[metric_name].mean().round(2).reset_index()

        if compiled_matrix is None:
            compiled_matrix = annual_avg
        else:
            compiled_matrix = pd.merge(compiled_matrix, annual_avg, on=['Zip Code', 'Year'], how='outer')

    except Exception as e:
        print(f"Error: {e} for {metric_name}")

if compiled_matrix is not None:
    output_path = os.path.join(base_dir, "Zillow-CA.2010-2024.csv")
    compiled_matrix.to_csv(output_path, index=False)
    print("Success.")
else:
    print("Error.")

print("Ended.")
