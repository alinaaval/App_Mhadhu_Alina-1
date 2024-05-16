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
                            event_priority = day_events['priority'].values if not day_events.empty else None
                            if 'High' in task_importance or 'Dringend' in event_priority:
                                button_label = f"**{day}**"
                            elif 'Medium' in task_importance:
                                button_label = f"*{day}*"
                            col.markdown(f"<button>{button_label}</button>", unsafe_allow_html=True)
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
                else:
                    st.write("**Events:**")
                    for index, event in user_events.iterrows():
                        st.markdown(
                            f"<div class='{'urgent-priority' if event['priority'] == 'Dringend' else 'can-wait-priority'}'>{event['description']} - {event['priority']}</div>", 
                            unsafe_allow_html=True
                        )

            st.write("**Events:**")
            if not user_events.empty:
                for index, event in user_events.iterrows():
                    st.markdown(
                        f"<div class='{'urgent-priority' if event['priority'] == 'Dringend' else 'can-wait-priority'}'>{event['description']} - {event['priority']}</div>", 
                        unsafe_allow_html=True
                    )
            else:
                st.write("No events for this day.")

        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.info("Logged out successfully.")


