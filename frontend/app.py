"""Streamlit frontend for the Expenses Tracker application."""

import os
import sys
import streamlit as st

sys.path.append(os.getcwd())

from backend.core.google_drive_handler import GoogleDriveHandler
from backend.core.file_handler import FileHandler
from backend.models.expenses_file import ExpensesFile

# Load credentials
SCOPES = st.secrets.google_drive_api.scopes
FOLDER_ID = st.secrets.google_drive_api.folder_id

st.title("Expenses Tracker")

uploaded_files = st.file_uploader(
    "Load here your expenses in CSV format.", type="csv", accept_multiple_files=True
)

if uploaded_files:
    drive_handler = GoogleDriveHandler(st.secrets)
    file_handler = FileHandler()

    for uploaded_file in uploaded_files:

        # store file content in a temporary variable
        file_content = uploaded_file.getvalue()

        # create ExpensesFile object
        expenses_file = ExpensesFile(
            file_name=uploaded_file.name,
            file_size=len(file_content),
            number_rows=file_content.count(b"\n") - 1, # exclude header
            checksum=ExpensesFile.generate_checksum(file_content),
        )

        # TODO: run validation against file

        # upload file metadata
        file_handler.upload_file_metadata(expenses_file)

        # check for duplicate file
        if drive_handler.file_exists(uploaded_file.name, FOLDER_ID):
            st.warning(f"⚠️ File {uploaded_file.name} already exists in the folder.")
        else:
            drive_handler.upload_file(uploaded_file, FOLDER_ID)
            st.success(f"✅ File {uploaded_file.name} uploaded successfully.")
