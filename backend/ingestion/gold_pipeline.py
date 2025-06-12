"""Gold Layer Ingestion Script"""

from backend.ingestion.gold.g_t_pipeline_config import GoldPipelineRunner
from backend.core.types import Result
from backend.core.database_handler import DatabaseHandler


def gold_pipeline() -> Result:
    """Run all active gold pipelines."""
    db_handler = DatabaseHandler()

    with db_handler.get_db_session() as db_session:
        try:
            runner = GoldPipelineRunner(db_session)
            result = runner.run()
            return result
        except Exception as e:
            return Result(
                success=False, message=f"Error found while running gold pipeline: {e}"
            )
