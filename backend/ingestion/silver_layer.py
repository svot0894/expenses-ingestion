"""
This module contains the task to load the files stored in Google Drive to the silver layer.
"""

from io import BytesIO
import pandas as pd
from backend.core.google_drive_handler import GoogleDriveHandler
from backend.core.file_handler import FileHandler
from backend.models.models import Expense, FailedExpense
from backend.validation.base_validator import RowValidatorPipeline
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


def load_data_to_silver(
    file_id: str,
    file_config_id: int,
    drive_handler: GoogleDriveHandler,
    file_handler: FileHandler,
) -> tuple[bool, str]:
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

        # STEP 2: Fetch file configuration from the database
        file_config = file_handler.get_file_config(file_config_id)

        # STEP 3: Read the file in CSV format
        try:
            df = pd.read_csv(
                BytesIO(file_content),
                encoding=file_config.encoding,
                sep=file_config.delimiter,
                decimal=file_config.decimal_separator,
            )
        except Exception as e:
            raise Exception(f"Failed to read file content: {e}")

        # STEP 4: Run validators
        validators = [
            DuplicatesValidator(),
            DateFormatValidator(file_config.date_format),
        ]

        validator_pipeline = RowValidatorPipeline(validators)

        valid_expenses = []
        failed_expenses = []

        for _, row in df.iterrows():
            is_valid, error_message = validator_pipeline.run_validations(row)

            if is_valid:
                # run cleaning steps
                cleaners = [
                    TrimColumnCleaner(),
                    FormatDateCleaner(file_config.date_format),
                    FormatAmountSignCleaner(file_config.amount_sign),
                ]

                cleaning_pipeline = CleaningPipeline(cleaners)
                cleaned_rows = cleaning_pipeline.run(row)

                expense = Expense(
                    file_id=file_id,
                    transaction_date=cleaned_rows.transaction_date,
                    amount=cleaned_rows.amount,
                    description=cleaned_rows.description,
                )
                valid_expenses.append(expense)
            else:
                # run error handling steps
                failed_expense = FailedExpense(
                    file_id=file_id,
                    transaction_date=str(row.transaction_date),
                    amount=str(row.amount),
                    description=str(row.description),
                    error_message=error_message,
                )
                failed_expenses.append(failed_expense)

        # STEP 6: Insert the data into the database

        # Insert good data into s_t_expenses
        for expense in valid_expenses:
            is_valid, message = file_handler.insert_expenses(
                expense, data_condition="good"
            )

            if not is_valid:
                raise Exception(f"Failed to insert data into the database: {message}")

        # Insert bad data into s_t_expenses_error
        for failed_expense in failed_expenses:
            is_valid, message = file_handler.insert_expenses(
                failed_expense, data_condition="error"
            )

        if not is_valid:
            raise Exception(f"Failed to insert error data into the database: {message}")

        # STEP 7: Update the status and ingested datetime of the file in the database
        if not failed_expenses:
            file_status = 3  # Completed
        elif valid_expenses and failed_expenses:
            file_status = 4  # Partially completed
        else:
            file_status = 9  # Failed

        file_handler.update_file_metadata(file_id, "file_status_id", file_status)
        file_handler.update_file_metadata(file_id, "ingested_datetime", "now()")

        # STEP 8: Return the result of the task
        return True, "File loaded successfully to the silver layer."
    except Exception as e:
        return False, str(e)
