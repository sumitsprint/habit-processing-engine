import os
import psycopg
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


database_url = os.getenv("EXTERNAL_DATABASE_URL")

with psycopg.connect(database_url) as connection:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS habit_metadata (
            habit_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            position INTEGER,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            question TEXT,
            description TEXT,
            frequency_numerator INTEGER NOT NULL
                CHECK (frequency_numerator > 0),
            frequency_denominator INTEGER NOT NULL
                CHECK (frequency_denominator > 0),
            color TEXT,
            unit TEXT,
            target_type TEXT,
            target_value REAL,
            archived BOOLEAN NOT NULL DEFAULT FALSE
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS habit_data (
            habit_id INTEGER NOT NULL REFERENCES habit_metadata(habit_id) ON DELETE CASCADE,
            date TEXT NOT NULL,
            value TEXT,
            PRIMARY KEY (habit_id, date)
        )
    """)

print("PostgreSQL tables created successfully!")