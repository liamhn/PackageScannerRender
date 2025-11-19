import streamlit as st
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import easyocr, re, datetime, pandas as pd
import numpy as np
from PIL import Image
import datetime






def pull_tenant_registry_from_sheet(sheetid,gid = 0):

    url = f"https://docs.google.com/spreadsheets/d/{sheetid}/export?format=csv&gid={gid}"


    try:
        df = pd.read_csv(url)
        print("DataFrame successfully loaded:")
        print(df.head())
    except Exception as e:
        print(f"Error loading DataFrame: {e}")

    return df

sheetid = "13HOk9F_fsEA9hjYcXCARRgnq1b7iu8svJV0rs3ofyns"
resident_database = pull_tenant_registry_from_sheet(sheetid,gid = 0)
resident_database.index = resident_database['unit_number']
print(resident_database)


#resident_database = pd.DataFrame()
#resident_database["unit_number"] = ['1109','1204','1306']
#resident_database["resident_name"] = ['Liam Haas-Neill','John Smith','Jane Doe']
#resident_database["email"] = ['lhn@gmail.com','js@gmail.com','jd@gmail.com']
#resident_database["phone_number"] = ['6475555555','64755555556','64755555557']
#resident_database.index = resident_database['unit_number']


st.set_page_config(page_title="Package Identifier", layout="centered",)
st.markdown("### Zonisync Package Identifier")

reader = easyocr.Reader(['en'], gpu=False)
buildingAddress = "25 Carlton"

#st.markdown("Take a picture of the label to process.")

# Camera or upload input
camera_photo = st.camera_input('Take a picture of the label to process.')
#uploaded_file = st.file_uploader("Or upload label image", type=["jpg", "png"])
uploaded_file = None
image_source = camera_photo or uploaded_file

if image_source:
    st.info("Processing image...")

    # Convert uploaded/camera image to numpy array
    image = Image.open(image_source)
    image_np = np.array(image)

    # Run OCR
    results = reader.readtext(image_np, detail=0)


    def get_unit_number_from_results_list(results,buildingAddress):
        formattedAddress = buildingAddress.strip().lower().replace(" ","")

        for i in range(len(results)):
            formatted_result = results[i].strip().lower().replace(" ","")
            
            if formattedAddress in formatted_result:
                unit_string_dirty = formatted_result.split(formattedAddress)[0]
                numeric_string = re.sub(r'[^0-9]', '', unit_string_dirty)
                return numeric_string

    unit_number  = get_unit_number_from_results_list(results, buildingAddress)

    if unit_number and unit_number in resident_database.index:
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        resident_information = resident_database.loc[unit_number]

        st.success(f"Package for {resident_information.resident_name} in unit {unit_number}")
        st.write(f" Email: {resident_information.email}\t\t\t Phone: {resident_information.phone_number}")
        #st.write(f" ")
        st.write(f" Logged at: {formatted_datetime}")
        if st.button("Send Email"):
            # Here you can add code to save the log to a file or database
            # and code to send email/SMS notification
            st.success("Email sent", icon="📨")

    else:
        st.error("Unit not found in database. Make sure text is fully clear and horizontal in the frame.")
        #st.error(results)
