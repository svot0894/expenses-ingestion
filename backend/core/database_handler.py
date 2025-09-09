# backend/core/database_handler.py

from contextlib import contextmanager
from typing import Generator
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema


class DatabaseHandler:
    """
    A class to handle database sessions and create schemas on 1st run.
    Provides flexibility for managing database connections.
    """

    def __init__(self) -> None:
        self.database_url = st.secrets.database.database_url

        if not self.database_url:
            raise ValueError("DATABASE_URL not set in environment variables")

        self.engine = create_engine(self.database_url, future=True)
        self._session_local = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=True
        )

    @contextmanager
    def get_db_session(self) -> Generator[Session, None, None]:
        """
        Creates and yields a new SQLAlchemy session.
        Automatically closes the session after use.
        """
        session = self._session_local()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_schema(self, schema_name: str) -> None:
        """
        Creates a new schema in the database.
        """
        with self.engine.connect() as connection:
            connection.execute(CreateSchema(schema_name, if_not_exists=True))
            connection.commit()

    def add_column(self, fq_table: str, col: str, col_type: str, nullable: bool) -> None:
        """
        Adds a new column to an existing table.
        """
        null_str = "NULL" if nullable else "NOT NULL"

        with self.engine.connect() as connection:
            stmt = text(f'ALTER TABLE {fq_table} ADD COLUMN IF NOT EXISTS "{col}" {col_type} {null_str}')
            connection.execute(stmt)
            connection.commit()
