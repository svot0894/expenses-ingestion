Usage:
- Create a python environment
- Activate python environment:

On Windows:

On Mac:
source venv/bin/activate

- Install UV (https://astral.sh/blog/uv)
    - I use UV as a python project and package manager

    On Windows:
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

    On Mac:
    curl -LsSf https://astral.sh/uv/install.sh | sh

- Install dependencies from pyproject.toml file
    uv pip install -r pyproject.toml --group dev

- Setup .env file
    This contains the DATABASE_URL key.
    It should look something like: "postgres://user:secret@localhost:5432/mydatabase"

- Set up .streamlit/secrets.toml file.
    This contains the Google Drive API variables.
    You need to set up access to Google Drive API.

- You can run the frontend app!
    streamlit run ./frontend/app.py

Database migrations:
TBD