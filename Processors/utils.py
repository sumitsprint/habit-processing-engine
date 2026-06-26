import pandas as pd
from fastapi import UploadFile
import os


os.makedirs("temp", exist_ok=True)

#  Save uploaded file
async def save_file(file: UploadFile):
    file_path = os.path.join("temp", file.filename)
    with open(file_path, "wb") as buffer:
        chunk = await file.read(1024)
        while chunk:
            buffer.write(chunk)
            chunk = await file.read(1024)
    return file_path


# load data
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

# clean dates

def parse_dates(date_series):
    
    
    date_series = date_series.dropna().astype(str).str.replace("-", "/")
    sample_date = date_series.iloc[0]
    parts = sample_date.split("/")

    if len(parts[0]) == 4:  # Year is first
        return pd.to_datetime(date_series, format="%Y/%m/%d")
    elif len(parts[2]) == 4:  # Year is last
        return pd.to_datetime(date_series, format="%d/%m/%Y")
    else:
        raise ValueError("Unknown date format")















 


 




