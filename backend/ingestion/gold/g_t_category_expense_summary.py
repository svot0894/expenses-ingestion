class MonthlyExpensesGenerator:
    def run(self, db_session, target_month: Optional[date] = None) -> None:
        # Pull from s_t_expenses, compute totals, store into g_monthly_summary
        ...
