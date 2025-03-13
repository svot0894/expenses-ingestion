import json
import streamlit as st
from ..backend.core.google_drive_handler import GoogleDriveHandler

# Load credentials
SCOPES = st.secrets.google_drive_api.scopes
FOLDER_ID = st.secrets.google_drive_api.folder_id

st.title("Expenses Tracker")

if not st.experimental_user.is_logged_in:
    st.button("Log in with Google", on_click=st.login)
    st.stop()

st.button("Log out", on_click=st.logout)

uploaded_files = st.file_uploader(
    "Load here your expenses in CSV format.", type="csv", accept_multiple_files=True
)

if uploaded_files:
    drive_handler = GoogleDriveHandler(st.secrets)

    for uploaded_file in uploaded_files:
        # check for duplicate file
        if drive_handler.file_exists(uploaded_file.name, FOLDER_ID):
            st.warning(f"⚠️ File {uploaded_file.name} already exists in the folder.")
        else:
            drive_handler.upload_file(uploaded_file, FOLDER_ID)
            st.success(f"✅ File {uploaded_file.name} uploaded successfully.")
