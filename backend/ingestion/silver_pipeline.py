"""
This module contains the task to load the files stored in Google Drive to the silver layer.
"""

from io import BytesIO
import pandas as pd
import streamlit as st
from backend.core.types import Result
from backend.core.google_drive_handler import GoogleDriveHandler
from backend.core.file_handler import FileHandler
from backend.models.models import Expense, FailedExpense
from backend.validation.base_validator import DataFrameValidatorPipeline
from backend.validation.validators.expense_validators import (
    DuplicatesValidator,
    DateFormatValidator,
)
from backend.validation.cleaning.expense_cleaners import (
    TrimColumnCleaner,
    FormatDateCleaner,
    FormatAmountSignCleaner,
)
from backend.validation.cleaning.base_cleaner import CleaningPipeline


def silver_pipeline(file_id: str, file_config_id: int) -> Result:
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
    drive_handler = GoogleDriveHandler(st.secrets)
    file_handler = FileHandler()

    try:
        # STEP 1: Download the file from Google Drive
        result = drive_handler.download_file(file_id)

        if not result.success:
            return Result(
                success=False,
                message=f"""
                Failed to download file with ID: {file_id}.
                Reason: {result.message}""",
            )

        file_content = result.data

        # STEP 2: Fetch file configuration from the database
        result = file_handler.get_file_config(file_config_id)

        if not result.success:
            return Result(
                success=False,
                message=f"""
                Failed to fetch file configuration with ID: {file_config_id}.
                Reason: {result.message}""",
            )

        file_config = result.data

        # STEP 3: Read the file in CSV format
        try:
            df = pd.read_csv(
                BytesIO(file_content),
                encoding=file_config.encoding,
                sep=file_config.delimiter,
                decimal=file_config.decimal_separator,
            )
        except Exception as e:
            return Result(
                success=False,
                message=f"Failed to read file content: {e}",
            )

        # STEP 4: Run validators
        validators = [
            DuplicatesValidator(),
            DateFormatValidator(file_config.date_format),
        ]

        validator_pipeline = DataFrameValidatorPipeline(validators)
        validation_result = validator_pipeline.run_validations(df)

        df = validation_result.data

        valid_rows = df[df["is_valid"]].copy()
        failed_rows = df[~df["is_valid"]].copy()

        # STEP 5: Clean valid rows
        cleaners = [
            TrimColumnCleaner(),
            FormatDateCleaner(file_config.date_format),
            FormatAmountSignCleaner(file_config.amount_sign),
        ]
        cleaning_pipeline = CleaningPipeline(cleaners)

        valid_expenses = []

        for _, row in valid_rows.iterrows():
            cleaned_row = cleaning_pipeline.run(row)
            try:
                expense = Expense(
                    file_id=file_id,
                    transaction_date=cleaned_row.TRANSACTION_DATE,
                    amount=cleaned_row.AMOUNT,
                    description=cleaned_row.DESCRIPTION,
                    category=cleaned_row.CATEGORY,
                )
                valid_expenses.append(expense)
            except Exception as e:
                # add to failed_rows as well
                failed_rows = failed_rows.append(
                    {
                        **row.to_dict(),
                        "error_message": row.get("error_message", "")
                        + f"Cleaning error: {str(e)}",
                    },
                    ignore_index=True,
                )

        # STEP 7: Prepare FailedExpenses objects from failed_rows
        failed_expenses = []
        for _, row in failed_rows.iterrows():
            failed_expense = FailedExpense(
                file_id=file_id,
                transaction_date=str(row.TRANSACTION_DATE),
                amount=str(row.AMOUNT),
                description=str(row.DESCRIPTION),
                category=str(row.CATEGORY),
                error_message=str(row.error_message),
            )
            failed_expenses.append(failed_expense)

        # Step 8: Insert good data into s_t_expenses
        for expense in valid_expenses:
            result = file_handler.insert_expenses(expense, data_condition="good")

            if not result.success:
                return Result(
                    success=False,
                    message=f"""
                    Failed to insert data into the database.
                    Reason: {result.message}""",
                )

        # Step 9: Insert bad data into s_t_expenses_error
        for failed_expense in failed_expenses:
            result = file_handler.insert_expenses(
                failed_expense, data_condition="error"
            )

            if not result.success:
                return Result(
                    success=False,
                    message=f"""
                    Failed to insert error data into the database.
                    Reason: {result.message}""",
                )

        # STEP 10: Update the status and ingested datetime of the file
        if not failed_expenses:
            file_status = 3  # Completed
        elif valid_expenses and failed_expenses:
            file_status = 4  # Partially completed
        else:
            file_status = 9  # Failed

        try:
            file_handler.update_file_metadata(file_id, "file_status_id", file_status)
            file_handler.update_file_metadata(file_id, "ingested_datetime", "now()")
        except Exception as e:
            return Result(
                success=False,
                message=f"""
                Failed to update file metadata in the database.
                Reason: {str(e)}""",
            )

        # STEP 11: Return the result of the task
        return Result(success=True, message="Data loaded to the silver layer.")
    except Exception as e:
        return Result(success=False, message=str(e))
