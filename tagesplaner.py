import streamlit as st
import pandas as pd
import calendar
from datetime import datetime

def calendar_view(year, month):
    """Create a calendar view for the given month and year."""
    cal = calendar.monthcalendar(year, month)
    return cal

def app():
    st.title("Kalender App")

    # Date selection
    selected_date = st.date_input("Datum", value=datetime.today())
    year, month, _ = selected_date.year, selected_date.month, selected_date.day

    # Show calendar
    cal = calendar_view(year, month)
    for week in cal:
        cols = st.columns(7)
        for day in week:
            with cols[day % 7]:
                if day != 0:
                    date_str = f"{year}-{month:02}-{day:02}"
                    st.write(f"**{day}**")

                    # Text input for each day
                    note = st.text_area("Notiz oder Aufgabe", key=date_str)
                    if st.button("Speichern", key=f"{date_str}_save"):
                        st.success(f"Notiz oder Aufgabe für {date_str} gespeichert: {note}")

    # Previous and Next month navigation buttons
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("Vorheriger Monat"):
            new_date = selected_date.replace(day=1) - pd.DateOffset(months=1)
            st.date_input("Datum", value=new_date, key="prev_month_date")
    with col_next:
        if st.button("Nächster Monat"):
            new_date = selected_date.replace(day=1) + pd.DateOffset(months=1)
            st.date_input("Datum", value=new_date, key="next_month_date")

if __name__ == "__main__":
    app()
