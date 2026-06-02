import pandas as pd

input_path = r"./data/Master-CA-Opioid.2010-2024.csv"
output_path = r"./data/Master-CA-Opioid.2010-2024.Extrema.csv"

print("Started.")

try:
    df = pd.read_csv(input_path)

    summary_data = []

    for col in df.columns:
        dtype_str = str(df[col].dtype)

        clean_col = df[col].dropna()

        if clean_col.empty:
            min_val = pd.NA
            max_val = pd.NA
        else:
            try:
                min_val = clean_col.min()
                max_val = clean_col.max()
            except TypeError:
                clean_col_str = clean_col.astype(str)
                min_val = clean_col_str.min()
                max_val = clean_col_str.max()

        summary_data.append({
            'variable_name': col,
            'variable_type': dtype_str,
            'value_minimum': min_val,
            'value_maximum': max_val
        })

    summary_df = pd.DataFrame(summary_data)

    summary_df.to_csv(output_path, index=False)
    print("Success.")

except Exception as e:
    print(f"Error: {e}")

print("Ended.")
