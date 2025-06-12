"""Script for full ingestion pipeline."""

from prefect import flow, task
from backend.ingestion.silver_pipeline import silver_pipeline
from backend.ingestion.gold_pipeline import gold_pipeline
from backend.core.types import Result


@task
def run_silver_pipeline(file_id: str, file_config_id: int) -> Result:
    """Task to run the silver pipeline."""
    return silver_pipeline(file_id, file_config_id)


@task
def run_gold_pipeline() -> Result:
    """Task to run the gold pipeline."""
    return gold_pipeline()


@flow
def pipeline(file_id: str, file_config_id: int) -> Result:
    """Full ingestion pipeline flow."""
    silver_result = run_silver_pipeline(file_id, file_config_id)

    if silver_result.success:
        gold_result = run_gold_pipeline()

        if gold_result.success:
            return Result(
                success=True,
                message="Silver and Gold ingestion completed successfully",
            )
        return Result(
            success=False, message=f"Gold ingestion failed: {gold_result.message}"
        )
    return Result(
        success=False, message=f"Silver ingestion failed: {silver_result.message}"
    )
