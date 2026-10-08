# Api should be in main.py, and all the processing logic should be in processing.py to keep the code clean and maintainable.

from fastapi import FastAPI, File, UploadFile #File is used to specify that the parameter is a file upload
from utils import load_data, save_file
import processing



app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


# API endpoint
 
@app.post("/upload")
async def upload_file(meta_data: UploadFile = File(...), habit_file: UploadFile | None = File(None),  
                      master_file: UploadFile | None = File(None), habit_name: str = ""):
    
    meta_file_path = await save_file(meta_data)
    meta_df = load_data(meta_file_path)

    if habit_file is not None and master_file is not None:
        return {"error": "Please provide either habit_file or master_file, not both."}

    if habit_file is None and master_file is None:
        return {"error": "Please provide either habit_file or master_file."}
    
    if habit_file is not None:
        habit_file_path = await save_file(habit_file) 
        raw_df = load_data(habit_file_path)
    else:
        master_file_path = await save_file(master_file)
        raw_df = load_data(master_file_path)

        #extract habit
        raw_df = raw_df[["Date", habit_name]]
        raw_df = raw_df.rename(columns={habit_name: "Value"}) #name based value passed to arguments

    #process habit
    result = processing.process_habit(meta_df, raw_df, habit_name)
    return result    

   
    
    




    
    




                                                                                      
                                                                                       
     
    
    
    
    

    
    
        
    


