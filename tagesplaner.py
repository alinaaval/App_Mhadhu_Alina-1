import streamlit as st
from datetime import datetime, timedelta
import calendar

def large_calendar_input(label, min_date=None, max_date=None, key=None):
    """Custom implementation of a large calendar date input."""
    selected_date = st.date_input(label, min_value=min_date, max_value=max_date, key=key)
    return selected_date

def calendar_view(year, month):
    """Create a calendar view for the given month and year."""
    cal = calendar.monthcalendar(year, month)
    return cal

def previous_month(current_year, current_month):
    """Get the previous month."""
    previous_month_year = current_year
    previous_month = current_month - 1
    if previous_month < 1:
        previous_month = 12
        previous_month_year -= 1
    return previous_month_year, previous_month

def next_month(current_year, current_month):
    """Get the next month."""
    next_month_year = current_year
    next_month = current_month + 1
    if next_month > 12:
        next_month = 1
        next_month_year += 1
    return next_month_year, next_month

def app():
    st.title("Kalender App")

    # Date selection
    selected_date = large_calendar_input("Datum")

    if selected_date:
        year, month, _ = selected_date.year, selected_date.month, selected_date.day

        # Show calendar
        st.subheader(calendar.month_name[month] + " " + str(year))
        cal = calendar_view(year, month)
        cols = st.columns(7)
        for week in cal:
            for day in week:
                if day != 0:
                    cols[calendar.weekday(year, month, day)].write(str(day))

        # Previous and Next Month Buttons
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("Vorheriger Monat"):
                year, month = previous_month(year, month)
                selected_date = datetime(year, month, 1)
        with col3:
            if st.button("Nächster Monat"):
                year, month = next_month(year, month)
                selected_date = datetime(year, month, 1)

if __name__ == "__main__":
    app()
