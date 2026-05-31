import pandas as pd




def clean_numerical_data(df):
    skip_mask = df["Value"] == "SKIP"
    unknown_mask = df["Value"] == "UNKNOWN"
    skipped_days_count = skip_mask.sum()
    unknown_days_count = unknown_mask.sum()
    df = df[~df["Value"].isin(["SKIP", "UNKNOWN"])]
    df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=True)
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce").fillna(0)  
    df["Value"] = df["Value"] / 1000
    df = df.sort_values(by="Date")
    df = df[["Date", "Value"]]
    return df, skipped_days_count, unknown_days_count


def calculate_numerical_metrics(df, target_value, frequency_denominator, skipped_days_count, unknown_days_count):
    values = df['Value'].tolist()
    freq = frequency_denominator

    windows = []
    current_window = []
    for val in values:
        current_window.append(val)
        if len(current_window) == freq:
            windows.append(current_window)
            current_window = []
    window_results = []
    for window in windows:
        window_sum = sum(window)

        if window_sum >= target_value:
            window_results.append(1)
        else:
            window_results.append(0)

    total_success = sum(window_results)
    total_windows = len(window_results) 
    consistency = (total_success/total_windows) * 100 if total_windows > 0 else 0

    max_streak = 0
    temp_streak = 0
    for n in window_results:
        if n == 1:
            temp_streak += 1
            max_streak = max(max_streak, temp_streak)
        else:
            temp_streak = 0

    current_streak = 0
    for n in reversed(window_results):
        if n == 1:
            current_streak += 1
        else:
            break
    failures = []
    for i, n in enumerate(window_results):
        if n == 0:
            failures.append(i + 1) 
     #failures in windows                          

    return {
                "total_success" : int(total_success),
                "Total_Windows" : int(total_windows),
                "Consistency" : round(consistency, 2),
                "Longest_Streak" : int(max_streak),
                "Current_Streak" : int(current_streak),
                "Failure_Windows" : failures,
                "Skipped_days_count": int(skipped_days_count),
                "unknown_days_count": int(unknown_days_count)
                

                }


# reconstructing the entire timeline for fixed window logic
# sparse data to timeline reconstruction



def reconstruct_timeline(raw_df):
    raw_df["Date"] = pd.to_datetime(raw_df["Date"])
    raw_df = raw_df.sort_values(by="Date")
    start_date =  raw_df["Date"].min()
    end_date = raw_df["Date"].max()
    full_date_range = pd.date_range(start=start_date, end=end_date, freq="D")

    # return a sequence of dates from 
    #start to end with daily frequency
    #returns a DatetimeIndex object containing all the dates in the specified range

    timeline_df = pd.DataFrame({"Date": full_date_range})
    timeline_df = timeline_df.merge(raw_df, on="Date", how="left")
    timeline_df["Value"] = timeline_df["Value"].fillna("UNKNOWN")
    timeline_df = timeline_df[["Date", "Value"]]
    return timeline_df

# normalise the string values to numbers and preserve skip and unknown
# and convert NO to 0




def normalise_numerical_states(timeline_df):
    normalise_df = timeline_df.copy()
    normalise_df["Value"] = normalise_df["Value"].replace("NO", 0)
    numeric_mask = ~normalise_df["Value"].isin(["SKIP", "UNKNOWN"])
    #row selection
    numeric_strings = normalise_df.loc[numeric_mask, "Value"]
    numeric_values = pd.to_numeric(numeric_strings)
    # returns series
    numeric_values = numeric_values / 1000
    # how to assign these numeric values back to the original dataframe
    
    normalise_df.loc[numeric_mask, "Value"] = numeric_values
    
    return normalise_df


# window extraction and evaluation logic
def evaluate_window(window_df):
    numeric_mask = ~window_df["Value"].isin(["SKIP", "UNKNOWN"])
    numeric_values = window_df.loc[numeric_mask, "Value"]
    running_sum = numeric_values.sum()
    return running_sum

#skip triggered extension logic 
def skip_triggered_extension(normalise_df, starting_point, provisional_end, skip_count):
    handled_skip_count = skip_count
    extended_end = provisional_end + handled_skip_count
    if extended_end > len(normalise_df):
        return None
    # slice the extended window and compute sum
    window_df = normalise_df.iloc[starting_point:extended_end]
        #recompute skip count in the extended window
    current_skip_count = (window_df["Value"] == "SKIP").sum()
    while current_skip_count > handled_skip_count:
        additional_skips = current_skip_count - handled_skip_count
        extended_end += additional_skips
        handled_skip_count = current_skip_count
        if extended_end > len(normalise_df):
            break
        window_df = normalise_df.iloc[starting_point:extended_end]
        current_skip_count = (window_df["Value"] == "SKIP").sum()
    return window_df, current_skip_count, extended_end
# window object with default params 
def create_window_object(
    window_number,
    window_df,
    result,
    extension=False,
    extension_length=None,
    skip_dates=None,
    partial_window=False
):
    
    return{
                "window_number": window_number,
                "start_date": window_df.iloc[0]["Date"].strftime("%d/%m/%Y"),
                "end_date": window_df.iloc[-1]["Date"].strftime("%d/%m/%Y"),
                "result": result,
                "extension": extension,
                "extension_length": extension_length,
                "skip_dates": skip_dates,
                "partial_window": partial_window


            }






def making_windows(normalise_df, frequency_denominator, target_value):
    # engagement entries mask 
    engagement_mask = ~normalise_df["Value"].isin(["UNKNOWN"])
    if not engagement_mask.any():
        return []
    #first engagement index
    # .index returns indices values 
    first_engagement_index = normalise_df[engagement_mask].index[0]
    #starting_point and end of the provisional window
    starting_point = first_engagement_index
    # windows of success and failure and unresolved
    windows = []
    window_number = 1
    
    while True:
        provisional_end = starting_point + frequency_denominator
        if provisional_end > len(normalise_df):
            break 
    # slice the window
        window_df = normalise_df.iloc[starting_point:provisional_end]
    # evaluate window
        running_sum = evaluate_window(window_df)
        # check window status
        if running_sum >= target_value:

            window_object = create_window_object(
                                    window_number,
                                    window_df,
                                     result=1
                                            )
            windows.append(window_object)
            
            # starting point of the next window
            starting_point = provisional_end
            window_number += 1
    # window extension logic
        
        else:
            #check skip count
            skip_count = (window_df["Value"] == "SKIP").sum()
            

       
        # if there are no skip entris no extension 
        
            if skip_count == 0:
                unknown_mask = window_df["Value"] == "UNKNOWN"
                if unknown_mask.any():
                    window_object = create_window_object(
                                            window_number,
                                            window_df,
                                            result="unresolved"
                                                         )
                    windows.append(window_object)

                    # starting point of the next window
                    starting_point = provisional_end
                    window_number += 1
                else:
                    window_object = create_window_object(
                                                window_number,
                                                window_df,
                                                result=0
                                                        )
                    windows.append(window_object)
                    # starting point of the next window
                    starting_point = provisional_end  
                    window_number += 1  
 # extend the window by the number of SKIP entries
            else:
                result = skip_triggered_extension(normalise_df, starting_point, provisional_end, skip_count)
                if result is None:
                    break
                else:

                    window_df, current_skip_count, extended_end = result

                skip_count = current_skip_count    
                #evaluate window
                running_sum = evaluate_window(window_df)
                skip_mask = window_df["Value"] == "SKIP"
                skip_dates = window_df.loc[skip_mask, "Date"] 
                # here .loc is returning a series
                skip_dates = skip_dates.dt.strftime("%d/%m/%Y").tolist()

                # check window status
                if running_sum >= target_value:
                    window_object = create_window_object(
                                                window_number,
                                                window_df,
                                                result=1,
                                                extension=True,
                                                extension_length=skip_count,
                                                skip_dates=skip_dates
                                                        )
                    windows.append(window_object)
                    # starting point of the next window
                    starting_point = extended_end
                    window_number += 1
                else:
                # if still not successful, check for UNKNOWN entries in the extended window
                # and if any UNKNOWN entries are present, discard window 
                # if no UNKNOWN entries, failure
                    unknown_mask = window_df["Value"] == "UNKNOWN"
                    if unknown_mask.any():
                        window_object = create_window_object(
                                                    window_number,
                                                    window_df,
                                                    result="unresolved",
                                                    extension=True,
                                                    extension_length=skip_count,
                                                    skip_dates=skip_dates
                                                    )#hereiam
                        windows.append(window_object)
                        # starting point of the next window
                        starting_point = extended_end
                        window_number += 1
                    else:
                        window_object = create_window_object(
                                                    window_number,
                                                    window_df,
                                                    result=0,
                                                    extension=True,
                                                    extension_length=skip_count,
                                                    skip_dates=skip_dates
                                                    )#hereiam
                        windows.append(window_object)
                        # starting point of the next window
                        starting_point = extended_end
                        window_number += 1
                    if starting_point >= len(normalise_df):
                        break
                    # handle last partial window if it exists
    if starting_point < len(normalise_df):
        window_df = normalise_df.iloc[starting_point:len(normalise_df)]
        # evaluate window
        running_sum = evaluate_window(window_df)
        if running_sum >= target_value:
            window_object = create_window_object(
                                        window_number,
                                        window_df,
                                        result=1,
                                        partial_window=True
                                        )
            windows.append(window_object)
        else:
            window_object = create_window_object(
                                        window_number,
                                        window_df,
                                        result="unresolved",
                                        partial_window=True
                                        )
            windows.append(window_object)



    return windows 

def build_api_response(windows, normalise_df, frequency_denominator, target_value, habit_name, habit_type):
    # first active entry

    active_entry_mask = ~normalise_df["Value"].isin(["SKIP", "UNKNOWN"])
    if not active_entry_mask.any():
        
        first_active_date = None
        first_active_value = None
    else:
        active_entries_df = normalise_df.loc[active_entry_mask, ["Date", "Value"]]
        first_active_date = active_entries_df.iloc[0]["Date"].strftime("%d-%m-%Y")
        first_active_value = active_entries_df.iloc[0]["Value"]

    #latest engagement entry

    engagement_mask = ~normalise_df["Value"].isin(["UNKNOWN"])
    engagement_entries_df = normalise_df.loc[engagement_mask, ["Date", "Value"]]
    latest_engagement_date = engagement_entries_df.iloc[-1]["Date"].strftime("%d-%m-%Y")
    latest_engagement_value = engagement_entries_df.iloc[-1]["Value"]

    #latest complete window status
    if windows[-1].get("partial_window", False):
        if len(windows) == 1:
            latest_complete_window_status = None
        else:
            latest_complete_window_status = windows[len(windows) - 2]["result"]
    else:
        latest_complete_window_status = windows[-1]["result"]

    unresolved_window_count = 0  
    success_window_count = 0
    failure_window_count = 0  
        #unresolved window count, success window count, failure window count
    for window in windows:
        if window["result"] == "unresolved":
            unresolved_window_count += 1
        elif window["result"] == 1:
            success_window_count += 1
        elif window["result"] == 0:
            failure_window_count += 1    


    partial_window = windows[-1].get("partial_window", False)  
    
    behavior_context = {
        "habit_name": habit_name,
        "habit_type": habit_type,
        "frequency_denominator": frequency_denominator,
        "target_value": target_value,

        #timeline level info

        "first_active_entry": {
        "date": first_active_date,
        "value": first_active_value
                               },
        "latest_engagement_entry": {
        "date": latest_engagement_date,
        "value": latest_engagement_value
                                   },
        #window level info

        "latest_complete_window_status": latest_complete_window_status,
        "unresolved_window_count": unresolved_window_count,
        "partial_window": partial_window,
        "success_window_count": success_window_count,
        "failure_window_count": failure_window_count


    }
    

    return behavior_context



    









      

    









    





            



       

    

   





        


        







    
















    