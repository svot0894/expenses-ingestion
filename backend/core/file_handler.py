import os
from dotenv import load_dotenv
from supabase import create_client, Client
from pydantic import BaseModel

load_dotenv()


class ExpensesFile(BaseModel):
    """Model for expenses file"""

    file_name: str
    file_size: int
    number_of_rows: int
    checksum: str


class FileHandler:
    def __init__(self):
        supabase_url: str = os.getenv("SUPABASE_URL")
        supabase_key: str = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def store_file_metadata(self, file: ExpensesFile):
        """Store file metadata in the database"""
        self.supabase.table("b_sch.b_t_expenses").insert(
            [
                {
                    "file_name": file.file_name,
                    "file_size": file.file_size,
                    "number_of_rows": file.number_of_rows,
                    "checksum": file.checksum,
                }
            ]
        ).execute()
        return "File metadata stored successfully"
