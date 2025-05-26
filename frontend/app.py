"""Streamlit frontend for the Expenses Tracker application."""

import os
import sys
import streamlit as st
import pandas as pd

sys.path.append(os.getcwd())

from backend.core.google_drive_handler import GoogleDriveHandler
from backend.core.file_handler import FileHandler
from backend.models.models import Files
from backend.validation.base_validator import FileValidatorPipeline
from backend.validation.validators.file_validators import (
    ChecksumValidator,
    SchemaValidator,
)
from backend.ingestion.silver_layer import load_data_to_silver

# Load credentials
SCOPES = st.secrets.google_drive_api.scopes
FOLDER_ID = st.secrets.google_drive_api.folder_id

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
                st.write("🔄 **Step 1:** Creating file metadata...")
                file_content = uploaded_file.getvalue()

                determine_config_id_result = file_handler.determine_file_config_id(uploaded_file.name)

                if not determine_config_id_result.success:
                    raise RuntimeError(f"Failed to determine file config ID: {determine_config_id_result.message}")

                file_metadata = {
                    "file_name": uploaded_file.name,
                    "file_size": len(file_content),
                    "file_config_id": determine_config_id_result.data
                }

                progress_bar = st.progress(20)

                # Step 2: Setting up validators
                st.write("🔍 **Step 2:** Setting up file validators...")

                get_config_result = file_handler.get_file_config(
                    file_metadata["file_config_id"]
                )

                if not get_config_result.success:
                    raise RuntimeError(f"Failed to get file config: {get_config_result.message}")

                validators = [
                    ChecksumValidator(),
                    SchemaValidator(
                        file_config=get_config_result.data,
                    ),
                ]
                validation_pipeline = FileValidatorPipeline(validators)

                progress_bar.progress(40)

                # Step 3: Running validators
                st.write("🔍 **Step 3:** Running file validators...")

                validations_result = validation_pipeline.run_validations(
                    file_content, file_metadata
                )
                if not validations_result.success:
                    raise RuntimeError(f"File didn't pass validations: {validations_result.message}")

                progress_bar.progress(60)

                # Step 4: Upload to Google Drive
                st.write("☁️ **Step 4:** Uploading file to Google Drive...")
                file_upload_result = drive_handler.upload_file(
                    uploaded_file, folder_id=FOLDER_ID
                )

                if not file_upload_result.success:
                    raise Exception(f"{file_upload_result.message}")

                # Register rollback: if error occurs later, delete the uploaded file
                rollback_actions.append(lambda: drive_handler.delete_file(file_upload_result.data))

                progress_bar.progress(80)

                # Step 5: Store metadata in database
                st.write("🗄️ **Step 5:** Storing file metadata...")

                expenses_file = Files(
                    file_id=file_upload_result.data,
                    file_source=file_metadata["file_name"].split("_")[0],
                    file_name=file_metadata["file_name"],
                    file_size=file_metadata["file_size"],
                    number_rows=file_content.count(b"\n") - 1,  # exclude header
                    checksum=file_metadata["checksum"],
                    file_status_id=1,  # 1 = uploaded
                    file_config_id=file_metadata["file_config_id"],
                )

                upload_metadata_result = file_handler.upload_file_metadata(expenses_file)

                if not upload_metadata_result.success:
                    raise Exception(f"{upload_metadata_result.message}")

                progress_bar.progress(100)

                st.success(f"✅ File {uploaded_file.name} uploaded successfully.")
                status.update(
                    label=f"✅ File {uploaded_file.name} uploaded successfully.",
                    state="complete",
                )

            except Exception as e:
                # trigger rollback actions
                for action in reversed(rollback_actions):
                    try:
                        action()
                    except Exception as rollback_error:
                        st.error(f"⚠️ Rollback failed: {rollback_error}")

                st.error(f"❌ {str(e)}")
                status.update(
                    label=f"🚨 Error: {uploaded_file.name} processing failed",
                    state="error",
                )

            finally:
                progress_bar.empty()

# File Processing Status
st.subheader("📊 File Processing Status")
st.caption("Select a file to start processing and track its status.")

get_all_files_result = file_handler.get_all_files()

if not get_all_files_result.success:
    st.error({get_all_files_result.data})
else:
    data = [expense_instance.model_dump(mode="json") for expense_instance in get_all_files_result.data]
    df = pd.DataFrame(data)

    selected_rows = st.dataframe(df, use_container_width=True, on_select="rerun")

    if selected_rows.selection["rows"]:
        selected_file = df.iloc[selected_rows.selection["rows"][0]]

        if selected_file.file_status_id != 3:
            load_silver_result = load_data_to_silver(
                selected_file.file_id,
                int(selected_file.file_config_id),
                drive_handler,
                file_handler,
            )

            if not load_silver_result.success:
                st.error(f"❌ {load_silver_result.message}")
            else:
                st.success("✅ File processed successfully.")
        else:
            st.warning("This file has already been processed.")
