#raw_df 
#  | 
#  | ----metrics pipeline, 
#  | ----behavior pipeline

import pandas as pd
from Processors.utils import parse_dates



def reconstruct_timeline_binary(raw_df, frequency_denominator):
    raw_df = raw_df.copy()

    #after filtering pandas sometimes returns a view and sometimes a new df 
    # the behavior is not always obvious
    raw_df = raw_df[raw_df["Value"] != "YES_AUTO"].copy() 

    raw_df["Date"] = parse_dates(raw_df["Date"])
    start_date = raw_df["Date"].min()
    end_date = raw_df["Date"].max()
    full_date_range = pd.date_range(start=start_date, end=end_date, freq="D")

    timeline_df = pd.DataFrame({"Date": full_date_range})
    timeline_df = timeline_df.merge(raw_df, on="Date", how="left")
    timeline_df["Value"] = timeline_df["Value"].fillna("UNKNOWN")
    timeline_df = timeline_df[["Date", "Value"]]

    engagement_mask = timeline_df["Value"].isin(["YES_MANUAL", "NO", "SKIP"])
    
    #think if it does not return anything

    if not engagement_mask.any():
        return timeline_df, None
    
    first_engagement_index = timeline_df[engagement_mask].index[0]
    anchor_index = first_engagement_index

    

    

    for i in range(anchor_index, len(timeline_df)):

        #if the day is scheduled
        if (i - anchor_index) % frequency_denominator == 0:
            if timeline_df.loc[i, "Value"] in ["YES_MANUAL", "NO", "SKIP", "UNKNOWN"]:
                continue
            
            
        else:
            if timeline_df.loc[i, "Value"] in ["YES_MANUAL", "NO", "SKIP"]:

                #anchor shift detcted
                anchor_index = i
            else:
                timeline_df.loc[i, "Value"] = "YES_AUTO" 
                
    return timeline_df, first_engagement_index

def create_state_views(timeline_df, first_engagement_index):
    if first_engagement_index is None:
        empty_df = pd.DataFrame(columns=["Date", "Value"])

        return (
            empty_df,
            empty_df,
            empty_df
        )

    post_anchor_df = timeline_df.iloc[first_engagement_index:]
    scheduled_df = post_anchor_df[post_anchor_df["Value"] != "YES_AUTO"] #filter out yesauto
    engagement_df = scheduled_df[scheduled_df["Value"] != "UNKNOWN"] # filter out unknown
    active_df = engagement_df[engagement_df["Value"] != "SKIP"] # filter out skip
    return scheduled_df, engagement_df, active_df

def calculate_binary_metrics(active_df):
    total_days = len(active_df)
    total_yes = (active_df["Value"] == "YES_MANUAL").sum()
    consistency = (total_yes/total_days) * 100 if total_days > 0 else 0

# max_streak with dates

    temp_streak = 0
    max_streak = 0
    start_date_temp = None
    

    for i in range(len(active_df)):
        value = active_df.iloc[i]["Value"]
        date = active_df.iloc[i]["Date"]
        if value == "YES_MANUAL":
            if temp_streak == 0:

            #Store only the first date of the current streak    
                start_date_temp = date

            temp_streak += 1
            if temp_streak > max_streak:
                max_streak = temp_streak
                start_date = start_date_temp
                end_date = date

        else:
            temp_streak = 0



# current streak
    current_streak = 0
    for value in reversed(active_df["Value"].tolist()):
        if value == "YES_MANUAL":
            current_streak += 1
        else:
            break

#failures
    failures = 0
    for value in active_df["Value"]:
        if value == "NO":
            failures += 1

    return {
        "total_decisive_days": int(total_days), #maybe wrong bcoz it excludes some scheduled days
        "total_yes": int(total_yes),
        "consistency": round(consistency, 2),
        "Longest_streak": {"length": int(max_streak),
                           "start_date": int(start_date),
                           "end_date": int(end_date)},
        "current_streak": int(current_streak),
        "total_failures": failures 
    }        






def build_behavior_context(habit_name, habit_type, frequency_denominator, engagement_df, active_df ):

    # Create an active-entry dataset.
    # We keep only intentional behavioral states:
    # YES_MANUAL -> user completed the habit
    # NO -> user explicitly failed
    # SKIP -> user intentionally skipped
    #
    # YES_AUTO and UNKNOWN are ignored because they are not considered
    # reliable behavioral signals for this context layer.
    #
    # .copy() is used because filtering can sometimes return a view
    # of the original dataframe instead of a completely independent dataframe.
    # If we later modify that view, it can accidentally affect the original data.
    # Using .copy() creates a safe independent dataframe.
    # active_df = raw_df[raw_df["Value"].isin(["YES_MANUAL", "NO", "SKIP"])].copy()

    # Convert the Date column into datetime format.
    # This allows proper chronological sorting and date operations.
    # active_df["Date"] = pd.to_datetime(
        # active_df["Date"] 
    # )

    # Sort the dataset from oldest -> newest.
    # Behavioral analysis depends on correct chronological order.
    # active_df = active_df.sort_values(by="Date")

    # Main behavior context dictionary.
    # This stores structured behavioral information separately from metrics.
    behavior_context = {
        "habit_name": habit_name,
        "habit_type": habit_type,
        "frequency_denominator": frequency_denominator,
        

    }

    # Continue only if interpretable behavioral entries exist.
    # If the dataframe is empty, we do not infer anything from UNKNOWN values.
    if not active_df.empty:

        # First intentional interaction with the habit.
        behavior_context["first_active_entry"] = {
            "date": active_df.iloc[0]["Date"].strftime("%d-%m-%Y"),
            "value": active_df.iloc[0]["Value"]
        }

    if not engagement_df.empty:

        # Latest intentional interaction with the habit.
        behavior_context["latest_engagement_entry"] = {
            "date": engagement_df.iloc[-1]["Date"].strftime("%d-%m-%Y"),
            "value": engagement_df.iloc[-1]["Value"]
        }

        # Stores all disengagement regions found in the dataset.
        disengagement_periods = []

        # Traversal pointer.
        # This represents the current unconsumed behavioral state.
        i = 0

        # Traverse through the engagement timeline.
        while i < len(engagement_df):

            row = engagement_df.iloc[i]

            # If current state is not SKIP,
            # move normally to the next row.
            if row["Value"] != "SKIP":
                i += 1

            else:

                # Beginning of a disengagement region.
                start_skip_date = row["Date"]

                # Count the current SKIP entry.
                skip_count = 1

                # Secondary traversal pointer.
                # This expands the disengagement region forward.
                j = i + 1

                # Continue consuming consecutive SKIP states.
                #
                # j must remain within dataframe bounds to avoid index errors.
                #
                # This is state-based traversal:
                # we are consuming an entire contiguous SKIP region,
                # not treating each SKIP row as an independent disengagement.
                while (
                    j < len(engagement_df)
                    and engagement_df.iloc[j]["Value"] == "SKIP"
                ):
                    skip_count += 1
                    j += 1

                # j is now either:
                # 1. pointing to the first non-SKIP state
                # OR
                # 2. outside dataframe bounds
                #
                # j - 1 therefore becomes the final SKIP entry
                # inside the disengagement region.
                end_skip_date = engagement_df.iloc[j - 1]["Date"]

                # If j is still inside dataframe bounds,
                # a future decisive behavioral outcome exists.
                if j < len(engagement_df):

                    next_decisive_date = engagement_df.iloc[j]["Date"]
                    next_decisive_outcome = engagement_df.iloc[j]["Value"]

                # Otherwise the disengagement region remains unresolved.
                else:

                    next_decisive_date = None
                    next_decisive_outcome = None

                # Store the disengagement region.
                disengagement_periods.append({
                    "start_skip_date": start_skip_date.strftime("%d-%m-%Y"),
                    "end_skip_date": end_skip_date.strftime("%d-%m-%Y"),
                    "skip_count": skip_count,
                    "next_decisive_date":
                        next_decisive_date.strftime("%d-%m-%Y")
                        if next_decisive_date is not None
                        else None,
                    "next_decisive_outcome": next_decisive_outcome
                })

                # IMPORTANT:
                # j now points to the first unconsumed non-SKIP state.
                #
                # We jump directly to j instead of doing i += 1.
                #
                # This prevents revisiting SKIP states that already belong
                # to the disengagement region we just processed.
                #
                # This is region/state traversal rather than simple row traversal.
                i = j

        # Attach all disengagement regions into the behavior context.
        behavior_context["disengagement_periods"] = disengagement_periods

    # Return the final structured behavior context.
    return behavior_context











    
                


            







        


        

        
        
        

        
        


    













                    
                    
                

             

                

            




    




