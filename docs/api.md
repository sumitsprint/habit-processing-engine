# API

## Endpoint

**POST /upload**

Processes a CSV export from the Loop Habit Tracker application and returns behavioral context and performance metrics for a specified habit.

---

## Response Overview

The API response contains two main categories of information:

### Performance Metrics

Performance metrics provide quantitative measurements of the user's habit performance, such as consistency, streaks, and other metrics calculated by the appropriate processing pipeline.

### Behavioral Context

Behavioral context provides information about the user's interaction with the habit over time, such as the active period of the habit and other behavioral patterns identified from the processed data.

## Request

The endpoint requires two inputs:

### 1. CSV File

A CSV file exported from the Loop Habit Tracker application.

### 2. Habit Name

The name of the habit to be analyzed.

### Why is the habit name required?

The uploaded CSV file contains only the raw habit data and does not identify which habit the data belongs to. Therefore, the user must provide the habit name explicitly.

The application uses the habit name to retrieve the corresponding metadata. This metadata determines:

- The habit type (Binary or Numerical).
- The frequency denominator.
- For numerical habits, the target value and Target Type.

Based on the identified habit type, the application routes the DataFrame to the appropriate processing pipeline.

---

## Supported Habit Types

### Binary Habits

Supported.

### Numerical Habits

Currently, the project supports only the **At Least** target type.

---

## Processing Flow

1. Receive the uploaded CSV file and habit name.
2. Load the CSV into a Pandas DataFrame.
3. Retrieve the corresponding metadata using the habit name.
4. Determine the habit type.
5. Route the DataFrame to the appropriate processing pipeline.
6. Process the habit data.
7. Return the computed behavioral context and performance metrics as a JSON response.

---

## Response

The endpoint returns a JSON response containing:

- Behavioral context.
- Performance metrics.
