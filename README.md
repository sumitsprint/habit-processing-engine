# Habit Processing Engine

A FastAPI backend application that processes CSV exports
from the Loop Habit Tracker app and returns simple behavioral insights
and performance metrics by analyzing the user's habit data.

This project started from a simple idea:
process my own real-world workout data exported from Loop Habit Tracker App.

## Supported Habit Types

The engine supports two categories of habits: binary habits and numerical habits.
Since these habit types have fundamentally different evaluation requirements,
the project uses two independent processing pipelines,
each designed specifically for its respective habit type.

### Binary Habits

Binary habits are simple yes/no habits where the user
either performs the habit or does not perform it in a fixed time period.

Examples:

- a particular workout (every 7 days)
- Meditation (every day)

### Numerical Habits

Numerical habits measure progress toward a target value within a fixed number of days.

Examples:

- Run 10 km every week
- Read 100 pages every month
- Drink 3.5 liters of water every day

## Processing Pipelines

### Binary Habit Processing

The binary pipeline processes binary (yes/no) habits.

Its responsibilities include:

- Reconstructing sparse habit data into a complete daily timeline.
- Calculating performance metrics such as consistency and streaks.
- Extracting behavioral context, including when the user first started the habit, their most recent interaction,
  and periods of disengagement.

### Numerical Habit Processing

The numerical pipeline processes target-based habits.

Its responsibilities include:

- Reconstructing sparse habit data into a complete daily timeline.
- Normalizing progress values into a consistent representation.
- Evaluating progress over fixed evaluation periods based on the habit frequency.
- Calculating performance metrics such as consistency and streaks.
- Extracting behavioral context, including when the user first started the habit, their most recent interaction,
  and periods of disengagement.

## Project Structure

```text
.
├── main.py                      # FastAPI application
├── utils.py                     # Shared utility functions
├── requirements.txt
│
├── Processors/
│   ├── __init__.py
│   ├── binary_processing.py     # Binary habit processing
│   └── numerical_processing.py  # Numerical habit processing
│
├── Sample_Datasets/
│   ├── binary(Mon - evening) L-sit.csv
│   ├── Meta.csv
│   ├── numerical(Brush).csv
│   └── numerical(Daily Reading).csv
│
└── README.md
```

## Tech Stack

- Python
- Pandas
- FastAPI

---

## Status

The project currently implements binary and numerical habit processing
through two independent processing pipelines and serves as a portfolio project
demonstrating data processing and API development with FastAPI.

For detailed information about the architecture, processing pipelines, and design decisions, see the [Documentation](./docs/).

Future enhancements may be added as the project evolves.
