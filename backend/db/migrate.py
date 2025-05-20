import os
import sys

sys.path.append(os.getcwd())

from backend.core.database_handler import DatabaseHandler
from backend.models.models import Base

# define a db handler
db_handler = DatabaseHandler()

def migrate():
    engine = db_handler.engine

    # create schemas if not exists
    for table in Base.metadata.tables.values():
        schema = table.schema
        if schema:
            db_handler.create_schema(schema)

    # create all tables
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    migrate()