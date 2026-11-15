from Processors.binary_processing import reconstruct_timeline_binary, create_state_views, build_behavior_context, calculate_binary_metrics
from Processors.numerical_processing import reconstruct_timeline, normalise_numerical_states, extract_windows, build_api_response, calculate_numerical_metrics
import pandas as pd


#processing pipelines
def process_habit(meta_df, raw_df, habit_name):
    if habit_name:
        meta_row = meta_df[meta_df["Name"] == habit_name]
        if meta_row.empty:
            return {"error": "Habit not found in Meta.csv"}
        row = meta_row.iloc[0] #series representing that row to access scalar
        habit_type = row["Type"]  

        # binary habit processing
        if row["Type"] == "YES_NO":
            frequency_denominator = int(row['FrequencyDenominator'])
            
            timeline_df, first_engagement_index = reconstruct_timeline_binary(raw_df, frequency_denominator)
            post_anchor_df, _, engagement_df, active_df = create_state_views(timeline_df, first_engagement_index)
            metrics = calculate_binary_metrics(active_df)
            behavior_context = build_behavior_context(habit_name, habit_type, frequency_denominator, engagement_df, active_df )
            
            #unpacking is position based not name based

        #numerical habit processing
        elif row["Type"] == "NUMERICAL":
            if row["Target Type"] != "AT_LEAST":
                return {"error": "only AT_LEAST target type is supported for NUMERICAL habits"}
            target_value = float(row["Target Value"])
            frequency_denominator = int(row['FrequencyDenominator'])
            
            timeline_df = reconstruct_timeline(raw_df)
            normalise_df = normalise_numerical_states(timeline_df)
            windows = extract_windows(normalise_df, frequency_denominator, target_value)
            behavior_context, success_window_count, unresolved_window_count = build_api_response(windows, normalise_df, frequency_denominator, target_value, habit_name, habit_type)
            metrics = calculate_numerical_metrics(windows, success_window_count, unresolved_window_count)


        else:
            return {"error": "Unsupported habit type"}

    if row["Type"] == "YES_NO":
        timeline_strings = (post_anchor_df["Date"].dt.strftime("%d-%m-%Y") + ": " + post_anchor_df["Value"].astype(str))
    else:
        engagement_mask = ~normalise_df["Value"].isin(["UNKNOWN"])
        if not engagement_mask.any():
            return {"error": "No engagement entries found"}
        first_engagement_index = normalise_df[engagement_mask].index[0]
        normalise_df = normalise_df.iloc[first_engagement_index:] # filter out leading unknowns
        timeline_strings = (normalise_df["Date"].dt.strftime("%d-%m-%Y") + ": " + normalise_df["Value"].astype(str))    
           
    return {
            "timeline": timeline_strings.tolist(),
            "behavior_context": behavior_context, 
            "metrics": metrics
            }