import streamlit as st
import pandas as pd
import requests
import zipfile
import os
from io import BytesIO
from urllib.parse import urlparse

# --- Function to Download and Zip ---
def process_images_to_zip(urls):
    zip_buffer = BytesIO()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for i, url in enumerate(urls):
            if pd.isna(url) or not str(url).startswith('http'):
                continue
                
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    # Clean up URL to get a valid filename
                    parsed_path = urlparse(url).path
                    ext = os.path.splitext(parsed_path)[1]
                    if not ext:
                        ext = ".jpg"
                    
                    filename = f"image_{i+1}{ext}"
                    zip_file.writestr(filename, response.content)
            except Exception:
                continue
                
    return zip_buffer.getvalue()

# --- Streamlit UI Layout ---
st.set_page_config(page_title="Excel Image Downloader", page_icon="📁")

st.title("📁 Bulk Excel Image Downloader")
st.write("Upload an Excel file containing a column of image URLs to package them into a ZIP.")

# Placeholder for the download button at the top
download_placeholder = st.empty()

# 1. File Upload
uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    # Load Excel
    df = pd.read_excel(uploaded_file)
    st.write("### Data Preview", df.head())
    
    # Column Selection
    column_to_scrape = st.selectbox("Select the column containing Image URLs:", df.columns)
    
    if st.button("🚀 Process & Generate ZIP"):
        urls = df[column_to_scrape].tolist()
        
        with st.spinner(f"Downloading {len(urls)} images... Please wait."):
            zip_data = process_images_to_zip(urls)
            
        if zip_data:
            st.success("✅ ZIP file ready!")
            
            # 2. Place the Save/Download button at the top using the placeholder
            download_placeholder.download_button(
                label="💾 SAVE ZIP FILE (Download Now)",
                data=zip_data,
                file_name="bulk_images.zip",
                mime="application/zip",
                use_container_width=True
            )
            
            # Also show a reminder at the bottom
            st.info("The download button is now active at the top of the page.")
        else:
            st.error("No valid images could be downloaded.")

else:
    st.info("Waiting for Excel file upload...")
