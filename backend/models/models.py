"""Database models for the expenses tracker application."""

from datetime import datetime
import enum
import hashlib
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    Numeric,
    ForeignKey,
    UniqueConstraint,
    func,
    Enum,
    text,
)
from sqlalchemy.ext.declarative import declarative_base

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


# configuration schema models
class FileConfiguration(Base, BaseModel):
    """Configuration for file processing in order to allow
    parsing of different file formats"""

    __tablename__ = "cfg_t_file_config"
    __table_args__ = {"schema": "cfg_sch"}

    config_id = Column(Integer, primary_key=True, autoincrement=True)
    file_pattern = Column(String, nullable=False, index=True)
    date_format = Column(String, server_default="%d.%m.%y", nullable=False)
    amount_sign = Column(Integer, server_default="1", nullable=False)
    delimiter = Column(String, server_default=",", nullable=False)
    decimal_separator = Column(String, server_default=".", nullable=False)
    encoding = Column(String, server_default="Windows-1252", nullable=False)
    expected_schema = Column(String, nullable=True)
    description = Column(String, default="", nullable=True)


class FileStatusEnum(enum.Enum):
    UPLOADED = 1
    IN_PROGRESS = 2
    PROCESSED = 3
    PARTIALLY_PROCESSED = 4
    FAILED = 9


class FileStatus(Base, BaseModel):
    """Status of the file processing"""

    __tablename__ = "cfg_t_file_status"
    __table_args__ = {"schema": "cfg_sch"}

    file_status_id = Column(Integer, primary_key=True, autoincrement=True)
    file_status_name = Column(Enum(FileStatusEnum), nullable=False)


class Files(Base, BaseModel):
    """Stores information about the uploaded files"""

    __tablename__ = "cfg_t_files"
    __table_args__ = {"schema": "cfg_sch"}

    file_id = Column(String, primary_key=True)
    file_source = Column(String(3), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    number_rows = Column(Integer, nullable=False)
    checksum = Column(String(255), unique=True, nullable=False)
    file_status_id = Column(
        Integer,
        ForeignKey("cfg_sch.cfg_t_file_status.file_status_id"),
        nullable=False,
    )
    file_config_id = Column(
        Integer, ForeignKey("cfg_sch.cfg_t_file_config.config_id"), nullable=False
    )
    active = Column(Boolean, server_default=text("true"), nullable=False)
    error_message = Column(String, nullable=True)
    inserted_datetime = Column(DateTime, server_default=func.now(), nullable=False)
    ingested_datetime = Column(DateTime, nullable=True)

    @staticmethod
    def generate_checksum(content: bytes) -> str:
        """Generate a checksum for the file content"""
        return hashlib.sha224(content).hexdigest()


# silver schema models
class Expense(Base, BaseModel):
    """Stores a single expense record"""

    __tablename__ = "s_t_expenses"
    __table_args__ = {"schema": "s_sch"}

    expense_id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(
        String,
        ForeignKey("cfg_sch.cfg_t_files.file_id", ondelete="CASCADE"),
        nullable=False,
    )
    transaction_date = Column(Date, nullable=False)
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    category = Column(String, nullable=True)
    account = Column(String, nullable=True)


class FailedExpense(Base, BaseModel):
    """Stores a single failed expense record"""

    __tablename__ = "s_t_expenses_failed"
    __table_args__ = {"schema": "s_sch"}

    failed_expense_id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(
        String,
        ForeignKey("cfg_sch.cfg_t_files.file_id", ondelete="CASCADE"),
        nullable=False,
    )
    transaction_date = Column(String, nullable=True)
    description = Column(String, nullable=True)
    amount = Column(String, nullable=True)
    category = Column(String, nullable=True)
    account = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    ready_for_reload = Column(Boolean, server_default=text("false"), nullable=False)


# gold schema models
class MonthlyExpenses(Base, BaseModel):
    __tablename__ = "g_t_monthly_expenses"
    __table_args__ = {"schema": "g_sch"}

    monthly_expenses_id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_month = Column(Date, nullable=False, index=True, unique=True)
    total_expenses = Column(Numeric(12, 2), nullable=False)
    total_earnings = Column(Numeric(12, 2), nullable=False)
    total_savings = Column(Numeric(12, 2), nullable=False)
    inserted_datetime = Column(DateTime, server_default=func.now())


class CategoryExpenses(Base, BaseModel):
    __tablename__ = "g_t_category_expenses"
    __table_args__ = (
        UniqueConstraint("transaction_month", "category"),
        {"schema": "g_sch"},
    )

    category_expenses_id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_month = Column(Date, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    total_expenses = Column(Numeric(12, 2), nullable=False)
    inserted_datetime = Column(DateTime, server_default=func.now(), nullable=False)


class SavingsRate(Base, BaseModel):
    __tablename__ = "g_t_savings_rate"
    __table_args__ = {"schema": "g_sch"}

    savings_rate_id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_month = Column(Date, nullable=False, index=True, unique=True)
    savings_rate = Column(Numeric(12, 2), nullable=False)
    inserted_datetime = Column(DateTime, server_default=func.now(), nullable=False)


class PipelineConfiguration(Base, BaseModel):
    """Configuration for the ingestion pipeline"""

    __tablename__ = "g_t_pipeline_config"
    __table_args__ = {"schema": "g_sch"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_table = Column(String, nullable=False, unique=True)
    module_path = Column(String, nullable=False)
    class_name = Column(String, nullable=False)
    active = Column(Boolean, server_default=text("false"))
    dependency = Column(Integer, nullable=True)
    last_run = Column(DateTime, nullable=True)
    inserted_datetime = Column(DateTime, server_default=func.now(), nullable=False)
