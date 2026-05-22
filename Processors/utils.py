import pandas as pd

# load data
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df











 


 



if __name__ == "__main__":
    df = load_data("Checkmarks.csv")
    df, skipped_days_count, unknown_days_count = clean_data(df)
    print(df.head(10))
    print("Total YES entries:", df['habit'].sum())
    print("unique values in 'habit' column:", df['habit'].unique(), "end of unique values")
    result = calculate_metrics(df, skipped_days_count, unknown_days_count)
    print("Results Summary:", result)
    
