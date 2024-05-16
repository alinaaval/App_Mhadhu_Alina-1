import streamlit as st
import pandas as pd
import calendar
from datetime import datetime

# Global DataFrames initialized
users = pd.DataFrame(columns=['username', 'password'])
tasks = pd.DataFrame(columns=['username', 'date', 'description', 'importance'])
events = pd.DataFrame(columns=['username', 'date', 'description', 'priority'])

def authenticate(username, password):
    global users
    """Check if the user credentials are valid."""
    user_data = users[users['username'] == username]
    if not user_data.empty:
        return user_data.iloc[0]['password'] == password
    return False

def add_user(username, password):
    global users
    """Add a new user to the DataFrame."""
    if username not in users['username'].values:
        new_user = pd.DataFrame({'username': [username], 'password': [password]})
        users = pd.concat([users, new_user], ignore_index=True)
        return True
    return False

def add_task(username, date, description, importance):
    global tasks
    """Add a new task to the DataFrame."""
    new_task = pd.DataFrame({
        'username': [username], 'date': [date], 'description': [description], 'importance': [importance]
    })
    tasks = pd.concat([tasks, new_task], ignore_index=True)

def add_event(username, date, description, priority):
    global events
    """Add a new event to the DataFrame."""
    new_event = pd.DataFrame({
        'username': [username], 'date': [date], 'description': [description], 'priority': [priority]
    })
    events = pd.concat([events, new_event], ignore_index=True)

def get_tasks_by_date(username, date):
    """Retrieve tasks for the logged-in user for a specific date."""
    return tasks[(tasks['username'] == username) & (tasks['date'] == date)]

def get_events_by_date(username, date):
    """Retrieve events for the logged-in user for a specific date."""
    return events[(events['username'] == username) & (events['date'] == date)]

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
    # Custom CSS for light blue background and other styling
    st.markdown("""
        <style>
        body {
            background-color: #E0FFFF;
        }
        .calendar-button {
            background-color: #FFFFFF;
            width: 100px;
            height: 100px;
            border-radius: 10px;
            padding: 10px;
            margin: 5px;
        }
        .calendar-button:hover {
            background-color: #ADD8E6;
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
        </style>
        """, unsafe_allow_html=True)
    
    st.title("Task and Event Manager")

    if 'logged_in' not in st.session_state:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['selected_date'] = datetime.today()
                st.success("Logged in successfully")
            else:
                st.error("Invalid username or password")
        if st.button("Register"):
            if add_user(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['selected_date'] = datetime.today()
                st.success("Registration successful. You are now logged in.")
            else:
                st.error("Username already taken")
    else:
        # Display month navigation and calendar
        selected_date = st.session_state['selected_date']
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Previous"):
                selected_date = selected_date.replace(day=1) - pd.DateOffset(months=1)
                st.session_state['selected_date'] = selected_date
        with col2:
            st.write(selected_date.strftime("%B %Y"))
        with col3:
            if st.button("Next"):
                selected_date = selected_date.replace(day=28) + pd.DateOffset(days=4)  # ensures it moves to the next month
                selected_date = selected_date.replace(day=1)
                st.session_state['selected_date'] = selected_date

        # Show calendar
        cal = calendar_view(selected_date.year, selected_date.month)
        st.write("**Click on a day to add/view tasks and events**")
        for week in cal:
            cols = st.columns(7)
            for day, col in zip(week, cols):
                with col:
                    if day != 0:
                        date_str = f"{selected_date.year}-{selected_date.month:02}-{day:02}"
                        button_label = f"{day}"
                        day_tasks = get_tasks_by_date(st.session_state['username'], date_str)
                        day_events = get_events_by_date(st.session_state['username'], date_str)
                        if not day_tasks.empty or not day_events.empty:
                            task_importance = day_tasks['importance'].values if not day_tasks.empty else None
                            event_priority = day_events
