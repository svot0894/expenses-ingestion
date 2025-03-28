"""Streamlit frontend for the Expenses Tracker application."""

import os
import sys
import time
import streamlit as st

sys.path.append(os.getcwd())

from backend.core.google_drive_handler import GoogleDriveHandler
from backend.core.file_handler import FileHandler
from backend.models.expenses_file import ExpensesFile
from backend.validation.file_validators import ChecksumValidator, SchemaValidator, FileValidatorPipeline

# Load credentials
SCOPES = st.secrets.google_drive_api.scopes
FOLDER_ID = st.secrets.google_drive_api.folder_id

st.title("Expenses Tracker")

uploaded_files = st.file_uploader(
    "Load here your expenses in CSV format.", type="csv", accept_multiple_files=True
)

if uploaded_files:
    validators = [ChecksumValidator(), SchemaValidator(expected_schema={"TRANSACTION_DATE", "DESCRIPTION", "AMOUNT"})]
    validation_pipeline = FileValidatorPipeline(validators)

    drive_handler = GoogleDriveHandler(st.secrets)
    file_handler = FileHandler()

    for uploaded_file in uploaded_files:
        with st.status(f"Processing {uploaded_file.name}...", expanded=True) as status:

            st.write("🔄 **Step 1:** Reading file content...")
        
            # file content
            file_content = uploaded_file.getvalue()
            file_metadata = {
                "file_name": uploaded_file.name,
                "file_size": len(file_content)
            }

            # progress bar
            progress_bar = st.progress(10)
            time.sleep(1)

            # run validators against file
            st.write("🔍 **Step 2:** Running file validators...")
            is_valid, message = validation_pipeline.run_validations(file_content, file_metadata)

            if not is_valid:
                st.error(f"❌ {message}")
                status.update(label=f"🚨 Error: {uploaded_file.name} validation failed", state="error")
                break
            else:
                progress_bar.progress(50)

                # Upload file to Google Drive
                st.write("☁️ **Step 3:** Uploading file to Google Drive...")
                drive_handler.upload_file(uploaded_file, folder_id=FOLDER_ID)
                progress_bar.progress(80)

                st.write("🗄️ **Step 4:** Storing file metadata...")

                # create ExpensesFile object
                expenses_file = ExpensesFile(
                    file_name=file_metadata["file_name"],
                    file_size=file_metadata["file_size"],
                    number_rows=file_content.count(b"\n") - 1, # exclude header
                    checksum=file_metadata["checksum"],
                )

                file_handler.upload_file_metadata(expenses_file)
                progress_bar.progress(100)
                st.success(f"✅ File {uploaded_file.name} uploaded successfully.")
                status.update(label=f"✅ File {uploaded_file.name} uploaded successfully.", state="complete")
