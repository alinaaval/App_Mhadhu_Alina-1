import streamlit as st
import pandas as pd
import calendar
from datetime import datetime

# Placeholder for user data, tasks, and events (for demo purposes)
users = pd.DataFrame(columns=['username', 'password'])
tasks = pd.DataFrame(columns=['username', 'date', 'description', 'importance'])
events = pd.DataFrame(columns=['username', 'date', 'description'])

def authenticate(username, password):
    """Check if the user credentials are valid."""
    if username in users['username'].values:
        user_data = users[users['username'] == username]
        return user_data['password'].iloc[0] == password
    return False

def add_user(username, password):
    """Add a new user to the DataFrame."""
    global users
    if username not in users['username'].values:
        users = users.append({'username': username, 'password': password}, ignore_index=True)
        return True
    return False

def add_task(username, date, description, importance):
    """Add a new task to the DataFrame."""
    global tasks
    tasks = tasks.append({
        'username': username, 'date': date, 'description': description, 'importance': importance
    }, ignore_index=True)

def add_event(username, date, description):
    """Add a new event to the DataFrame."""
    global events
    events = events.append({
        'username': username, 'date': date, 'description': description
    }, ignore_index=True)

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

def app():
    # Custom CSS for pastel pink gradient
    st.markdown("""
        <style>
        html {
            height: 100%;
        }
        body {
            background: linear-gradient(180deg, #FFC0CB, #FFB6C1, #FF69B4, #FF1493, #FFC0CB);
            color: #4B0082;
            height: 100%;
        }
        </style>
        """, unsafe_allow_html=True)

    st.title("Task and Event Manager")

    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login = st.form_submit_button("Login")
            register = st.form_submit_button("Register")

            if login:
                if authenticate(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                else:
                    st.error("Invalid username or password")

            if register:
                if add_user(username, password):
                    st.success("User registered. You can now login.")
                else:
                    st.error("Username already taken")

    else:
        # Display month navigation and calendar
        selected_date = st.session_state.get('selected_date', datetime.today())
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
                st.session_state['selected_date'] = selected_date

        # Show calendar
        cal = calendar_view(selected_date.year, selected_date.month)
        for week in cal:
            cols = st.columns(7)
            for day, col in zip(week, cols):
                with col:
                    if day != 0:
                        date_str = f"{selected_date.year}-{selected_date.month:02}-{day:02}"
                        if st.button(f"{day}", key=date_str):
                            st.session_state['current_date'] = date_str

        # Show selected day details
        if 'current_date' in st.session_state:
            current_date = st.session_state['current_date']
            st.subheader(f"Details for {current_date}")
            user_tasks = get_tasks_by_date(st.session_state['username'], current_date)
            user_events = get_events_by_date(st.session_state['username'], current_date)
            if not user_tasks.empty:
                st.write("Tasks:")
                st.dataframe(user_tasks)
            if not user_events.empty:
                st.write("Events:")
                st.dataframe(user_events)

            with st.form("add_event"):
                event_desc = st.text_input("Event Description")
                add_event_btn = st.form_submit_button("Add Event")
            
            if add_event_btn:
                add_event(st.session_state['username'], current_date, event_desc)
                st.success("Event added successfully")

        # Logout button
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.info("Logged out successfully.")

# Note: Uncomment the following line to run this script directly in your local environment.
# app()
