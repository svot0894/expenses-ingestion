import os
from dotenv import load_dotenv
from supabase import create_client, Client
from backend.models.expenses_file import ExpensesFile

load_dotenv()


class FileHandler:
    def __init__(self):
        self.supabase_url: str = os.getenv("SUPABASE_URL")
        self.supabase_key: str = os.getenv("SUPABASE_SECRET_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("❌ Error: Missing Supabase URL or Secret Key in the .env file")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

    def upload_file_metadata(self, file: ExpensesFile):
        """Store file metadata in the database"""

        try:
            data = self.supabase.schema("config_sch").table("cfg_t_files").insert(
            [
                file.model_dump(mode="json"),
            ]
            ).execute()
            print(file.model_dump_json())
            return "File metadata stored successfully"
        except Exception as e:
            print(f"An error occurred while storing file metadata: {e}")
            return "Failed to store file metadata"
