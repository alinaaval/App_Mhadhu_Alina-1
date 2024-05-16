import streamlit as st
import sqlite3
import pandas as pd
import calendar
from datetime import datetime

# Verbindung zur SQLite-Datenbank herstellen (oder erstellen, falls nicht vorhanden)
conn = sqlite3.connect('user_data.db')
c = conn.cursor()

# Tabelle für Benutzer erstellen, falls sie noch nicht existiert
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
conn.commit()

# Funktion zur Überprüfung, ob ein Benutzer bereits existiert
def user_exists(username):
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    return c.fetchone() is not None

# Funktion zur Registrierung eines neuen Benutzers
def register(username, password):
    if not user_exists(username):
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    else:
        return False

# Funktion zur Überprüfung der Anmeldeinformationen
def login(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone() is not None

# Funktion zur Überprüfung der Anmeldeinformationen
def authenticate(username, password):
    return login(username, password)

# Funktion zur Hinzufügung eines neuen Benutzers
def add_user(username, password):
    return register(username, password)

# Funktion zur Hinzufügung einer Aufgabe
def add_task(username, date, description, importance):
    global tasks
    """Add a new task to the DataFrame."""
    new_task = pd.DataFrame({
        'username': [username], 'date': [date], 'description': [description], 'importance': [importance]
    })
    tasks = pd.concat([tasks, new_task], ignore_index=True)

# Funktion zur Hinzufügung eines Ereignisses
def add_event(username, date, description, priority):
    global events
    """Add a new event to the DataFrame."""
    new_event = pd.DataFrame({
        'username': [username], 'date': [date], 'description': [description], 'priority': [priority]
    })
    events = pd.concat([events, new_event], ignore_index=True)

# Funktion zur Filterung von Aufgaben nach Datum und Benutzer
def get_tasks_by_date(username, date):
    """Retrieve tasks for the logged-in user for a specific date."""
    return tasks[(tasks['username'] == username) & (tasks['date'] == date)]

# Funktion zur Filterung von Ereignissen nach Datum und Benutzer
def get_events_by_date(username, date):
    """Retrieve events for the logged-in user for a specific date."""
    return events[(events['username'] == username) & (events['date'] == date)]

# Funktion zur Erstellung einer Kalenderansicht für einen bestimmten Monat
def calendar_view(year, month):
    """Create a calendar view for the given month and year."""
    cal = calendar.monthcalendar(year, month)
    return cal

# Funktion zur Hinzufügung eines Kalendereintrags (Aufgabe oder Ereignis)
def add_calendar_entry(username, date, entry_type, description, importance=None, priority=None):
    """Add a calendar entry which can be a task or an event."""
    if entry_type == 'Task':
        add_task(username, date, description, importance)
    elif entry_type == 'Event':
        add_event(username, date, description, priority)

# Streamlit-Anwendung
def main():
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
            user_events = get_events_by_date(st.session
