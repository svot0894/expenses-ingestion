"""Streamlit frontend for the Expenses Tracker application."""

import os
import sys
import time
import streamlit as st
import pandas as pd

sys.path.append(os.getcwd())

from backend.core.google_drive_handler import GoogleDriveHandler
from backend.core.file_handler import FileHandler
from backend.models.expenses_file import ExpensesFile
from backend.validation.base_validator import FileValidatorPipeline
from backend.validation.validators.file_validators import ChecksumValidator, SchemaValidator

# Load credentials
SCOPES = st.secrets.google_drive_api.scopes
FOLDER_ID = st.secrets.google_drive_api.folder_id

# Initialize handlers
validators = [ChecksumValidator(), SchemaValidator(expected_schema={"TRANSACTION_DATE", "DESCRIPTION", "AMOUNT"})]
validation_pipeline = FileValidatorPipeline(validators)

drive_handler = GoogleDriveHandler(st.secrets)
file_handler = FileHandler()

st.title("Expenses Tracker")

# Bronze Layer: Upload files to Google Drive and validate them
st.subheader("📥 Upload Files")
uploaded_files = st.file_uploader(
    "Load here your expenses in CSV format.", type="csv", accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.status(f"Processing {uploaded_file.name}...", expanded=True) as status:

            rollback_actions = []

            try:
                st.write("🔄 **Step 1:** Reading file content...")
                file_content = uploaded_file.getvalue()
                file_metadata = {
                    "file_name": uploaded_file.name,
                    "file_size": len(file_content),
                }

                progress_bar = st.progress(10)
                time.sleep(0.5)

                # Step 2: Run validators
                st.write("🔍 **Step 2:** Running file validators...")
                is_valid, message = validation_pipeline.run_validations(file_content, file_metadata)

                if not is_valid:
                    raise Exception(f"Validation failed: {message}")

                progress_bar.progress(50)

                # Step 3: Upload to Google Drive
                st.write("☁️ **Step 3:** Uploading file to Google Drive...")
                is_valid, file_id, message = drive_handler.upload_file(uploaded_file, folder_id=FOLDER_ID)

                if not is_valid:
                    raise Exception(f"{message}")

                # Register rollback: if error occurs later, delete the uploaded file
                rollback_actions.append(lambda: drive_handler.delete_file(file_id))

                progress_bar.progress(80)

                # Step 4: Store metadata in database
                st.write("🗄️ **Step 4:** Storing file metadata...")

                expenses_file = ExpensesFile(
                    file_id=file_id,
                    file_name=file_metadata["file_name"],
                    file_size=file_metadata["file_size"],
                    number_rows=file_content.count(b"\n") - 1,  # exclude header
                    checksum=file_metadata["checksum"],
                )

                is_valid, message = file_handler.upload_file_metadata(expenses_file)
                if not is_valid:
                    raise Exception(f"{message}")

                progress_bar.progress(100)

                st.success(f"✅ File {uploaded_file.name} uploaded successfully.")
                status.update(label=f"✅ File {uploaded_file.name} uploaded successfully.", state="complete")

            except Exception as e:
                # Rollback actions
                for action in reversed(rollback_actions):
                    try:
                        action()
                    except Exception as rollback_error:
                        st.error(f"⚠️ Rollback failed: {rollback_error}")

                st.error(f"❌ {str(e)}")
                status.update(label=f"🚨 Error: {uploaded_file.name} processing failed", state="error")

            finally:
                progress_bar.empty()

# File Processing Status
st.subheader("📊 File Processing Status")

is_valid, file_list = file_handler.get_all_files()

if not file_list:
    st.info("No files found in the database.")
else:
    df = pd.DataFrame(file_list)

    status_text = {
        1: "🟡 Pending",
        2: "🔵 Processing",
        3: "✅ Completed",
        4: "❌ Failed",
    }

    df["status"] = df["file_status_id"].map(status_text)
    df = df[["file_id", "file_name", "number_rows", "inserted_datetime", "ingested_datetime", "status"]]

    selected_rows = st.dataframe(df, use_container_width=True, on_select="rerun")

    if selected_rows.selection["rows"]:
        selected_file = df.iloc[selected_rows.selection["rows"][0]]
        st.session_state.selected_file = selected_file
