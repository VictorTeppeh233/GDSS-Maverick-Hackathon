import streamlit as st
import pandas as pd
from PIL import Image
from extractor import extract_product_data
from validator import validate_extraction
import os

st.set_page_config(page_title="AI IMDB Auto-Fill", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Center title and style gradient */
    .stApp > header {
        background-color: transparent;
    }
    .title-text {
        font-size: 3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #8A2BE2, #4169E1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: -1rem;
    }
    .subtitle-text {
        text-align: center;
        color: #A0AEC0;
        font-weight: 300;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }
    
    /* Button Hover Effects */
    .stButton > button {
        border-radius: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(138, 43, 226, 0.3);
    }
    
    /* Image Grid Hover */
    [data-testid="stImage"] img {
        border-radius: 12px;
        transition: transform 0.3s ease;
    }
    [data-testid="stImage"] img:hover {
        transform: scale(1.05);
    }
    
    /* Hide Streamlit footer */
    footer {visibility: hidden;}
    
    /* Data Editor Radius */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title-text'>📦 AI-Driven Image-to-IMDB</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>Intelligent visual data extraction for your Item Master Database.</p>", unsafe_allow_html=True)

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
            duplicate_df = pd.DataFrame()
            
            if not db_to_check.empty:
                barcode = str(validated_data.get("BARCODE", ""))
                brand = str(validated_data.get("BRAND", ""))
                weight = str(validated_data.get("WEIGHT", ""))
                
                if barcode and "BARCODE" in db_to_check.columns:
                    match_barcode = db_to_check[db_to_check["BARCODE"].astype(str) == barcode]
                    if not match_barcode.empty:
                        duplicate_df = pd.concat([duplicate_df, match_barcode])
                        
                if duplicate_df.empty and brand and weight and "BRAND" in db_to_check.columns and "WEIGHT" in db_to_check.columns:
                    match_bw = db_to_check[(db_to_check["BRAND"].astype(str).str.upper() == brand) & (db_to_check["WEIGHT"].astype(str).str.upper() == weight)]
                    if not match_bw.empty:
                        duplicate_df = pd.concat([duplicate_df, match_bw])
                        
                if not duplicate_df.empty:
                    duplicate_df = duplicate_df.drop_duplicates()
                    current_warning = validated_data.get("WARNINGS", "")
                    validated_data["WARNINGS"] = ("⚠️ DUPLICATE! " + current_warning).strip()
                    st.session_state['duplicate_match_df'] = duplicate_df
                else:
                    st.session_state['duplicate_match_df'] = None
            else:
                st.session_state['duplicate_match_df'] = None

            st.session_state['current_item'] = [validated_data]
        except Exception as e:
            st.error(f"Failed to extract data: {e}")

if 'current_item' in st.session_state and st.session_state['current_item']:
    st.divider()
    st.subheader("Review Extracted Item")
    
    # Show explicit warnings
    warnings = st.session_state['current_item'][0].get("WARNINGS", "")
    if warnings:
        if "DUPLICATE" in warnings:
            st.error(f"🚨 **Action Required:** {warnings}")
        else:
            st.warning(f"⚠️ **Attention Required:** {warnings}")
            
    # Show the duplicate row if it exists
    if 'duplicate_match_df' in st.session_state and st.session_state['duplicate_match_df'] is not None and not st.session_state['duplicate_match_df'].empty:
        st.error("**This product appears to be a duplicate of the following existing record(s):**")
        dup_display = st.session_state['duplicate_match_df'].copy()
        # Offset index by 1 for readability
        dup_display.index = dup_display.index + 1
        st.dataframe(dup_display, use_container_width=True)
    
    df_current = pd.DataFrame(st.session_state['current_item'])
    df_current.index = df_current.index + 1
    edited_df = st.data_editor(df_current, num_rows="dynamic", use_container_width=True, key=f"editor_{st.session_state.uploader_key}")
    
    col1, col2 = st.columns(2)
    with col1:
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
    with col2:
        if st.button("❌ Discard Extraction", use_container_width=True):
            st.session_state['current_item'] = []
            st.session_state.uploader_key += 1
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
