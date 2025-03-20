# create a virtual environment if it doesn't exist
if (-not (Test-Path .\expenses_env)) {
    python -m venv expenses_env
}

# activate the virtual environment
.\expenses_env\Scripts\Activate.ps1

# install the required packages
pip install -r requirements.txt

# run the application
streamlit run .\frontend\app.py