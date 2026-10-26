
import os
import pandas as pd
import psycopg
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

df = pd.read_csv(r"Sample_Datasets\Meta.csv")

database_url = os.getenv("EXTERNAL_DATABASE_URL")

with psycopg.connect(database_url) as connection:
    for i in range(len(df)):
        row = df.iloc[i]

        # Insert the row into the habit_metadata table, INSERT  describes columns
        connection.execute(
            """
            INSERT INTO habit_metadata (
                position, name, type, question, description,  
                frequency_numerator, frequency_denominator,
                color, unit, target_type, target_value, archived
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (name) DO NOTHING
            """,
            (
                row["Position"], row["Name"], row["Type"],
                row["Question"], row["Description"],
                row["FrequencyNumerator"], row["FrequencyDenominator"],
                row["Color"], row["Unit"], row["Target Type"],
                row["Target Value"], row["Archived?"]
            )
        )

print("Metadata imported successfully!")
