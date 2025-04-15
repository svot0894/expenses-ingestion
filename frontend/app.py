"""Streamlit frontend for the Expenses Tracker application."""

import os
import sys
import time
import streamlit as st
import pandas as pd

sys.path.append(os.getcwd())

from backend.core.google_drive_handler import GoogleDriveHandler
from backend.core.file_handler import FileHandler
from backend.models.models import ExpensesFile
from backend.validation.base_validator import FileValidatorPipeline
from backend.validation.validators.file_validators import (
    ChecksumValidator,
    SchemaValidator,
)
from backend.tasks.silver_layer_tasks import load_data_to_silver
from sqlalchemy import create_engine, text

# Load credentials
SCOPES = st.secrets.google_drive_api.scopes
FOLDER_ID = st.secrets.google_drive_api.folder_id

# Initialize handlers
validators = [
    ChecksumValidator(),
    SchemaValidator(
        expected_schema={"TRANSACTION_DATE", "DESCRIPTION", "AMOUNT", "ACCOUNT"}
    ),
]
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
                    "file_config_id": file_handler.determine_file_config_id(
                        uploaded_file.name
                    ),
                }

                progress_bar = st.progress(10)

                # Step 2: Run validators
                st.write("🔍 **Step 2:** Running file validators...")
                is_valid, message = validation_pipeline.run_validations(
                    file_content, file_metadata
                )

                if not is_valid:
                    raise Exception(f"File didn't pass validations: {message}")

                progress_bar.progress(50)

                # Step 3: Upload to Google Drive
                st.write("☁️ **Step 3:** Uploading file to Google Drive...")
                is_valid, file_id, message = drive_handler.upload_file(
                    uploaded_file, folder_id=FOLDER_ID
                )

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
                    account_type=file_metadata["file_name"].split("_")[0],
                    file_config_id=file_metadata["file_config_id"],
                )

                is_valid, message = file_handler.upload_file_metadata(expenses_file)

                if not is_valid:
                    raise Exception(f"{message}")

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

is_valid, file_list = file_handler.get_all_files()

if not file_list:
    st.info("No files found in the database.")
else:
    data = [expense_instance.model_dump(mode="json") for expense_instance in file_list]
    df = pd.DataFrame(data)

    selected_rows = st.dataframe(df, use_container_width=True, on_select="rerun")

    if selected_rows.selection["rows"]:
        selected_file = df.iloc[selected_rows.selection["rows"][0]]

        if selected_file.file_status_id != 3:
            is_valid, message = load_data_to_silver(
                selected_file.file_id,
                int(selected_file.file_config_id),
                drive_handler,
                file_handler,
            )

            if not is_valid:
                st.error(f"❌ {message}")
            else:
                st.success("✅ File processed successfully.")
        else:
            st.warning("This file has already been processed.")

st.subheader("Savings Rate")
# Query table g_sch.g_t_expenses and create a chart to show savings rate


# Initialize database connection
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

query = """
SELECT
    monthDate,
    savings / salary AS savings_rate,
    AVG(savings / salary) OVER (ORDER BY monthDate ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) AS avg_savings_rate_12_months
FROM (
    SELECT
        date_trunc('month', transaction_date) AS monthDate,
        sum(CASE WHEN account ILIKE 'compte épargne bonus%' THEN amount ELSE 0 END) AS savings,
        sum(CASE WHEN category = 'Salary' THEN amount ELSE 0 END) AS salary
    FROM g_sch.g_t_expenses
    GROUP BY date_trunc('month', transaction_date)
    ORDER BY date_trunc('month', transaction_date) ASC
) a;
"""

try:
    with engine.connect() as connection:
        result = connection.execute(text(query))
        data = result.fetchall()

    if not data:
        st.info("No data available for savings rate chart.")
    else:
        df = pd.DataFrame(
            data, columns=["monthDate", "savings_rate", "avg_savings_rate_12_months"]
        )
        df["monthDate"] = pd.to_datetime(df["monthDate"], utc=True)
        df.set_index("monthDate", inplace=True)

        st.line_chart(
            df[["savings_rate", "avg_savings_rate_12_months"]], use_container_width=True
        )
except Exception as e:
    st.error(f"❌ Failed to fetch data for savings rate chart: {str(e)}")
