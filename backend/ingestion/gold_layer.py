"""Gold Layer Ingestion Script
This script is responsible for triggering the Gold layer ingestion pipeline."""
from gold.g_t_pipeline_config import GoldPipelineRunner
from dotenv import load_dotenv
from backend.core.database_handler import DatabaseHandler

load_dotenv()

def run_gold_pipeline():
    # Start a session using the database handler
    db_handler = DatabaseHandler()
    with db_handler.get_db_session() as db_session:
        try:
            # Initialize the pipeline runner
            runner = GoldPipelineRunner(db_session)

            # Trigger the pipeline to process the Gold layer
            runner.run()

            print("Gold pipeline completed successfully")
        except Exception as e:
            print(f"Error found while running gold pipeline: {e}")

if __name__ == "__main__":
    run_gold_pipeline()
