import streamlit as st
import pandas as pd
from datetime import datetime
from calendar import month_abbr

from backend.core.dashboard.gold_queries import (
    get_monthly_summary,
    get_previous_monthly_summary,
    get_savings_rate_summary,
)

from backend.core.database_handler import DatabaseHandler

st.set_page_config(page_title="Expenses Dashboard", layout="wide")

# Initialize database session
db_handler = DatabaseHandler()

# -- Filter: Select a specific month
with st.sidebar:
    st.header("Filters")
    this_year = datetime.now().year
    this_month = datetime.now().month
    report_year = st.selectbox("Select Year", range(this_year, this_year - 5, -1))
    month_abbr = month_abbr[1:]
    report_month_str = st.radio("Select Month", month_abbr, index=this_month - 1, horizontal=True)
    report_month = month_abbr.index(report_month_str) + 1

# convert report_month and report_year to a date object
report_month_date = datetime(report_year, report_month, 1)

# -- KPIs: Display main KPIs
st.title("📊 Financial Overview")

# import data using get_monthly_summary function
try:
    with db_handler.get_db_session() as session:
        is_valid1, kpis_data = get_monthly_summary(session, report_month_date)
        is_valid2, previous_kpis_data = get_previous_monthly_summary(session, report_month_date)

    if is_valid1:
        col1, col2, col3 = st.columns(3)

        if is_valid2:
            try:
                total_expenses_diff = kpis_data.total_expenses - previous_kpis_data.total_expenses
                total_earnings_diff = kpis_data.total_earnings - previous_kpis_data.total_earnings
                total_savings_diff = kpis_data.total_savings - previous_kpis_data.total_savings

                total_expenses_change = (
                    round(total_expenses_diff / previous_kpis_data.total_expenses, 4) * 100
                    if previous_kpis_data.total_expenses else 0
                )
                total_earnings_change = (
                    round(total_earnings_diff / previous_kpis_data.total_earnings, 4) * 100
                    if previous_kpis_data.total_earnings else 0
                )
                total_savings_change = (
                    round(total_savings_diff / previous_kpis_data.total_savings, 4) * 100
                    if previous_kpis_data.total_savings else 0
                )

                col1.metric("💸 Total Expenses", float(kpis_data.total_expenses), f"{float(total_expenses_change)}%")
                col2.metric("💰 Total Earnings", float(kpis_data.total_earnings), f"{float(total_earnings_change)}%")
                col3.metric("🧮 Total Savings", float(kpis_data.total_savings), f"{float(total_savings_change)}%")
            except ZeroDivisionError:
                st.error("Division by zero occurred while calculating percentage changes.")
            except Exception as e:
                st.error(f"An unexpected error occurred while processing KPIs: {e}")
        else:
            col1.metric("💸 Total Expenses", float(kpis_data.total_expenses), "N/A")
            col2.metric("💰 Total Earnings", float(kpis_data.total_earnings), "N/A")
            col3.metric("🧮 Total Savings", float(kpis_data.total_savings), "N/A")
            st.info("No data available for the previous month to calculate changes.")
    else:
        st.warning("No data available for the selected month.")
except Exception as e:
    st.error(f"An error occurred while fetching data: {e}")

st.markdown("---")

# --- Dashboard 1: Category vs. Budget ---
st.subheader("📂 Expenses per Category vs Budget")

#category_data = get_category_vs_budget(selected_month)
#st.bar_chart(category_data.set_index("category")[["expenses", "budget"]])

st.markdown("---")

# --- Dashboard 2: Overall Savings Rate ---
st.subheader("💼 Overall Savings Rate")

with db_handler.get_db_session() as session:
    is_valid, savings_rate = get_savings_rate_summary(session)

if is_valid:
    # convert savings_rate to a DataFrame
    savings_rate_df = pd.DataFrame(
        [(r.transaction_month, r.savings_rate) for r in savings_rate],
        columns=["transaction_month", "savings_rate"]
    )
    savings_rate_df["transaction_month"] = pd.to_datetime(savings_rate_df["transaction_month"])
    savings_rate_df["savings_rate"] = pd.to_numeric(savings_rate_df["savings_rate"], errors="coerce")

    st.line_chart(savings_rate_df.set_index("transaction_month"))