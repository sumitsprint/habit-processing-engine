import pandas as pd
from fastapi import UploadFile
import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv


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
    
    
    date_series = date_series.dropna().astype(str).str.replace("-", "/") #str is the string accessor just like dt
    sample_date = date_series.iloc[0]
    parts = sample_date.split("/")

    if len(parts[0]) == 4:  # Year is first
        return pd.to_datetime(date_series, format="%Y/%m/%d")
    elif len(parts[2]) == 4:  # Year is last
        return pd.to_datetime(date_series, format="%d/%m/%Y")
    else:
        raise ValueError("Unknown date format")


# fetch data from database
load_dotenv()
DATABASE_URL = os.getenv("EXTERNAL_DATABASE_URL")


def fetch_habit_data(habit_name: str):
    if not DATABASE_URL:
        raise ValueError("EXTERNAL_DATABASE_URL is missing from .env")

    with psycopg.connect(DATABASE_URL) as connection:
        meta_query = """
            SELECT
                name AS "Name",
                type AS "Type",
                frequency_denominator AS "FrequencyDenominator", 
                target_type AS "Target Type",
                target_value AS "Target Value"
            FROM habit_metadata
            WHERE name = %s
        """

        meta_rows = connection.execute(meta_query, (habit_name,)).fetchall() # comma makes it a tuple

        meta_df = pd.DataFrame(
            meta_rows,
            columns=[
                "Name",
                "Type",
                "FrequencyDenominator",
                "Target Type",
                "Target Value",
            ],
        )

        habit_query = """
            SELECT
                date AS "Date",
                value AS "Value"
            FROM habit_data
            WHERE habit_id = (
                SELECT habit_id
                FROM habit_metadata
                WHERE name = %s
            )
            ORDER BY date
        """

        habit_rows = connection.execute(habit_query, (habit_name,)).fetchall()

        raw_df = pd.DataFrame(
            habit_rows,
            columns=["Date", "Value"]
        )

    return meta_df, raw_df    



        























 


 




