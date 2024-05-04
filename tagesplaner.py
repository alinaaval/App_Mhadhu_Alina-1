import streamlit as st
import pandas as pd
import calendar
from datetime import datetime

# Global DataFrames initialized
users = pd.DataFrame(columns=['username', 'password'])
tasks = pd.DataFrame(columns=['username', 'date', 'description', 'importance'])
events = pd.DataFrame(columns=['username', 'date', 'description'])

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

def add_event(username, date, description):
    global events
    """Add a new event to the DataFrame."""
    new_event = pd.DataFrame({
        'username': [username], 'date': [date], 'description': [description]
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

def app():
    # Custom CSS for pastel pink gradient
    st.markdown("""
        <style>
        html, body, [class*="css"] {
            height: 100%;
            background: linear-gradient(180deg, #FFC0CB, #FFB6C1, #FF69B4, #FF1493, #FFC0CB);
            color: #4B0082;
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
                st.success("Logged in successfully")
            else:
                st.error("Invalid username or password")
        if st.button("Register"):
            if add_user(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success("Registration successful. You are now logged in.")
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
            if not user_tasks.empty or not user_events.empty:
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
            else:
                st.write("No tasks or events for this day.")
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.info("Logged out successfully.")

# Note: Uncomment the following line to run this script directly in your local environment.
app()
