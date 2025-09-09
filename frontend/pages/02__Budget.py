import os
import sys
import streamlit as st
from datetime import datetime
from calendar import month_abbr as call_month_abbr

sys.path.append(os.getcwd())

from backend.core.database_handler import DatabaseHandler

st.set_page_config(page_title="Monthly Budget", page_icon="💰", layout="wide")

# Initialize database session
db_handler = DatabaseHandler()

# -- Filter: Select a specific month
with st.sidebar:
    st.header("Filters")
    this_year = datetime.now().year
    this_month = datetime.now().month
    report_year = st.selectbox("Select Year", range(this_year, this_year - 5, -1))
    month_abbr = call_month_abbr[1:]
    report_month_str = st.radio(
        "Select Month", month_abbr, index=this_month - 1, horizontal=True
    )
    report_month = month_abbr.index(report_month_str) + 1

# convert report_month and report_year to a date object
report_month_date = datetime(report_year, report_month, 1)

st.title("Monthly Budget")

st.subheader("Enter your monthly budget.", divider=True)

# TODO: fetch categories from cfg_t_categories table
categories = db_handler.fetch_categories()

budget = {}

with st.form("budget_form"):
    for category in categories:
        budget[category] = st.number_input(
            f"{category}", min_value=0.0, step=0.05, format="%.2f"
        )
    submitted = st.form_submit_button("Save Budget")

if submitted:
    db_handler.save_monthly_budget(report_month_date, budget)
    st.success("Budget saved!")


st.subheader("Monthly budget for " + report_month_date.strftime("%B %Y"), divider=True)
st.table(budget)