# Binary Habit Fields Glossary (`YES_NO`)

### Behavior Context
- `habit_name`: The exact database name of the habit.
- `habit_type`: "YES_NO" (makes a distinction between numerical habit and binary habit) 
- `frequency_denominator`: Fixed number of days in which user is supposed to perform the habit (e.g., 7 means scheduled once every 7 days).
- `first_active_entry`: The date and outcome of the user's very first decisive interaction with the habit (`YES_MANUAL` or `NO`).
- `latest_engagement_entry`: The date and outcome of the most recent engagement (`YES_MANUAL`, `NO`, or `SKIP`).
- `disengagement_periods`: Lists of consecutive intentional SKIP entries, showing when the user took deliberate breaks. Includes start and end dates, and the date and outcome of the next decisive interaction (`YES_MANUAL` or `NO`). If `next_decisive_date` is null, the deliberate break is currently ongoing.


### Metrics
- `total_decisive_days`: Count of scheduled days where the user either performed the habit `YES_MANUAL` or failed `NO`. Excludes SKIP and non-scheduled days (`YES_AUTO`).
- `total_yes`: Count of scheduled days successfully marked `YES_MANUAL` (total no. of days where user successfully performed the habit).
- `total_failures`: Count of scheduled days marked `NO` (total no. of days where user failed to performed the habit).
- `consistency`: Percentage score: `(total_yes / total_decisive_days) * 100`.
- `Longest_streak`: Longest consecutive run of scheduled days marked `YES_MANUAL`, including start and end dates.
- `current_streak`: Number of consecutive recent scheduled days marked `YES_MANUAL` 



