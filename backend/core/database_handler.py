# backend/core/database_handler.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from contextlib import contextmanager


load_dotenv()

class DatabaseHandler:
    """
    A class to handle database sessions.
    Provides flexibility for managing database connections.
    """

    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.engine = create_engine(self.db_url, future=True)
        self._session_local = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    @contextmanager
    def get_db_session(self) -> Session:
        """
        Creates and yields a new SQLAlchemy session.
        Automatically closes the session after use.
        """
        session = self._session_local()
        try:
            yield session
        finally:
            session.close()

