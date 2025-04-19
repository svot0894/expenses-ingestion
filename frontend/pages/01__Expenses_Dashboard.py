import streamlit as st
from datetime import datetime
from calendar import month_abbr

st.set_page_config(page_title="Expenses Dashboard", layout="wide")

# -- Filter: Select a specific month
with st.sidebar:
    st.header("Filters")
    this_year = datetime.now().year
    this_month = datetime.now().month
    report_year = st.selectbox("Select Year", range(this_year, this_year - 5, -1))
    month_abbr = month_abbr[1:]
    report_month_str = st.radio("Select Month", month_abbr, index=this_month - 1, horizontal=True)
    report_month = month_abbr.index(report_month_str) + 1

# -- KPIs: Display main KPIs
st.title("📊 Financial Overview")

col1, col2, col3 = st.columns(3)
col1.metric("💸 Total Expenses", 10, 0.02)
col2.metric("💰 Total Earnings", 10, 0.02)
col3.metric("🧮 Total Savings", 10, 0.02)

st.markdown("---")

# --- Dashboard 1: Category vs. Budget ---
st.subheader("📂 Expenses per Category vs Budget")

#category_data = get_category_vs_budget(selected_month)
#st.bar_chart(category_data.set_index("category")[["expenses", "budget"]])

st.markdown("---")

# --- Dashboard 2: Overall Savings Rate ---
st.subheader("💼 Overall Savings Rate")

#savings_rate = get_savings_rate()
#st.metric("💹 Savings Rate", f"{savings_rate:.2f}%")