import streamlit as st
import pandas as pd
import calendar
from datetime import datetime

def calendar_view(year, month):
    """Create a calendar view for the given month and year."""
    cal = calendar.monthcalendar(year, month)
    return cal

def add_calendar_entry(username, date, entry_type, description, importance=None, priority=None):
    """Add a calendar entry which can be a task or an event."""
    # Hier müssten die Einträge in einer Datenbank oder einer anderen Form von Datenspeicherung gespeichert werden
    pass

def app():
    # Custom CSS for pastel pink gradient and other styling
    st.markdown("""
        <style>
        html, body, [class*="css"] {
            height: 100%;
            background: linear-gradient(180deg, #FFC0CB, #FFB6C1, #FF69B4, #FF1493, #FFC0CB);
            color: #4B0082;
        }
        .low-importance {
            background-color: #D3FFD3;
        }
        .medium-importance {
            background-color: #FFFF99;
        }
        .high-importance {
            background-color: #FF9999;
        }
        .urgent-priority {
            border: 2px solid red;
            background-color: #FF9999;
        }
        .can-wait-priority {
            border: 2px solid green;
        }
        .day-button {
            width: 100px;
            height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }
        </style>
        """, unsafe_allow_html=True)

    st.title("Kalender App")

    # Date selection
    selected_date = st.date_input("Datum", value=datetime.today())
    year, month, _ = selected_date.year, selected_date.month, selected_date.day

    # Show calendar


   

if __name__ == "__main__":
    app()
