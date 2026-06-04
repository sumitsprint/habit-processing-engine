import pandas as pd

# load data
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

# clean dates

def parse_dates(date_series):
    
    
    date_series = date_series.dropna().astype(str).str.replace("-", "/")
    sample_date = str(date_series.iloc[0])
    parts = sample_date.split("/")

    if len(parts[0]) == 4:  # Year is first
        return pd.to_datetime(date_series, format="%Y/%m/%d")
    elif len(parts[2]) == 4:  # Year is last
        return pd.to_datetime(date_series, format="%d/%m/%Y")
    else:
        raise ValueError("Unknown date format")















 


 




