# Purpose

The numerical processing pipeline processes numerical habits exported from the Loop Habit Tracker app.

Numerical habits are measureable habits where the user has to achieve a target value within a fixed number of days. For example, running 10 kilometers every seven days or brushing twice every day.

The purpose of this pipeline is to process numerical habit data and evaluate the user's progress toward the defined target.

## Exported Data

A numerical habit exported from the Loop Habit Tracker app can contain four possible states:

- **Numerical Value** – A user-recorded progress value for that day.
- **NO** – The user recorded no progress for that day. This state is interpreted as a value of zero during processing.
- **SKIP** – The user intentionally skipped the habit for that day.
- **UNKNOWN** – No information is available for that day.

The Loop Habit Tracker stores numerical values as scaled integers. For example, a value of `1.0` is stored as `1000`, and a value of `1.5` is stored as `1500`. These values are normalized to their original scale during processing.

## Design Decisions

### Why is timeline reconstruction necessary?

Numerical habits require the user to achieve a target value within a fixed number of days. Therefore, the evaluation of a numerical habit depends on evaluating these recurring fixed periods, which the pipeline represents as evaluation windows.

The exported dataset may be sparse. It may contain missing calendar dates and only the days on which the user recorded an entry.

Therefore, the exported dataset cannot be evaluated directly. The timeline is first reconstructed into a continuous sequence of calendar days, with newly reconstructed dates initially assigned the UNKNOWN state, so that every evaluation window contains a complete representation of its time period.

### Why is normalization necessary?

The Loop Habit Tracker stores numerical values as integers scaled by a factor of 1000. In addition, the exported dataset represents zero progress using the `NO` state.

Before evaluation, the data is normalized by converting the scaled integers back to their original numerical values and interpreting `NO` as `0`.

After normalization, the pipeline operates on three states:

- **Numerical Value** – User-recorded progress.
- **SKIP** – The user intentionally skipped the habit.
- **UNKNOWN** – No information is available for that day.

### Step 3 – Extract Evaluation Windows

The frequency denominator from the metadata defines the length of each evaluation window. Starting from the first engagement entry (the first engagement entry is used because the dataset may contain leading `UNKNOWN` entries, which are not relevant), the pipeline partitions the reconstructed timeline into consecutive windows, each spanning the number of days specified by the frequency denominator.

However, the window boundaries are not always final after the initial extraction. If a window contains SKIP entries, it may need to be extended before it can be evaluated.

### Diagram

Timeline
─────────────────────────────────────────────────────────────►

Window 1               Window 2               Window 3
[───────7 days───────] [───────7 days───────] [───────7 days───────]

### Step 4 – Window Semantics

Before a window can be evaluated, the pipeline must determine whether its boundaries are final.

The pipeline distinguishes between two kinds of evaluation windows:

- Windows without `SKIP` entries.
- Windows containing `SKIP` entries.

Windows without `SKIP` entries already have fixed boundaries and can be evaluated immediately.

Windows containing `SKIP` entries may require additional processing. A `SKIP` entry represents an intentionally skipped opportunity and should not affect the user's performance metrics. Therefore, a skipped day must be compensated by extending the evaluation window, giving the user another opportunity to contribute toward the target.

However, extension is not always necessary. The pipeline first checks whether the cumulative progress within the window has already reached the target value. If the target has already been achieved, no extension is performed because the evaluation result cannot change.

Otherwise, if the window contains one or more `SKIP` entries and the target has not yet been reached, the window becomes eligible for extension.

The `skip_triggered_extension` algorithm performs this extension. It repeatedly extends the window by the number of newly discovered `SKIP` entries. If the newly added portion also contains `SKIP` entries, the process repeats. This cascading extension continues until no additional `SKIP` entries are discovered.

### Diagram

NORMAL WINDOW
7 days ──────────────────────────► Final boundaries
No SKIP                           → Evaluate


WINDOW WITH SKIP
7 days ──────────────────────────► SKIP detected
                                      │
                                      ▼
                              Target reached?
                               /          \
                             YES           NO
                              │             │
                         Success      Extend window
                                            │
                                            ▼
                                      Check new days
                                            │
                                      More SKIP?
                                       /       \
                                     YES       NO
                                      │         │
                                  Extend     Final boundaries
                                      │         │
                                      └────────► Evaluate

### Step 5 – Window Evaluation

Once the boundaries of an evaluation window have been finalized, the pipeline evaluates the window using the `determine_window_status` function.

The evaluation follows a deterministic sequence of rules:

1. If the cumulative progress is greater than or equal to the target value, the window is classified as **SUCCESS**.
2. Otherwise, if the window contains one or more `UNKNOWN` entries, the window is classified as **UNRESOLVED** because the missing information cannot be interpreted.
3. Otherwise, the window is classified as **FAILURE**.

This evaluation logic is applied to every finalized evaluation window, including windows whose boundaries were extended by the `skip_triggered_extension` process.

### Step 6 – Window Objects

After a window has been evaluated, the pipeline creates a window object containing the evaluation result together with the metadata associated with that window.

Each window object stores information such as:

- Window number.
- Window start date.
- Window end date.
- Evaluation result.
- Extension metadata (if the window was extended).
- Skipped dates.
- Other metadata required for downstream processing.

The evaluated window object is appended to a collection of window objects.

Once all windows have been evaluated, this collection becomes the foundation for computing behavioral context and performance metrics.
