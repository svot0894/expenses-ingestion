"""Streamlit frontend for the Expenses Tracker application."""

import os
import sys
import streamlit as st

sys.path.append(os.getcwd())

from backend.core.google_drive_handler import GoogleDriveHandler

# Load credentials
SCOPES = st.secrets.google_drive_api.scopes
FOLDER_ID = st.secrets.google_drive_api.folder_id

st.title("Expenses Tracker")

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
