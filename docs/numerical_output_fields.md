# Numerical Habit Fields Glossary (`NUMERICAL`)

### timeline

- **`timeline`** (`list[str]`): complete timeline of habit formatted as 'DD-MM-YYYY: VALUE' starting from the first engagement date.

### Behavior Context

- `habit_name`: The exact database name of the habit.
- `habit_type`: "NUMERICAL" (makes a distinction between numerical habits and binary habits).
- `frequency_denominator`: Number of days in which user has to achieve the target value, (supposedly Length of each evaluation window in days (e.g., 1 for daily, 7 for weekly)).
- `target_value`: The cumulative numeric target required to pass each window.
- `first_active_entry`: Date and numeric value of the first recorded active entry.
- `latest_engagement_entry`: Date and numeric value of the latest recorded engagement with the habit.
- `total_windows`: Total number of evaluation windows constructed across the timeline.
- `latest_complete_window_status`: evaluation result of last complete window in timeline (there may be a partial window in timeline)
  - `1`: user achieved the target in the most recently completed window.
  - `0`: user failed to achieve the target in the most recently completed window.

- `unresolved_window_count`: Windows containing `UNKNOWN` where the target wasn't met. These are excluded from consistency calculations, not penalized as failures.
- `partial_window`: If true, the final window is still active/ongoing and has not yet reached `frequency_denominator` days. The pipeline treats it as a partial window, making the second-to-last window the (latest complete window) `latest_complete_window_status`. Do not interpret incomplete cumulative values in an active partial window as a failure or streak break.
- `extended_windows_count`: Windows where intentional `SKIP` entries occurred, triggering an extension to the window to give additional days to reach the target.
- `normal_windows_count`: Standard windows completed without needing skip-triggered extensions.
- `success_window_count`: Total completed windows where the sum reached or exceeded `target_value`.
- `failure_window_count`: Total completed windows that closed without meeting `target_value`.

### Metrics

- `Consistency`: Percentage score: `(success_window_count / (total_windows - unresolved_window_count)) * 100`.
- `Longest_Streak`: Highest number of consecutive successful windows where user achieved the target value, with start and end dates.
- `Current_Streak`: Number of consecutive successful windows leading up to the last completed window.
