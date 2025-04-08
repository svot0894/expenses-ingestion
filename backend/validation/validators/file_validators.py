import csv
from io import StringIO
from backend.validation.base_validator import BaseValidator
from backend.core.file_handler import FileHandler
from backend.models.models import ExpensesFile


class ChecksumValidator(BaseValidator):
    """Validator to check if a file with the same checksum already exists."""

    def __init__(self):
        self.file_handler = FileHandler()

    def validate(self, file_content: bytes, file_metadata: dict) -> tuple[bool, str]:
        checksum = ExpensesFile.generate_checksum(file_content)
        file_found, message = self.file_handler.get_file_by_checksum(checksum)

        if file_found:
            return False, f"⚠️ Duplicated file detected: {file_metadata['file_name']}"
        
        file_metadata["checksum"] = checksum
        return True, "File is unique."

class SchemaValidator(BaseValidator):
    """Validator to check if the file schema is valid."""

    def __init__(self, expected_schema: dict):
        self.expected_schema = expected_schema

    def validate(self, file_content: str, file_metadata: dict) -> tuple[bool, str]:
        try:
            decoded_content = file_content.decode("Windows-1252")
        except UnicodeDecodeError:
            return False, "⚠️ File encoding is not Windows-1252."
        
        reader = csv.reader(StringIO(decoded_content), delimiter=";")
        header = next(reader, None)

        if not header:
            return False, "⚠️ File is empty or has no header."
        
        missing_columns = self.expected_schema - set(header)

        if missing_columns:
            return False, f"⚠️ Missing columns: {', '.join(missing_columns)}"
        
        return True, "File schema is valid."