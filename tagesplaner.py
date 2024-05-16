import streamlit as st
from datetime import datetime
import calendar

def large_calendar_input(label, min_date=None, max_date=None, key=None):
    """Custom implementation of a large calendar date input."""
    selected_date = st.date_input(label, min_value=min_date, max_value=max_date, key=key)
    year, month = selected_date.year, selected_date.month
    cal = calendar.monthcalendar(year, month)
    day_container = st.container()
    for week in cal:
        with day_container:
            for day in week:
                if day != 0:
                    date_str = f"{year}-{month:02}-{day:02}"
                    if st.button(day, key=date_str):
                        return datetime(year, month, day)

def calendar_view(year, month):
    """Create a calendar view for the given month and year."""
    cal = calendar.monthcalendar(year, month)
    return cal

def app():
    st.title("Kalender App")

    # Date selection
    selected_date = large_calendar_input("Datum")

    year, month, _ = selected_date.year, selected_date.month, selected_date.day

    # Show calendar
    st.subheader(calendar.month_name[month] + " " + str(year))
    cal = calendar_view(year, month)
    for week in cal:
        cols = st.columns(7)
        for day in week:
            if day != 0:
                cols[day - 1].button(label=str(day), key=f"{year}-{month:02}-{day:02}")

if __name__ == "__main__":
    app()
