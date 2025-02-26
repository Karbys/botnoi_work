import streamlit as st
import pandas as pd

def upload_file():
    st.set_page_config(page_title="Wong-Wai", page_icon=":pushpin:", layout="wide")
    image_path = "IMG_6027.png" 
    st.image(image_path, width=300 ) #use_container_width =True
    st.title("Wong-Wai AI")
    st.write("AI for Detection and Handling Social Media Crisis Management")
    st.title("Upload your file")

    # แบ่ง layout เป็น 2 คอลัมน์ (ซ้ายเล็กกว่า)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📂 Upload File")
        uploaded_file = st.file_uploader("Choose a file", type=["xlsx", "csv"])

    selected_data = None

    if uploaded_file is not None:
        with col1:
            st.subheader("🔍 Select Columns")

        with col2:
            st.subheader("📊 Data Preview")
            
            # อ่านไฟล์ CSV หรือ Excel
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                xls = pd.ExcelFile(uploaded_file)
                sheet_names = xls.sheet_names
                selected_sheet = st.selectbox("Choose a sheet", sheet_names)
                df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

            df = df.applymap(str)  # แปลงข้อมูลเป็น string
            st.write(df.head())  # แสดงตารางตัวอย่าง
        
        with col1:  # กล่องเลือกคอลัมน์อยู่ฝั่งซ้าย
            column1 = st.selectbox("Select first column", df.columns.tolist(), key="col1")

            # # กรองคอลัมน์ที่เหลือโดยไม่รวม column1
            # available_columns_2 = [col for col in df.columns if col != column1]
            # column2 = st.selectbox("Select sentiment answer", available_columns_2, key="col2")

            # # กรองคอลัมน์ที่เหลือโดยไม่รวม column1 และ column2
            # available_columns_3 = [col for col in df.columns if col not in [column1, column2]]
            # column3 = st.selectbox("Select classify answer", available_columns_3, key="col3")


        with col2:  # แสดงผลข้อมูลที่เลือกไปอยู่ฝั่งขวา
            if column1:
                selected_data = df[[column1]].values.tolist()
                st.subheader("📌 Selected Data")
                st.write(selected_data)
            # if column1 and column2 and column3:
            #     selected_data = df[[column1, column2, column3]].values.tolist()
            #     st.subheader("📌 Selected Data")
            #     st.write(selected_data)

    return selected_data
