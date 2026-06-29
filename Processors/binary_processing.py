import pandas as pd
from Processors.utils import parse_dates


# construct the timeline
def reconstruct_timeline_binary(raw_df, frequency_denominator):
    
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

        # if the day is scheduled
        if (i - anchor_index) % frequency_denominator == 0:
            if timeline_df.loc[i, "Value"] in ["YES_MANUAL", "NO", "SKIP", "UNKNOWN"]:
                #preserve these values
                continue
            
            
        else:

            #if any engagement entry appears on non-scheduled day that means anchor is shifting  
            if timeline_df.loc[i, "Value"] in ["YES_MANUAL", "NO", "SKIP"]:


                #anchor shift detcted
                anchor_index = i
            else:
                timeline_df.loc[i, "Value"] = "YES_AUTO" 
                
    return timeline_df, first_engagement_index


# create df for particular states
#helper func
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

# calculate metrics
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

                #keep updating end date on the fly
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
                           "start_date": start_date.strftime("%d/%m/%Y"),
                           "end_date": end_date.strftime("%d/%m/%Y")
                           },
        "current_streak": int(current_streak),
        "total_failures": failures 
    }        

#create object 
def create_behavior_context(habit_name, habit_type,
                             frequency_denominator, 
                             first_active_entry=None, 
                             latest_engagement_entry=None,
                             disengagement_periods=None):
    return {
            "habit_name": habit_name,
            "habit_type": habit_type,
            "frequency_denominator": frequency_denominator,
            "first_active_entry": first_active_entry or {},
            "latest_engagement_entry": latest_engagement_entry or {},
            "disengagement_periods": disengagement_periods or [],
    
    }



# api response
def build_behavior_context(habit_name, habit_type, frequency_denominator, engagement_df, active_df ):
    first_active_entry = None
    latest_engagement_entry = None
    disengagement_periods = None

    if not active_df.empty:

        # First intentional interaction with the habit.
        first_active_entry = {
            "date": active_df.iloc[0]["Date"].strftime("%d-%m-%Y"),
            "value": active_df.iloc[0]["Value"]
        }

        

    if not engagement_df.empty:

        # Latest intentional interaction with the habit.
        latest_engagement_entry = {
            "date": engagement_df.iloc[-1]["Date"].strftime("%d-%m-%Y"),
            "value": engagement_df.iloc[-1]["Value"]
        }

        # Stores all disengagement regions found in the dataset.
        disengagement_periods = []

        # Traversal pointer.
        
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

                
                # traverse the skip region (region traversal)
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
                    "next_decisive_outcome": next_decisive_outcome if next_decisive_outcome is not None
                        else None
                })

                
                # This is region/state traversal rather than simple row traversal.
                i = j

        
    behavior_context = create_behavior_context(habit_name, habit_type,
                            frequency_denominator, 
                            first_active_entry=first_active_entry, 
                            latest_engagement_entry=latest_engagement_entry,
                            disengagement_periods=disengagement_periods)

    # Return the final structured behavior context.
    return behavior_context