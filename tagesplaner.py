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

    # Simplified login and register forms for debugging
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate(username, password):
            st.success("Logged in successfully")
        else:
            st.error("Invalid username or password")
    if st.button("Register"):
        if add_user(username, password):
            st.success("User registered. You can now login.")
        else:
            st.error("Username already taken")

    # Simplified display of tasks and events without detailed day selection
    if st.checkbox("Show Tasks and Events"):
        st.write("Tasks:")
        st.dataframe(tasks)
        st.write("Events:")
        st.dataframe(events)

# Note: Uncomment the following line to run this script directly in your local environment.
# app()
