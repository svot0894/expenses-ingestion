import importlib
import os
import sys

# This is a workaround to add the project root to the path
sys.path.append(os.getcwd())

from backend.core.types import Result
from backend.models.models import PipelineConfiguration


class GoldPipelineRunner:
    def __init__(self, db_session) -> None:
        self.db = db_session

    def run(self) -> Result:
        # fetch all active pipeline configurations
        configs = self.db.query(PipelineConfiguration).filter_by(active=True).all()

        if not configs:
            return Result(
                success=False,
                message="No active pipeline configurations found."
            )

        errors = []
        for config in configs:
            try:
                module = importlib.import_module(config.module_path)
                generator_class = getattr(module, config.class_name)
                generator = generator_class()
                generator.run(self.db)
            except (ImportError, AttributeError, Exception) as e:
                errors.append(f"{config.module_path}: {e}")
        
        if errors:
            Result(success=False, message="Errors occurred:\n" + "\n".join(errors))
        return Result(success=True, message="Gold pipeline run completed successfully.")