import streamlit as st
import pandas as pd
import requests
import zipfile
import os
import re
from io import BytesIO
from urllib.parse import urlparse

# --- Function to Clean Filenames ---
def slugify(text):
    """Removes special characters to make text safe for filenames."""
    return re.sub(r'[^\w\s-]', '', str(text)).strip().replace(' ', '_')

# --- Function to Download and Zip ---
def process_images_to_zip(df, brand_col, model_col, url_col):
    zip_buffer = BytesIO()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for index, row in df.iterrows():
            url = row[url_col]
            brand = row[brand_col]
            model = row[model_col]

            if pd.isna(url) or not str(url).startswith('http'):
                continue
                
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    # Determine extension
                    parsed_path = urlparse(url).path
                    ext = os.path.splitext(parsed_path)[1]
                    if not ext:
                        ext = ".png" # Default to png as requested
                    
                    # Create custom filename: Brand_Model.png
                    clean_name = f"{slugify(brand)}-{slugify(model)}{ext}"
                    
                    zip_file.writestr(clean_name, response.content)
            except Exception:
                continue
                
    return zip_buffer.getvalue()

# --- Streamlit UI Layout ---
st.set_page_config(page_title="Custom Excel Image Downloader", page_icon="📁")

st.title("📁 Bulk Excel Image Downloader")
st.write("Upload your Excel to package images into a ZIP using **Brand - Model** names.")

# Placeholder for the download button at the top
download_placeholder = st.empty()

# 1. File Upload
uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("### Data Preview", df.head())
    
    # Column Selection
    col1, col2, col3 = st.columns(3)
    with col1:
        brand_column = st.selectbox("Select Brand column:", df.columns, index=0)
    with col2:
        model_column = st.selectbox("Select Model column:", df.columns, index=1)
    with col3:
        url_column = st.selectbox("Select Image URL column:", df.columns, index=2)
    
    if st.button("🚀 Process & Generate ZIP"):
        with st.spinner(f"Downloading images as '{brand_column}-{model_column}.png'..."):
            zip_data = process_images_to_zip(df, brand_column, model_column, url_column)
            
        if zip_data:
            st.success("✅ ZIP file ready!")
            
            # 2. Place the Save/Download button at the top
            download_placeholder.download_button(
                label="💾 SAVE ZIP FILE (Download Now)",
                data=zip_data,
                file_name="brand_model_images.zip",
                mime="application/zip",
                use_container_width=True
            )
        else:
            st.error("No valid images could be downloaded.")
else:
    st.info("Waiting for Excel file upload...")
