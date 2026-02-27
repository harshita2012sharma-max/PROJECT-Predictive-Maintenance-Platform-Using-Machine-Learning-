import pandas as pd
from database.data_access import fetch_training_data  

def load_data():
    data = fetch_training_data()  
    if not data:  
        print("Warning: No training data found in MySQL.")
        return pd.DataFrame()  
    
    df = pd.DataFrame(data)  
    print(f"Loaded {len(df)} records from database")
    return df