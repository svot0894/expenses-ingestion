import importlib
import os
import sys

sys.path.append(os.getcwd())

from backend.models.models import GoldPipelineConfig

class GoldPipelineRunner:
    def __init__(self, db_session):
        self.db = db_session

    def run(self):
        configs = self.db.query(GoldPipelineConfig).filter_by(active=True).all()
        for config in configs:
            module = importlib.import_module(config.module_path)
            generator_class = getattr(module, self._class_name_from_module(config.module_path))
            generator = generator_class()
            generator.run(self.db)
            # Update last_run