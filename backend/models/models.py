from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    Float,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import hashlib

Base = declarative_base()


class BaseModel:
    """Base model for all database models"""

    __abstract__ = True

    def model_dump(self, mode="json"):
        """Dump the model data in the specified format (default is JSON)"""
        if mode == "json":

            def serialize(value):
                if isinstance(value, datetime):
                    return value.isoformat()
                return value

            return {
                column.name: serialize(getattr(self, column.name))
                for column in self.__table__.columns
            }
        return None


class FileConfiguration(Base, BaseModel):
    """Configuration for file processing"""

    __tablename__ = "cfg_t_file_config"
    __table_args__ = {"schema": "config_sch"}

    config_id = Column(Integer, primary_key=True)
    file_pattern = Column(String, nullable=False)
    date_format = Column(String, default="%d.%m.%y", nullable=False)
    amount_sign = Column(Integer, default=1, nullable=False)  # 1 or -1
    delimiter = Column(String, default=",", nullable=False)
    decimal_separator = Column(String, default=".", nullable=False)
    encoding = Column(String, default="Windows-1252", nullable=True)
    description = Column(String, default="", nullable=False)


class FileStatus(Base, BaseModel):
    """Status of the file processing"""

    __tablename__ = "cfg_t_file_status"
    __table_args__ = {"schema": "config_sch"}

    file_status_id = Column(Integer, primary_key=True)
    file_status_name = Column(String(255), unique=True, nullable=False)
    description = Column(String, nullable=True)


class ExpensesFile(Base, BaseModel):
    """File containing expenses data"""

    __tablename__ = "cfg_t_files"
    __table_args__ = {"schema": "config_sch"}

    def __init__(self, **kwargs):
        """Initialize the ExpensesFile model"""
        # Set default values for columns with defaults if not provided
        if "file_status_id" not in kwargs:
            kwargs["file_status_id"] = 1
        if "active" not in kwargs:
            kwargs["active"] = True
        if "inserted_datetime" not in kwargs:
            kwargs["inserted_datetime"] = datetime.today()
        super().__init__(**kwargs)

    file_id = Column(String, primary_key=True)
    account_type = Column(String(3), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    number_rows = Column(Integer, nullable=False)
    checksum = Column(String(255), unique=True, nullable=False)
    file_status_id = Column(
        Integer,
        ForeignKey("config_sch.cfg_t_file_status.file_status_id"),
        nullable=False,
    )
    file_config_id = Column(
        Integer, ForeignKey("config_sch.cfg_t_file_config.config_id"), nullable=True
    )
    active = Column(Boolean, default=True, nullable=False)
    error_message = Column(String, nullable=True)
    inserted_datetime = Column(DateTime, nullable=False)
    ingested_datetime = Column(DateTime, nullable=True)

    @staticmethod
    def generate_checksum(content: str) -> str:
        """Generate a checksum for the file content"""
        return hashlib.sha224(content).hexdigest()


class Expense(Base, BaseModel):
    """Expense record"""

    __tablename__ = "s_t_expenses"
    __table_args__ = {"schema": "s_sch"}

    expense_id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(
        String, ForeignKey("config_sch.cfg_t_files.file_id"), nullable=False
    )
    transaction_date = Column(Date, nullable=False)
    description = Column(String(255))
    amount = Column(Float, nullable=False)
    account = Column(String(255), nullable=True)


class FailedExpense(Base, BaseModel):
    """Failed expense record"""

    __tablename__ = "s_t_expenses_failed"
    __table_args__ = {"schema": "s_sch"}

    failed_expense_id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(
        String, ForeignKey("config_sch.cfg_t_files.file_id"), nullable=False
    )
    transaction_date = Column(String, nullable=True)
    description = Column(String, nullable=True)
    amount = Column(String, nullable=True)
    account = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
