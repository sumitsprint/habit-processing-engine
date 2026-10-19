
import sqlite3

connection = sqlite3.connect("habits.db")

connection.execute("""
    CREATE TABLE IF NOT EXISTS habit_metadata (
        habit_id INTEGER PRIMARY KEY,
        position INTEGER,
        name TEXT NOT NULL UNIQUE,
        type TEXT NOT NULL,
        question TEXT,
        description TEXT,
        frequency_numerator INTEGER,
        frequency_denominator INTEGER,
        color TEXT,
        unit TEXT,
        target_type TEXT,
        target_value REAL,
        archived INTEGER
    )
""")

connection.execute("""
    CREATE TABLE IF NOT EXISTS habit_data (

        habit_id INTEGER,
        Date TEXT NOT NULL,
        Value TEXT,
        PRIMARY KEY (habit_id, Date) 
)
""")

connection.close()










