from sqlmodel import SQLModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime
import hashlib


class FileStatus(SQLModel, table=True):
    __tablename__ = "cfg_t_file_status"
    __table_args__ = {"schema": "config_sch"}

    file_status_id: int = Field(primary_key=True)
    file_status_name: str = Field(max_length=255, unique=True)
    description: Optional[str] = None


class ExpensesFile(SQLModel, table=True):
    __tablename__ = "cfg_t_files"
    __table_args__ = {"schema": "config_sch"}

    file_id: UUID = Field(primary_key=True)
    file_name: str = Field(max_length=255)
    file_size: int
    number_rows: int
    checksum: str = Field(max_length=255, unique=True)
    file_status_id: int = Field(foreign_key="config_sch.cfg_t_file_status.file_status_id")
    active: bool = Field(default=True)
    error_message: Optional[str] = None
    inserted_datetime: datetime = Field(default_factory=datetime.today)
    ingested_datetime: Optional[datetime] = None

    @staticmethod
    def generate_checksum(content: str) -> str:
        return hashlib.sha224(content).hexdigest()