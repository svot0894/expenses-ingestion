"""Gold Layer Ingestion Script"""
from gold.g_t_pipeline_config import GoldPipelineRunner
from dotenv import load_dotenv
from backend.core.types import Result
from backend.core.database_handler import DatabaseHandler

load_dotenv()

def run_gold_pipeline() -> Result:
    db_handler = DatabaseHandler()

    with db_handler.get_db_session() as db_session:
        try:
            runner = GoldPipelineRunner(db_session)
            result = runner.run()
            return result
        except Exception as e:
            return Result(
                success=False,
                message=f"Error found while running gold pipeline: {e}"
            )

if __name__ == "__main__":
    result = run_gold_pipeline()
    print(f"Success: {result.success} | Message: {result.message}")
