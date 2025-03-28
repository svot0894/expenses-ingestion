"""Streamlit frontend for the Expenses Tracker application."""

import os
import sys
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
        
        # file content
        file_content = uploaded_file.getvalue()
        file_metadata = {
            "file_name": uploaded_file.name,
            "file_size": len(file_content)
        }

        # run validators against file
        is_valid, message = validation_pipeline.run_validations(file_content, file_metadata)

        if not is_valid:
            st.warning(message)
            break
        else:
            # create ExpensesFile object
            expenses_file = ExpensesFile(
                file_name=file_metadata["file_name"],
                file_size=file_metadata["file_size"],
                number_rows=file_content.count(b"\n") - 1, # exclude header
                checksum=file_metadata["checksum"],
            )

            # upload file metadata
            file_handler.upload_file_metadata(expenses_file)
            st.success(f"✅ File {uploaded_file.name} uploaded successfully.")
