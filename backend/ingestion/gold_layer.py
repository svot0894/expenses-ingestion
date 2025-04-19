import os
from gold.g_t_pipeline_config import GoldPipelineRunner
from dotenv import load_dotenv
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

def run_gold_pipeline():
    # Start a session
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    db_session = Session()

    try:
        # Initialize the pipeline runner
        runner = GoldPipelineRunner(db_session)

        # Trigger the pipeline to process the Gold layer
        runner.run()  # You can specify a target month or leave it as today

        print("Gold pipeline successfully triggered!")
    except Exception as e:
        print(f"Error triggering gold pipeline: {e}")
    finally:
        # Close the DB session after running the pipeline
        db_session.close()

if __name__ == "__main__":
    run_gold_pipeline()
