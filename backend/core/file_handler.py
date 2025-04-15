import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, update, select, insert, text
from sqlalchemy.orm import sessionmaker
from backend.models.models import (
    Expense,
    FailedExpense,
    ExpensesFile,
    FileConfiguration,
)

load_dotenv()


class FileHandler:
    def __init__(self):
        self.database_url: str = os.getenv("DATABASE_URL")

        if not self.database_url:
            raise ValueError("DATABASE_URL not set in environment variables")

        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)

    def upload_file_metadata(self, file: ExpensesFile) -> tuple[bool, str]:
        """Store file metadata in the database"""
        session = self.Session()
        try:
            session.add(file)
            session.commit()
            return True, "File metadata stored successfully"
        except Exception as e:
            session.rollback()
            return False, f"An error occurred while storing file metadata: {e}"
        finally:
            session.close()

    def update_file_metadata(
        self, file_id: str, attribute: str, value: any
    ) -> tuple[bool, str]:
        """Update the passed attribute of a file in the database"""
        session = self.Session()
        try:
            statement = (
                update(ExpensesFile)
                .where(ExpensesFile.file_id == file_id)
                .values({attribute: value})
            )
            session.execute(statement)
            session.commit()
            return True, "File attribute updated successfully"
        except Exception as e:
            session.rollback()
            return False, f"An error occurred while updating file attribute: {e}"
        finally:
            session.close()

    def get_file_by_checksum(self, checksum: str) -> tuple[bool, str | dict]:
        """Check if a file with the given checksum exists in the database"""
        session = self.Session()
        try:
            response = (
                session.query(ExpensesFile)
                .filter(ExpensesFile.checksum == checksum)
                .first()
            )
            if response:
                return True, {"file_id": response.file_id}
            return False, "No file found with the given checksum"
        except Exception as e:
            return False, f"An error occurred while checking for checksum: {e}"
        finally:
            session.close()

    def determine_file_config_id(self, file_name: str) -> int:
        """Determine the file configuration ID based on the file name by comparing against existing patterns in file_pattern column of cfg_t_file_config table"""
        session = self.Session()
        try:
            statement = text(
                "SELECT config_id FROM config_sch.cfg_t_file_config WHERE :file_name ~ file_pattern"
            ).bindparams(file_name=file_name)
            response = session.execute(statement).first()

            if response:
                return int(response[0])  # Ensure the ID is returned as an integer
            else:
                return ValueError("No matching file configuration found.")
        except Exception as e:
            return RuntimeError(
                f"An error occurred while determining file configuration ID: {e}"
            )
        finally:
            session.close()

    def get_file_config(self, file_config_id: int) -> FileConfiguration:
        """Retrieve file configuration based on the file configuration ID"""
        session = self.Session()
        try:
            response = (
                session.query(FileConfiguration)
                .filter(FileConfiguration.config_id == file_config_id)
                .first()
            )
            if response:
                return response
            else:
                return ValueError("No file configuration found with the given ID.")
        except Exception as e:
            raise RuntimeError(
                f"An error occurred while retrieving file configuration: {e}"
            )
        finally:
            session.close()

    def get_all_files(self) -> tuple[bool, str | list]:
        """Retrieve all files from the database"""
        session = self.Session()
        try:
            response = session.query(ExpensesFile).all()
            return True, response
        except Exception as e:
            return False, f"An error occurred while retrieving files: {e}"
        finally:
            session.close()

    def insert_expenses(
        self, expense: Expense | FailedExpense, data_condition: str
    ) -> tuple[bool, str]:
        """
        Load data to the respective table based on the data condition (good or error).

        Parameters:
        - expense: Expense object or dict containing the data to be inserted.
        - data_condition: Condition to determine if the data is good or error.
        """
        session = self.Session()
        try:
            if data_condition == "good" and isinstance(expense, Expense):
                session.add(expense)
            elif data_condition == "error" and isinstance(expense, dict):
                session.add(expense)
            else:
                return False, "Invalid data type or condition"

            session.commit()
            return True, "Data inserted successfully"
        except Exception as e:
            session.rollback()
            return False, f"An error occurred while inserting data: {e}"
        finally:
            session.close()
