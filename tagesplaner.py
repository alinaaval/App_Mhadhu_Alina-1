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
    if entry_type == 'Task':
        add_task(username, date, description, importance)
    elif entry_type == 'Event':
        add_event(username, date, description, priority)

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
    cal = calendar_view(year, month)
    for week in cal:
        cols = st.columns(7)
        for day, col in zip(week, cols):
            if day != 0:
                date_str = f"{year}-{month:02}-{day:02}"
                button_label = f"{day}"
                col.markdown(f"<div class='day-button'>{button_label}</div>", unsafe_allow_html=True)
                if st.button(button_label, key=date_str, help=date_str):
                    st.session_state['current_date'] = date_str

    # Show selected day details
    if 'current_date' in st.session_state:
        current_date = st.session_state['current_date']
        st.subheader(f"Details for {current_date}")
        user_tasks = get_tasks_by_date(st.session_state['username'], current_date)
        user_events = get_events_by_date(st.session_state['username'], current_date)
        
        st.write("**Tasks:**")
        if not user_tasks.empty:
            for index, task in user_tasks.iterrows():
                st.markdown(
                    f"<div class='{'low-importance' if task['importance'] == 'Low' else 'medium-importance' if task['importance'] == 'Medium' else 'high-importance'}'>{task['description']} - {task['importance']}</div>", 
                    unsafe_allow_html=True
                )
        else:
            st.write("No tasks for this day.")
        
        st.write("**Add a new task or event:**")
        entry_type = st.selectbox("Entry Type", ["Task", "Event"])
        entry_desc = st.text_input("Description")
        if entry_type == "Task":
            entry_importance = st.selectbox("Importance", ["Low", "Medium", "High"])
            entry_priority = None
        else:
            entry_importance = None
            entry_priority = st.selectbox("Priority", ["Dringend", "kann warten"])
        if st.button("Add Entry"):
            add_calendar_entry(st.session_state['username'], current_date, entry_type, entry_desc, entry_importance, entry_priority)
            st.success(f"{entry_type} added successfully")
            # Refresh the task and event list after adding
            user_tasks = get_tasks_by_date(st.session_state['username'], current_date)
            user_events = get_events_by_date(st.session_state['username'], current_date)
            if entry_type == "Task":
                st.write("**Tasks:**")
                for index, task in user_tasks.iterrows():
                    st.markdown(
                        f"<div class='{'low-importance' if task['importance'] == 'Low' else 'medium-importance' if task['importance'] == 'Medium' else 'high-importance'}'>{task['description']} - {task['importance']}</div>", 
                        unsafe_allow_html=True
                    )
