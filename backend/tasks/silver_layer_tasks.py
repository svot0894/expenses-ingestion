"""
This module contains the task to load the files stored in Google Drive to the silver layer.
"""
import io
import pandas as pd
from backend.models.expenses_model import Expense
from backend.core.google_drive_handler import GoogleDriveHandler
from backend.core.file_handler import FileHandler


def load_data_to_silver(file_id: str, drive_handler: GoogleDriveHandler, file_handler: FileHandler) -> tuple[bool, str]:
    """
    Task to load the files stored in Google Drive to the silver layer.
    This task:
    - Downloads the file from Google Drive
    - Reads the file in CSV format
    - Validates: no duplicates, data types, date format, etc.
    -   Good data moves to s_t_expenses
    -   Bad data moves to s_t_expenses_error
    - Updates the status of the file in the database
    """

    try:
        # STEP 1: Download the file from Google Drive
        is_valid, file_content = drive_handler.download_file(file_id)

        if not is_valid:
            raise Exception(f"Failed to download file with ID: {file_id}")

        # STEP 2: Read the file in CSV format
        try:
            df = pd.read_csv(io.BytesIO(file_content), encoding="Windows-1252", sep=";")
        except Exception as e:
            raise Exception(f"Failed to read file content: {e}")
        
        # STEP 3: Clean the data TODO: this should be in a separate pipeline
        try:
            # Remove leading and trailing whitespace from column names
            df.columns = df.columns.str.strip()

            # Convert the transaction_date column to date format (eg. 25.02.25)
            df["TRANSACTION_DATE"] = pd.to_datetime(df["TRANSACTION_DATE"], format="mixed")

            # Convert the amount column to float format
            df["AMOUNT"] = pd.to_numeric(df["AMOUNT"])

        except Exception as e:
            raise Exception(f"Failed to clean data: {e}")
        

        # STEP 3: Convert data into a list of Expense objects
        expenses = []
        failed_expenses = []

        for _, row in df.iterrows():
            try:
                expense = Expense(
                    file_id=file_id,
                    transaction_date=row["TRANSACTION_DATE"],
                    amount=row["AMOUNT"],
                    description=row["DESCRIPTION"]
                )
                expenses.append(expense)
            except Exception as e:
                failed_expense = {
                    "file_id": file_id,
                    "transaction_date": str(row["TRANSACTION_DATE"]),
                    "amount": str(row["AMOUNT"]),
                    "description": str(row["DESCRIPTION"]),
                    "error_message": str(e)
                }
                failed_expenses.append(failed_expense)

        # STEP 4: Insert the data into the database

        # Insert good data into s_t_expenses
        for expense in expenses:
            is_valid, message = file_handler.insert_expenses(expense, data_condition="good")

            if not is_valid:
                raise Exception(f"Failed to insert data into the database: {message}")

        # Insert bad data into s_t_expenses_error
        for failed_expense in failed_expenses:
            is_valid, message = file_handler.insert_expenses(failed_expense, data_condition="error")
        
        if not is_valid:
            raise Exception(f"Failed to insert error data into the database: {message}")
        

        # STEP 5: Update the status and ingested datetime of the file in the database
        if not failed_expenses:
            file_status = 3  # Completed
        elif expenses and failed_expenses:
            file_status = 4 # Partially completed
        else:
            file_status = 9 # Failed

        file_handler.update_file_metadata(file_id, "file_status_id", file_status)
        file_handler.update_file_metadata(file_id, "ingested_datetime", "now()")

        # STEP 6: Return the result of the task
        return True, "File loaded successfully to the silver layer."
    except Exception as e:
        return False, str(e)