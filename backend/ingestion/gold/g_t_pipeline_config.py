import importlib
import os
import sys

# This is a workaround to add the project root to the path
sys.path.append(os.getcwd())

from backend.models.models import GoldPipelineConfig


class GoldPipelineRunner:
    def __init__(self, db_session):
        self.db = db_session

    def run(self):
        configs = self.db.query(GoldPipelineConfig).filter_by(active=True).all()
        for config in configs:
            try:
                # Dynamically import the module
                module = importlib.import_module(config.module_path)
                # Get the class name from the module path
                class_name = config.class_name
                # Get the class from the module
                generator_class = getattr(module, class_name)
                # Instantiate the class
                generator = generator_class()
                # Run the generator
                generator.run(self.db)
            except (ImportError, AttributeError) as e:
                print (f"Error loading module or class: {e}")