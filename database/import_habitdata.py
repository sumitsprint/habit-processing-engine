import os
import pandas as pd
import psycopg
from pathlib import Path
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parent.parent / ".env")

database_url = os.getenv("EXTERNAL_DATABASE_URL")

raw_df = pd.read_csv(r"Sample_Datasets\Checkmarks.csv")

with psycopg.connect(database_url) as connection:

    # Fetch all habit IDs once
    rows = connection.execute(
        "SELECT habit_id, name FROM habit_metadata"
    ).fetchall() # returns a list of tuples (habit_id, name)

    habit_ids = {}

    for habit_id, name in rows:
        habit_ids[name] = habit_id

    # Collect valid records in Python
    records = []

    for _, row in raw_df.iterrows():
        date = row["Date"]

        for habit_name in raw_df.columns[1:]:
            value = row[habit_name]

            if pd.isna(value): # skip NaN values
                continue

            if habit_name not in habit_ids:
                print(
                    f"Warning: '{habit_name}' not found in habit_metadata. Skipping."
                )
                continue

            records.append(
                (habit_ids[habit_name], date, str(value))
            )

    print(f"Prepared {len(records)} records for import.")

    # Insert records in batches
    with connection.cursor() as cursor:
        for start in range(0, len(records), 500):
            batch = records[start:start + 500]

            cursor.executemany(
                """
                INSERT INTO habit_data (habit_id, date, value)
                VALUES (%s, %s, %s)
                ON CONFLICT (habit_id, date) DO NOTHING
                """,
                batch # tuple by tuple insertion
            )

            print(
                f"Processed {min(start + 500, len(records))}"
                f" of {len(records)} records."
            )

print("Habit data imported successfully!")
