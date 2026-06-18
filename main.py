# Api should be in main.py, and all the processing logic should be in processing.py to keep the code clean and maintainable.

from fastapi import FastAPI, File, UploadFile
from fastapi.params import Form
from Processors.utils import load_data
from Processors.binary_processing import reconstruct_timeline_binary, create_state_views, build_behavior_context
from Processors.numerical_processing import clean_numerical_data, calculate_numerical_metrics, reconstruct_timeline, normalise_numerical_states, extract_windows, build_api_response
import os

app = FastAPI()
os.makedirs("temp", exist_ok=True)


@app.get("/")
def root():
    return {"message": "Hello World"}


# 🔹 Save uploaded file
async def save_file(file: UploadFile):
    file_path = os.path.join("temp", file.filename)
    with open(file_path, "wb") as buffer:
        chunk = await file.read(1024)
        while chunk:
            buffer.write(chunk)
            chunk = await file.read(1024)
    return file_path



# 🔹 API endpoint
 
@app.post("/upload")
async def upload_file(file: UploadFile = File(...), habit_name: str = ""):
    file_path = await save_file(file)
    df = load_data(file_path)
    raw_df = df.copy()

    if habit_name:
        meta_df = load_data("datasets/Meta.csv")
        meta_row = meta_df[meta_df["Name"] == habit_name]
        if meta_row.empty:
            return {"error": "Habit not found in Meta.csv"}
        row = meta_row.iloc[0]
        habit_type = row["Type"]  
        if row["Type"] == "YES_NO":
            frequency_denominator = int(row['FrequencyDenominator'])
            
            timeline_df, first_engagement_index = reconstruct_timeline_binary(raw_df, frequency_denominator)
            _, engagement_df, active_df = create_state_views(timeline_df, first_engagement_index)
            behavior_context = build_behavior_context(habit_name, habit_type, frequency_denominator, engagement_df, active_df )
            #unpacking is position based not name based
                
                
            

        elif row["Type"] == "NUMERICAL":
            if row["Target Type"] != "AT_LEAST":
                return {"error": "only AT_LEAST target type is supported for NUMERICAL habits"}
            target_value = float(row["Target Value"])
            frequency_denominator = int(row['FrequencyDenominator'])
            df, skipped_days_count, unknown_days_count = clean_numerical_data(df)
            result = calculate_numerical_metrics(df, target_value, frequency_denominator, skipped_days_count, unknown_days_count)
            #new pipeline
            timeline_df = reconstruct_timeline(raw_df)
            normalise_df = normalise_numerical_states(timeline_df)
            windows = extract_windows(normalise_df, frequency_denominator, target_value)
            #
            print(len(windows))

            for window in windows:
                print(window)
                #
            behavior_context = build_api_response(windows, normalise_df, frequency_denominator, target_value, habit_name, habit_type)


        else:
            return {"error": "Unsupported habit type"}
    
           
    return behavior_context





    
    




                                                                                      
                                                                                       
     
    
    
    
    

    
    
        
    


