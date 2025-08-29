Usage:
- Create a python environment
- Activate python environment:

On Windows:
venv\Scripts\activate

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

- Set up .streamlit/secrets.toml file.
    This contains the Infomaniak kDrive and DATABASE_URL variables.
    You need to create an access token to kDrive.

- You can run the frontend app!
    streamlit run ./frontend/app.py

Database migrations:
TBD