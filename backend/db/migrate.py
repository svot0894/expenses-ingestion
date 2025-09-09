import os
import sys
from sqlalchemy import inspect

sys.path.append(os.getcwd())

from backend.core.database_handler import DatabaseHandler
from backend.models.models import Base

# define a db handler
db_handler = DatabaseHandler()


def migrate() -> None:
    """
    Migrate the database by creating schemas and tables if they do not exist.
    """
    engine = db_handler.engine

    # create schemas if not exists
    for table in Base.metadata.tables.values():
        schema = table.schema
        table_name = table.name
        fq_table = f"{schema}.{table_name}" if schema else table_name

        # ensure schema exists
        if schema:
            db_handler.create_schema(schema)

        # create table if not exists
        if not inspect(engine).has_table(table_name, schema=schema):
            Base.metadata.create_all(engine)

        # check existing columns
        existing_columns = [col["name"] for col in inspect(engine).get_columns(table_name, schema=schema)]
        columns_in_model = set(table.columns.keys())

        # add missing columns
        for col in columns_in_model - set(existing_columns):
            db_handler.add_column(fq_table, col, table.columns[col].type, table.columns[col].nullable)
            print(f"Added column {col} to {fq_table}")
        
        # drop extra columns: TBD - requires careful handling

if __name__ == "__main__":
    migrate()
