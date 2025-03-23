import pandas as pd
import numpy as np
import re

CSV_INPUT = 'ebay_tech_deals.csv'
CSV_OUTPUT = 'cleaned_ebay_deals.csv'

def read_csv_file(file_path):
    return pd.read_csv(file_path)

def clean_currency_column(series):
    def clean_value(val):
        if pd.isna(val):
            return val
        if isinstance(val, str):
            val = re.sub(r'[^\d.-]', '', val.strip())
            return val if val else None
        return val
    return series.apply(clean_value)

def handle_shipping_info(df):
    df['shipping'] = df['shipping'].fillna('').astype(str).str.strip()
    missing_shipping = (df['shipping'].isin(["", "N/A"]) | df['shipping'].isna())
    df.loc[missing_shipping, 'shipping'] = "Shipping info unavailable"
    return df

def compute_discount(df):
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['original_price'] = pd.to_numeric(df['original_price'], errors='coerce')
    df['discount_percentage'] = np.where(
        (df['original_price'].notna()) & (df['original_price'] != 0),
        ((1 - df['price'] / df['original_price']) * 100).round(2),
        np.nan
    )
    return df

def fill_missing_original_prices(df):
    df['original_price'] = df['original_price'].fillna(df['price'])
    return df

def clean_and_process_data(df):
    df['price'] = clean_currency_column(df['price'])
    df['original_price'] = clean_currency_column(df['original_price'])
    df = fill_missing_original_prices(df)
    df = handle_shipping_info(df)
    df = compute_discount(df)
    df = df.dropna(subset=['title', 'price', 'original_price'])
    return df

def save_clean_data(df, output_file):
    df.to_csv(output_file, index=False)

def main():
    data = read_csv_file(CSV_INPUT)
    cleaned_data = clean_and_process_data(data)
    save_clean_data(cleaned_data, CSV_OUTPUT)
    print(f"Cleaned data saved to {CSV_OUTPUT}")

if __name__ == "__main__":
    main()
