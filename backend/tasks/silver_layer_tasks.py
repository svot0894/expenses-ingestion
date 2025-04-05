from celery import Celery

# Celery configuration
app = Celery('silver_ingestion', broker='redis://localhost:6379/0')


@app.task
def load_data_to_silver(file_id: str):
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

    # STEP 1: Download the file from Google Drive

    # STEP 2: Read the file in CSV format

    # STEP 3: Convert data into a list of Expense objects

    # STEP 4: Insert the data into the database

    # STEP 5: Update the status of the file in the database

    # STEP 6: Handle errors and rollback if necessary

    # STEP 7: Return the result of the task