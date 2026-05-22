# Habit Processing Engine

A backend processing engine for evaluating and interpreting habit-tracker datasets.

This project started from a simple idea:
process my own real-world workout data exported from Loop Habit Tracker App.

While building it, the project gradually evolved into a deeper system-design exercise around:

- behavioral state interpretation
- uncertainty handling
- temporal window evaluation
- engagement analysis
- habit evaluation semantics

The goal is not just to process habit data, but to think carefully about what the data actually means.

---

# Current Features

## Binary Habit Processing

- binary metrics calculation
- behavior context extraction
- first active entry detection
- latest active entry detection
- disengagement period detection
- contiguous skip grouping

## Numerical Habit Processing

- timeline reconstruction
- fixed-window evaluation engine
- adaptive skip-based window extension
- UNKNOWN-aware evaluation logic
- SUCCESS / FAILURE / UNRESOLVED classification

---

# Key Design Ideas

Some of the core ideas currently being explored in this project:

- separating SKIP from UNKNOWN semantics
- uncertainty-aware evaluation
- fixed calendar windows
- behavioral context vs performance metrics
- state-based processing logic
- temporal evaluation systems

---

# Project Structure

```text
main.py
    → API orchestration layer

processors/
    ├── binary_processing.py
    ├── numerical_processing.py
    └── utils.py
    
```

# Tech Stack

- Python
- Pandas
- FastAPI

---

# Status

This project is actively evolving.

The architecture, semantics, and evaluation logic are still being refined while working with real-world habit datasets and edge cases.