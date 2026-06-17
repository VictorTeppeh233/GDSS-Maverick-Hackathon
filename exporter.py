import pandas as pd
import io

def generate_excel(data_list):
    df = pd.DataFrame(data_list)
    
    expected_cols = [
        "ITEM_NAME", "BARCODE", "MANUFACTURER", "BRAND", "WEIGHT", 
        "PACKAGING TYPE", "COUNTRY", "VARIANT", "TYPE", 
        "FRAGRANCE_FLAVOR", "PROMOTION", "ADDONS", "TAGLINE", "WARNINGS"
    ]
    
    for col in expected_cols:
        if col not in df.columns:
            df[col] = ""
            
    df = df[expected_cols]
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='IMDB_Data')
    
    output.seek(0)
    return output

def generate_csv(data_list):
    df = pd.DataFrame(data_list)
    
    expected_cols = [
        "ITEM_NAME", "BARCODE", "MANUFACTURER", "BRAND", "WEIGHT", 
        "PACKAGING TYPE", "COUNTRY", "VARIANT", "TYPE", 
        "FRAGRANCE_FLAVOR", "PROMOTION", "ADDONS", "TAGLINE", "WARNINGS"
    ]
    
    for col in expected_cols:
        if col not in df.columns:
            df[col] = ""
            
    df = df[expected_cols]
    
    output = io.BytesIO()
    output.write(df.to_csv(index=False).encode('utf-8'))
    output.seek(0)
    return output
