"""Streamlit frontend for the Expenses Tracker application."""

import os
import sys
import streamlit as st
import pandas as pd

sys.path.append(os.getcwd())

from backend.core.types import Result
from backend.ingestion.pipeline import pipeline
from backend.core.kdrive_handler import KDriveHandler
from backend.core.file_handler import FileHandler
from backend.models.models import Files, FileStatusEnum
from backend.validation.base_validator import FileValidatorPipeline
from backend.validation.validators.file_validators import (
    ChecksumValidator,
    SchemaValidator,
)

st.set_page_config(page_title="APP", layout="wide")

drive_handler = KDriveHandler(st.secrets)
file_handler = FileHandler()

st.title("Expenses Tracker")

# Bronze Layer: Upload files to Google Drive and validate them
st.subheader("📥 Upload Files")
uploaded_files = st.file_uploader(
    "Load here your expenses in CSV format.", type="csv", accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}...", show_time=True):

            rollback_actions = []

            try:
                file_content = uploaded_file.getvalue()

                determine_config_id_result = file_handler.determine_file_config_id(
                    uploaded_file.name
                )

                if not determine_config_id_result.success:
                    raise RuntimeError(
                        f"Failed to determine file config ID: {determine_config_id_result.message}"
                    )

                file_metadata = {
                    "file_name": uploaded_file.name,
                    "file_size": len(file_content),
                    "file_config_id": determine_config_id_result.data,
                }

                # Step 2: Setting up validators
                get_config_result = file_handler.get_file_config(
                    file_metadata["file_config_id"]
                )

                if not get_config_result.success:
                    raise RuntimeError(
                        f"Failed to get file config: {get_config_result.message}"
                    )

                validators = [
                    ChecksumValidator(),
                    SchemaValidator(
                        file_config=get_config_result.data,
                    ),
                ]
                validation_pipeline = FileValidatorPipeline(validators)

                # Step 3: Running validators
                validations_result = validation_pipeline.run_validations(
                    file_content, file_metadata
                )
                if not validations_result.success:
                    raise RuntimeError(
                        f"File didn't pass validations: {validations_result.message}"
                    )

                # Step 4: Upload to Google Drive
                file_upload_result = drive_handler.upload_file(
                    uploaded_file
                )

                if not file_upload_result.success:
                    raise Exception(f"File uploaded file: {file_upload_result.message}")

                # Register rollback: if error occurs later
                # Delete the uploaded file
                rollback_actions.append(
                    lambda: drive_handler.delete_file(file_upload_result.data)
                )

                # Step 5: Store metadata in database
                expenses_file = Files(
                    file_id=file_upload_result.data,
                    file_source=file_metadata["file_name"].split("_")[0],
                    file_name=file_metadata["file_name"],
                    file_size=file_metadata["file_size"],
                    number_rows=file_content.count(b"\n") - 1,
                    checksum=file_metadata["checksum"],
                    file_status_id=FileStatusEnum.UPLOADED.value,
                    file_config_id=file_metadata["file_config_id"],
                )

                upload_metadata_result = file_handler.upload_file_metadata(
                    expenses_file
                )

                if not upload_metadata_result.success:
                    raise Exception(f"{upload_metadata_result.message}")

                st.success(f"✅ File {uploaded_file.name} uploaded successfully.")

            except Exception as e:
                # trigger rollback actions
                for action in reversed(rollback_actions):
                    try:
                        action()
                    except Exception as rollback_error:
                        st.error(f"⚠️ Rollback failed: {rollback_error}")

                st.error(f"❌ Something went wrong: {str(e)}")

# File Processing Status
st.subheader("📊 File Processing Status")
st.caption("Select a file to start processing and track its status.")

#  Fetch all files from the database
get_all_files_result = file_handler.get_all_files()

if not get_all_files_result.success:
    st.error(f"Something went wrong: {get_all_files_result.message}")

# Display the files in a table format
df = pd.DataFrame(get_all_files_result.data)

#
CLICKED_FILE_ID = None
ACTION_RESULT = None

# create a header for the table
header_cols = st.columns([3, 1, 1, 2, 2], vertical_alignment="center")
header_cols[0].markdown("**File Name**")
header_cols[1].markdown("**Bytes**")
header_cols[2].markdown("**Rows**")
header_cols[3].markdown("**Status**")
header_cols[4].markdown("**Actions**")

# Display each file's information in a row
for i, row in df.iterrows():
    cols = st.columns([3, 1, 1, 2, 2], vertical_alignment="center")

    cols[0].write(row.file_name)
    cols[1].write(row.file_size)
    cols[2].write(row.number_rows)
    cols[3].write(FileStatusEnum(row.file_status_id).name)

    # Action buttons for each file
    with cols[4]:
        btn_cols = st.columns(2)
        # process button
        with btn_cols[0]:
            if row.file_status_id != FileStatusEnum.PROCESSED.value:
                if st.button(
                    "▶️",
                    key=f"file_{row.file_id}",
                    help="Process",
                    use_container_width=True,
                ):
                    CLICKED_FILE_ID = row.file_id
                    ACTION_RESULT = pipeline(row.file_id, int(row.file_config_id))

        # delete button
        with btn_cols[1]:
            if st.button(
                "❌",
                key=f"delete_{row.file_id}",
                help="Delete",
                use_container_width=True,
            ):
                delete_drive = drive_handler.delete_file(row.file_id)
                delete_rec = file_handler.delete_file_metadata(row.file_id)
                CLICKED_FILE_ID = row.file_id

                if delete_drive.success and delete_rec.success:
                    ACTION_RESULT = Result(
                        success=True, message="Deleted successfully."
                    )
                else:
                    ACTION_RESULT = Result(
                        success=False,
                        message=f"""
                        Error deleting file:
                        {delete_drive.message} / {delete_rec.message}
                        """,
                    )

if ACTION_RESULT:
    if ACTION_RESULT.success:
        st.success(f"✅ {ACTION_RESULT.message}")
    else:
        st.error(f"❌ {ACTION_RESULT.message}")
