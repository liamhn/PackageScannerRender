import streamlit as st
import os
import re
import datetime
import pandas as pd
import numpy as np
from PIL import Image
import pytesseract  # lighter than EasyOCR

# --- Load resident database ---
def pull_tenant_registry_from_sheet(sheetid,gid=0):
    url = f"https://docs.google.com/spreadsheets/d/{sheetid}/export?format=csv&gid={gid}"
    try:
        df = pd.read_csv(url)
        print("DataFrame successfully loaded:")
        print(df.head())
    except Exception as e:
        print(f"Error loading DataFrame: {e}")
    return df

sheetid = "13HOk9F_fsEA9hjYcXCARRgnq1b7iu8svJV0rs3ofyns"
resident_database = pull_tenant_registry_from_sheet(sheetid,gid=0)
resident_database.index = resident_database['unit_number']

st.set_page_config(page_title="Package Identifier", layout="centered")
st.markdown("### Zonisync Package Identifier")

buildingAddress = "25 Carlton"

# Camera or upload input
camera_photo = st.camera_input('Take a picture of the label to process.')
uploaded_file = st.file_uploader("Or upload label image", type=["jpg", "png"])
image_source = camera_photo or uploaded_file

if image_source:
    st.info("Processing image...")

    # Convert uploaded/camera image to PIL
    image = Image.open(image_source)

    # Optional: resize to reduce memory
    image = image.convert("L")  # grayscale
    image.thumbnail((800, 800))

    # Run OCR using pytesseract
    ocr_result = pytesseract.image_to_string(image)
    results = [line for line in ocr_result.splitlines() if line.strip() != ""]

    # --- Extract unit number ---
    def get_unit_number_from_results_list(results, buildingAddress):
        formattedAddress = buildingAddress.strip().lower().replace(" ","")
        for res in results:
            formatted_result = res.strip().lower().replace(" ","")
            if formattedAddress in formatted_result:
                unit_string_dirty = formatted_result.split(formattedAddress)[0]
                numeric_string = re.sub(r'[^0-9]', '', unit_string_dirty)
                return numeric_string

    unit_number  = get_unit_number_from_results_list(results, buildingAddress)

    if unit_number and unit_number in resident_database.index:
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        resident_information = resident_database.loc[unit_number]

        st.success(f"Package for {resident_information.resident_name} in unit {unit_number}")
        st.write(f" Email: {resident_information.email}\t\t Phone: {resident_information.phone_number}")
        st.write(f" Logged at: {current_datetime}")

        if st.button("Send Email"):
            st.success("Email sent", icon="📨")
    else:
        st.error("Unit not found in database.")
        st.write(results)
