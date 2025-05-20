# backend/core/database_handler.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema
import os
from dotenv import load_dotenv
from contextlib import contextmanager


load_dotenv()

class DatabaseHandler:
    """
    A class to handle database sessions and create schemas on 1st run.
    Provides flexibility for managing database connections.
    """

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")

        if not self.database_url:
            raise ValueError("DATABASE_URL not set in environment variables")
        
        self.engine = create_engine(self.database_url, future=True)
        self._session_local = sessionmaker(bind=self.engine)

    @contextmanager
    def get_db_session(self) -> Session:
        """
        Creates and yields a new SQLAlchemy session.
        Automatically closes the session after use.
        """
        session = self._session_local()
        try:
            yield session
        except Exception as e:
            session.rollback()
        finally:
            session.close()
    
    def create_schema(self, schema_name: str):
        """
        Creates a new schema in the database.
        """
        with self.engine.connect() as connection:
            connection.execute(CreateSchema(schema_name, if_not_exists=True))
            connection.commit()

