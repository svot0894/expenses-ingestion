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

    def upload_file_metadata(self, file: ExpensesFile) -> tuple[bool, str]:
        """Store file metadata in the database"""
        try:
            self.supabase.schema("config_sch").table("cfg_t_files").insert(
                [
                    file.model_dump(mode="json"),
                ]
            ).execute()
            return True, "File metadata stored successfully"
        except Exception as e:
            return False, f"An error occurred while storing file metadata: {e}"

    def get_file_by_checksum(self, checksum: str) -> tuple[bool, str | dict]:
        """Check if a file with the given checksum exists in the database"""
        try:
            response = self.supabase.schema("config_sch").table("cfg_t_files").select("file_id").eq("checksum", checksum).execute()
            if response.data:
                return True, response.data
            return False, "No file found with the given checksum"
        except Exception as e:
            return False, f"An error occurred while checking for checksum: {e}"

    def get_all_files(self) -> tuple[bool, str | list]:
        """Retrieve all files from the database"""
        try:
            response = self.supabase.schema("config_sch").table("cfg_t_files").select("*").execute()
            return True, response.data
        except Exception as e:
            return False, f"An error occurred while retrieving files: {e}"
