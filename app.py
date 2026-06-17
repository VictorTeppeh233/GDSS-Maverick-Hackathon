import streamlit as st
import pandas as pd
from PIL import Image
from extractor import extract_product_data
from validator import validate_extraction
import os

st.set_page_config(page_title="AI IMDB Auto-Fill", layout="wide")

st.title("📦 AI-Driven Image-to-IMDB Tool")
st.markdown("Process products one by one and append them directly to your master database.")

from dotenv import load_dotenv
load_dotenv()

# Fallback to Streamlit secrets if not in environment variables
if "GEMINI_API_KEY" not in os.environ and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
    
# Master Data Initialization
PREDICTIONS_FILE = "predictions.xlsx"

if 'master_data' not in st.session_state:
    st.session_state.master_data = pd.DataFrame()

if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

st.sidebar.divider()
existing_db_file = st.sidebar.file_uploader("Upload External DB for Duplicate Check", type=['xlsx', 'csv'])
existing_db = None
if existing_db_file:
    try:
        if existing_db_file.name.endswith('.csv'):
            existing_db = pd.read_csv(existing_db_file)
        else:
            existing_db = pd.read_excel(existing_db_file)
        st.sidebar.success(f"Loaded external DB with {len(existing_db)} rows.")
    except Exception as e:
        st.sidebar.error("Failed to load external DB.")

st.markdown("### Process Recent Product")
files = st.file_uploader("Upload Images for Current Product", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'], key=f"uploader_{st.session_state.uploader_key}")

if files:
    # Display thumbnails in a mobile-responsive grid (max 3 per row)
    for i in range(0, min(len(files), 6), 3):
        cols = st.columns(3)
        for j, file in enumerate(files[i:i+3]):
            img = Image.open(file)
            cols[j].image(img, use_container_width=True)

if files and st.button("Extract Data for Recent Product", type="primary", use_container_width=True):
    with st.spinner("Analyzing product with AI..."):
        try:
            images = [Image.open(f) for f in files]
            raw_data = extract_product_data(images)
            validated_data = validate_extraction(raw_data)
            
            # Duplicate check
            db_to_check = existing_db if existing_db is not None else st.session_state.master_data
            if not db_to_check.empty:
                barcode = str(validated_data.get("BARCODE", ""))
                brand = str(validated_data.get("BRAND", ""))
                weight = str(validated_data.get("WEIGHT", ""))
                
                is_duplicate = False
                if barcode and "BARCODE" in db_to_check.columns:
                    if barcode in db_to_check["BARCODE"].astype(str).values:
                        is_duplicate = True
                        
                if not is_duplicate and brand and weight and "BRAND" in db_to_check.columns and "WEIGHT" in db_to_check.columns:
                    match = db_to_check[(db_to_check["BRAND"].astype(str).str.upper() == brand) & (db_to_check["WEIGHT"].astype(str).str.upper() == weight)]
                    if not match.empty:
                        is_duplicate = True
                        
                if is_duplicate:
                    current_warning = validated_data.get("WARNINGS", "")
                    validated_data["WARNINGS"] = ("⚠️ DUPLICATE! " + current_warning).strip()

            st.session_state['current_item'] = [validated_data]
        except Exception as e:
            st.error(f"Failed to extract data: {e}")

if 'current_item' in st.session_state and st.session_state['current_item']:
    st.subheader("Review Extracted Item")
    df_current = pd.DataFrame(st.session_state['current_item'])
    df_current.index = df_current.index + 1
    edited_df = st.data_editor(df_current, num_rows="dynamic", use_container_width=True, key=f"editor_{st.session_state.uploader_key}")
    
    if st.button("✅ Approve & Save Item", type="primary", use_container_width=True):
        # Append to master data
        new_row_df = pd.DataFrame(edited_df)
        st.session_state.master_data = pd.concat([st.session_state.master_data, new_row_df], ignore_index=True)
        
        # Save to excel file
        st.session_state.master_data.to_excel(PREDICTIONS_FILE, index=False, engine='openpyxl')
        
        # Clear current item and reset uploader
        st.session_state['current_item'] = []
        st.session_state.uploader_key += 1
        st.success("Item saved to predictions.xlsx successfully!")
        st.rerun()

st.divider()
st.subheader("Master Data (predictions.xlsx)")
if not st.session_state.master_data.empty:
    display_df = st.session_state.master_data.copy()
    display_df.index = display_df.index + 1
    st.dataframe(display_df, use_container_width=True)
    
    if os.path.exists(PREDICTIONS_FILE):
        with open(PREDICTIONS_FILE, "rb") as file:
            btn = st.download_button(
                label="⬇️ Download Master Excel",
                data=file,
                file_name="predictions.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
else:
    st.info("No items processed yet.")
