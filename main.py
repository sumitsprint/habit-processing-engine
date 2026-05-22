# Api should be in main.py, and all the processing logic should be in processing.py to keep the code clean and maintainable.

from fastapi import FastAPI, File, UploadFile
from fastapi.params import Form
from Processors.utils import load_data
from Processors.binary_processing import clean_binary_data, calculate_binary_metrics, build_behavior_context
from Processors.numerical_processing import clean_numerical_data, calculate_numerical_metrics
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
        if row["Type"] == "YES_NO":
            df, skipped_days_count, unknown_days_count = clean_binary_data(df)
            metrics = calculate_binary_metrics(df, skipped_days_count, unknown_days_count)
            behavior_context = build_behavior_context(raw_df, habit_name)
            result = {
                "metrics": metrics,
                "behavior_context": behavior_context
            }

        elif row["Type"] == "NUMERICAL":
            if row["Target Type"] != "AT_LEAST":
                return {"error": "only AT_LEAST target type is supported for NUMERICAL habits"}
            target_value = float(row["Target Value"])
            frequency_denominator = int(row['FrequencyDenominator'])
            df, skipped_days_count, unknown_days_count = clean_numerical_data(df)
            result = calculate_numerical_metrics(df, target_value, frequency_denominator, skipped_days_count, unknown_days_count)
        else:
            return {"error": "Unsupported habit type"}
    else:
        df, skipped_days_count, unknown_days_count = clean_binary_data(df)
        result = calculate_binary_metrics(df, skipped_days_count, unknown_days_count)    
    return result





    
    




                                                                                      
                                                                                       
     
    
    
    
    

    
    
        
    


