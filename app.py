import streamlit as st
import pandas as pd
import os
from io import BytesIO
import matplotlib.pyplot as plt

# Set up Streamlit app
st.set_page_config(page_title="Data Sweeper", layout="wide")
st.title("Data Cleaner")
st.write("Transform Your Files between CSV and Excel formats with built-in data cleaning and Visualization")

uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Read file based on extension
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Display file details
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {len(file.getbuffer()) / 1024:.2f} KB")

        # Display dataframe preview
        st.write("Preview the head of the DataFrame")
        st.dataframe(df.head())

        # Data cleaning options
        st.subheader("Data Cleaning Options")

        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.success("Duplicates Removed!")

            with col2:
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("Missing Values have been filled!")

            # Move the column selection outside the col2 block
            st.subheader("🛠️ Select Columns to Convert")
            columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
            df = df[columns]

        # Data Visualization
        st.subheader("📊 Data Visualization")
        if not df.empty:
            chart_type = st.selectbox("Select Chart Type", ["Line Chart", "Bar Chart", "Histogram"], key=f"chart_{file.name}")
            x_axis = st.selectbox("Select X-axis", df.columns, key=f"x_{file.name}")
            numeric_cols = df.select_dtypes(include="number").columns

            if not numeric_cols.empty:
                y_axis = st.selectbox("Select Y-axis", numeric_cols, key=f"y_{file.name}")

                if st.button(f"Generate Chart for {file.name}"):
                    fig, ax = plt.subplots()
                    try:
                        if chart_type == 'Line Chart':
                            df.plot(x=x_axis, y=y_axis, ax=ax, kind='line')
                        elif chart_type == 'Bar Chart':
                            df.plot(x=x_axis, y=y_axis, ax=ax, kind='bar')
                        elif chart_type == 'Histogram':
                            df[y_axis].plot(kind='hist', ax=ax)

                        st.pyplot(fig)
                    except KeyError as e:
                        st.error(f"⚠️ Error: Column '{e.args[0]}' not found. Please reselect the columns.")
            else:
                st.warning("⚠️ No numeric columns available for visualization.")

        # Convert the File -> CSV to Excel
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(f"Convert {file.name}", ['CSV', 'Excel'], key=file.name)

        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"

            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False)
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)

            st.download_button(
                label=f"Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type,
            )

    st.success("All files Processed!")
