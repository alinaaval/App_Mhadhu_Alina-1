import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta

# Initialize session state
if 'users' not in st.session_state:
    st.session_state['users'] = pd.DataFrame(columns=['username', 'password'])

if 'tasks' not in st.session_state:
    st.session_state['tasks'] = pd.DataFrame(columns=['username', 'date', 'description', 'importance'])

if 'events' not in st.session_state:
    st.session_state['events'] = pd.DataFrame(columns=['username', 'date', 'description'])

def authenticate(username, password):
    """Check if the user credentials are valid."""
    users = st.session_state['users']
    user_data = users[users['username'] == username]
    if not user_data.empty:
        return user_data.iloc[0]['password'] == password
    return False

def add_user(username, password):
    """Add a new user to the DataFrame."""
    users = st.session_state['users']
    if username not in users['username'].values:
        new_user = pd.DataFrame({'username': [username], 'password': [password]})
        st.session_state['users'] = pd.concat([users, new_user], ignore_index=True)
        return True
    return False

def add_task(username, date, description, importance):
    """Add a new task to the DataFrame."""
    tasks = st.session_state['tasks']
    new_task = pd.DataFrame({
        'username': [username], 'date': [date], 'description': [description], 'importance': [importance]
    })
    st.session_state['tasks'] = pd.concat([tasks, new_task], ignore_index=True)

def add_event(username, date, description):
    """Add a new event to the DataFrame."""
    events = st.session_state['events']
    new_event = pd.DataFrame({
        'username': [username], 'date': [date], 'description': [description]
    })
    st.session_state['events'] = pd.concat([events, new_event], ignore_index=True)

def get_tasks_by_date(username, date):
    """Retrieve tasks for the logged-in user for a specific date."""
    tasks = st.session_state['tasks']
    return tasks[(tasks['username'] == username) & (tasks['date'] == date)]

def get_events_by_date(username, date):
    """Retrieve events for the logged-in user for a specific date."""
    events = st.session_state['events']
    return events[(events['username'] == username) & (events['date'] == date)]

def calendar_view(year, month):
    """Create a calendar view for the given month and year."""
    cal = calendar.monthcalendar(year, month)
    return cal

def app():
    # Custom CSS for pastel gradient and other styling
    st.markdown("""
        <style>
        html, body, [class*="css"] {
            height: 100%;
            background: linear-gradient(180deg, #F0F8FF, #E6E6FA, #D8BFD8, #DDA0DD);
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
        .calendar-day {
            border: 1px solid #ccc;
            padding: 10px;
            text-align: center;
            margin: 2px;
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
                selected_date = selected_date.replace(day=1) - timedelta(days=1)
                selected_date = selected_date.replace(day=1)
                st.session_state['selected_date'] = selected_date
        with col2:
            st.write(selected_date.strftime("%B %Y"))
        with col3:
            if st.button("Next"):
                selected_date = selected_date.replace(day=28) + timedelta(days=4)
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
                        if st.button(f"{day}", key=date_str, help=date_str):
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
            
            st.write("**Add a new task:**")
            task_desc = st.text_input("Task Description")
            task_importance = st.selectbox("Importance", ["Low", "Medium", "High"])
            if st.button("Add Task"):
                add_task(st.session_state['username'], current_date, task_desc, task_importance)
                st.success("Task added successfully")
                st.experimental_rerun()  # Refresh the page to show the added task

            st.write("**Events:**")
            if not user_events.empty:
                for index, event in user_events.iterrows():
                    st.markdown(f"<div>{event['description']}</div>", unsafe_allow_html=True)
            else:
                st.write("No events for this day.")

            st.write("**Add a new event:**")
            event_desc = st.text_input("Event Description")
            if st.button("Add Event"):
                add_event(st.session_state['username'], current_date, event_desc)
                st.success("Event added successfully")
                st.experimental_rerun()  # Refresh the page to show the added event

        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.info("Logged out successfully.")

if __name__ == "__main__":
    app()
