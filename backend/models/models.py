from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Float, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import hashlib

Base = declarative_base()

class FileConfiguration(Base):
    __tablename__ = "cfg_t_file_config"
    __table_args__ = {"schema": "config_sch"}

    config_id = Column(Integer, primary_key=True)
    file_pattern = Column(String, nullable=False)
    date_format = Column(String, default="%d.%m.%y", nullable=False)
    amount_sign = Column(Integer, default=1, nullable=False)  # 1 or -1
    delimiter = Column(String, default=",", nullable=False)
    decimal_separator = Column(String, default=".", nullable=False)
    description = Column(String, default="", nullable=False)


class FileStatus(Base):
    __tablename__ = "cfg_t_file_status"
    __table_args__ = {"schema": "config_sch"}

    file_status_id = Column(Integer, primary_key=True)
    file_status_name = Column(String(255), unique=True, nullable=False)
    description = Column(String, nullable=True)


class ExpensesFile(Base):
    __tablename__ = "cfg_t_files"
    __table_args__ = {"schema": "config_sch"}

    file_id = Column(String, primary_key=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    number_rows = Column(Integer, nullable=False)
    checksum = Column(String(255), unique=True, nullable=False)
    file_status_id = Column(Integer, ForeignKey("config_sch.cfg_t_file_status.file_status_id"), nullable=False)
    file_config_id = Column(Integer, ForeignKey("config_sch.cfg_t_file_config.config_id"), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    error_message = Column(String, nullable=True)
    inserted_datetime = Column(DateTime, default=datetime.today, nullable=False)
    ingested_datetime = Column(DateTime, nullable=True)

    @staticmethod
    def generate_checksum(content: str) -> str:
        return hashlib.sha224(content.encode()).hexdigest()


class Expense(Base):
    __tablename__ = "s_t_expenses"
    __table_args__ = {"schema": "s_sch"}

    file_id = Column(String, ForeignKey("config_sch.cfg_t_files.file_id"), primary_key=True)
    transaction_date = Column(Date, primary_key=True)
    description = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)