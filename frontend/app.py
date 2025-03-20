"""Streamlit frontend for the Expenses Tracker application."""

import os
import sys
import hashlib
import streamlit as st

sys.path.append(os.getcwd())

from backend.core.google_drive_handler import GoogleDriveHandler
from backend.core.file_handler import ExpensesFile, FileHandler

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

        # Instantiate ExpensesFile
        expenses_file = ExpensesFile(
            file_name=uploaded_file.name,
            file_size=uploaded_file.size,
            number_of_rows=uploaded_file.read().count(b"\n"),
            checksum=hashlib.sha224(uploaded_file.read()).hexdigest(),
        )

        # Store file metadata to the database with store_file_metadata method
        file_handler = FileHandler()
        file_handler.store_file_metadata(expenses_file)

        # check for duplicate file
        if drive_handler.file_exists(uploaded_file.name, FOLDER_ID):
            st.warning(f"⚠️ File {uploaded_file.name} already exists in the folder.")
        else:
            drive_handler.upload_file(uploaded_file, FOLDER_ID)
            st.success(f"✅ File {uploaded_file.name} uploaded successfully.")
