from typing import Any
from backend.core.types import Result
from sqlalchemy import update, text
from backend.core.database_handler import DatabaseHandler
from backend.models.models import (
    Expense,
    FailedExpense,
    Files,
    FileConfiguration,
)


class FileHandler:
    """
    A class to handle file operations.
    """

    def __init__(self):
        self.db_handler = DatabaseHandler()

    def upload_file_metadata(self, file: Files) -> Result:
        """Store file metadata in the database"""
        with self.db_handler.get_db_session() as session:
            try:
                session.add(file)

                return Result(
                    success=True, message="File metadata stored successfully."
                )
            except Exception as e:
                session.rollback()
                return Result(
                    success=False,
                    message=f"An error occurred while storing file metadata: {e}",
                )

    def update_file_metadata(self, file_id: str, attribute: str, value: Any) -> Result:
        """Update the passed attribute of a file in the database"""
        with self.db_handler.get_db_session() as session:
            try:
                statement = (
                    update(Files)
                    .where(Files.file_id == file_id)
                    .values({attribute: value})
                )
                session.execute(statement)

                return Result(
                    success=True, message="File attribute updated successfully."
                )
            except Exception as e:
                session.rollback()
                return Result(
                    success=False,
                    message=f"An error occurred while updating file attribute: {e}",
                )

    def get_file_by_checksum(self, checksum: str) -> Result:
        """Check if a file with the given checksum exists in the database"""
        with self.db_handler.get_db_session() as session:
            try:
                response = (
                    session.query(Files).filter(Files.checksum == checksum).first()
                )
                if response:
                    return Result(success=True, data={"file_id": response.file_id})
                return Result(
                    success=False, message="No file found with the given checksum"
                )
            except Exception as e:
                return Result(
                    success=False,
                    message=f"An error occurred while checking for checksum: {e}",
                )

    def determine_file_config_id(self, file_name: str) -> Result:
        """Determine the file configuration ID based on the file name by comparing against existing patterns in file_pattern column of cfg_t_file_config table"""
        with self.db_handler.get_db_session() as session:
            try:
                statement = text(
                    "SELECT config_id FROM cfg_sch.cfg_t_file_config WHERE :file_name ~ file_pattern"
                ).bindparams(file_name=file_name)
                response = session.execute(statement).first()

                if response:
                    return Result(
                        success=True, data=int(response[0])
                    )  # Ensure the ID is returned as an integer
                else:
                    return Result(
                        success=False, message="No matching file configuration found."
                    )
            except Exception as e:
                return Result(
                    success=False,
                    message=f"An error occurred while determining file configuration ID: {e}",
                )

    def get_file_config(self, file_config_id: int) -> Result:
        """Retrieve file configuration based on the file configuration ID"""
        with self.db_handler.get_db_session() as session:
            try:
                response = (
                    session.query(FileConfiguration)
                    .filter(FileConfiguration.config_id == file_config_id)
                    .first()
                )
                if response:
                    session.expunge(response)
                    return Result(success=True, data=response)
                else:
                    return Result(
                        success=False,
                        message="No file configuration found with the given ID.",
                    )
            except Exception as e:
                return Result(
                    success=False,
                    message=f"An error occurred while retrieving file configuration: {e}",
                )

    def get_all_files(self) -> Result:
        """Retrieve all files from the database"""
        with self.db_handler.get_db_session() as session:
            try:
                response = session.query(Files).all()
                # serialize objects while the session is still open
                serialized_files = [
                    file_instance.model_dump(mode="json") for file_instance in response
                ]
                return Result(success=True, data=serialized_files)
            except Exception as e:
                return Result(
                    success=False,
                    message=f"An error occurred while retrieving files: {e}",
                )

    def insert_expenses(
        self, expense: Expense | FailedExpense, data_condition: str
    ) -> Result:
        """
        Load data to the respective table based on the data condition (good or error).

        Parameters:
        - expense: Expense object or dict containing the data to be inserted.
        - data_condition: Condition to determine if the data is good or error.
        """
        with self.db_handler.get_db_session() as session:
            try:
                if data_condition == "good" and isinstance(expense, Expense):
                    session.add(expense)
                elif data_condition == "error" and isinstance(expense, FailedExpense):
                    session.add(expense)
                else:
                    return Result(
                        success=False, message="Invalid data type or condition"
                    )

                return Result(success=True, message="Data inserted successfully")
            except Exception as e:
                session.rollback()
                return Result(
                    success=False,
                    message=f"An error occurred while inserting data: {e}",
                )
