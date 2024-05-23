import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import sqlite3
import time

# Funktion zur Verbindung mit der SQLite-Datenbank
def get_db_connection():
    conn = sqlite3.connect('user_data.db')
    return conn, conn.cursor()

# Tabellen für Benutzer und Kalendereinträge erstellen, falls sie noch nicht existieren
def create_tables():
    conn, c = get_db_connection()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (id INTEGER PRIMARY KEY, username TEXT, date TEXT, event TEXT, priority INTEGER)''')
    conn.commit()
    conn.close()

create_tables()

# Funktion zur Überprüfung, ob ein Benutzer bereits existiert
def user_exists(username):
    conn, c = get_db_connection()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    return result is not None

# Funktion zur Registrierung eines neuen Benutzers
def register(username, password):
    if not user_exists(username):
        conn, c = get_db_connection()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    else:
        return False

# Funktion zur Überprüfung der Anmeldeinformationen
def login(username, password):
    conn, c = get_db_connection()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None

# Funktion zum Ausloggen
def logout():
    st.session_state['authenticated'] = False
    if 'username' in st.session_state:
        del st.session_state['username']
        
# Funktion zur Anzeige der Tagesansicht
def show_day_view(date):
    st.write(f"Anzeigen von Informationen für {date}")
    
    # Events für das angegebene Datum anzeigen
    if 'username' in st.session_state:
        username = st.session_state['username']
        events = show_events(username, date)
        if events:
            st.write("Termine:")
            for event in events:
                priority = event["priority"]
                priority_text = "Niedrig" if priority == 1 else "Mittel" if priority == 2 else "Hoch"
                st.write(f"- {event['event']} (Priorität: {priority_text})")
        else:
            st.write("Keine Termine für diesen Tag.")
            
# Funktion zur Berechnung des nächsten Monats
def next_month(current_year, current_month):
    next_month_year = current_year
    next_month = current_month + 1
    if next_month > 12:
        next_month = 1
        next_month_year += 1
    return next_month_year, next_month

# Funktion zur Berechnung des vorherigen Monats
def previous_month(current_year, current_month):
    previous_month_year = current_year
    previous_month = current_month - 1
    if previous_month < 1:
        previous_month = 12
        previous_month_year -= 1
    return previous_month_year, previous_month

# Funktion zur Terminhinzufügung mit Priorität
def add_event(username, date, event, priority):
    try:
        conn, c = get_db_connection()
        c.execute("INSERT INTO events (username, date, event, priority) VALUES (?, ?, ?, ?)", (username, date, event, priority))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"Fehler beim Hinzufügen des Termins: {e}")

# Funktion zur Anzeige von Terminen
def show_events(username, date):
    try:
        conn, c = get_db_connection()
        c.execute("SELECT id, event, priority FROM events WHERE username=? AND date=?", (username, date))
        events = c.fetchall()
        conn.close()
        return [{"id": event[0], "event": event[1], "priority": event[2]} for event in events]
    except sqlite3.Error as e:
        st.error(f"Fehler beim Abrufen der Termine: {e}")
        return []

# Funktion zur Überprüfung, ob für einen bestimmten Tag Termine existieren
def has_events(username, date):
    try:
        conn, c = get_db_connection()
        c.execute("SELECT COUNT(*) FROM events WHERE username=? AND date=?", (username, date))
        count = c.fetchone()[0]
        conn.close()
        return count > 0
    except sqlite3.Error as e:
        st.error(f"Fehler beim Überprüfen der Termine: {e}")
        return False

# Funktion zum Löschen eines Termins
def delete_event(event_id):
    try:
        conn, c = get_db_connection()
        c.execute("DELETE FROM events WHERE id=?", (event_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        st.error(f"Fehler beim Löschen des Termins: {e}")
        return False
def main():
    st.title("Kalender App mit Timer")

    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        st.title("Benutzerregistrierung und -anmeldung")
        # Code für Registrierung und Anmeldung hier ...
        
# Funktion zur Anzeige der aktuellen Tagesansicht
def show_current_day_view():
    current_date = datetime.today().strftime("%Y-%m-%d")
    with st.sidebar:
        st.subheader("Heutige Termine")
        if 'username' in st.session_state:
            username = st.session_state['username']
            events = show_events(username, current_date)
            if events:
                st.write("Termine:")
                for event in events:
                    priority = event["priority"]
                    priority_text = "Niedrig" if priority == 1 else "Mittel" if priority == 2 else "Hoch"
                    checked = st.checkbox(event['event'], key=event['id'])
                    if checked:
                        st.write(f"- ~~{event['event']}~~ (Priorität: {priority_text})")
                    else:
                        st.write(f"- {event['event']} (Priorität: {priority_text})")
            else:
                st.write("Keine Termine für heute.")

# Streamlit-Anwendung
def main():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        st.title("Benutzerregistrierung und -anmeldung")
    
        if st.checkbox("Registrieren"):
            # Benutzerregistrierung
            st.subheader("Registrierung")
            new_username = st.text_input("Benutzername")
            new_password = st.text_input("Passwort", type="password")
            if st.button("Registrieren"):
                if register(new_username, new_password):
                    st.success("Registrierung erfolgreich!")
                else:
                    st.error("Benutzername bereits vergeben!")
        else:
            # Benutzeranmeldung
            st.subheader("Anmeldung")
            login_username = st.text_input("Benutzername", key="login_username")
            login_password = st.text_input("Passwort", type="password", key="login_password")
            if st.button("Anmelden", key="login_button"):
                if login(login_username, login_password):
                    st.success("Anmeldung erfolgreich!")
                    st.write("Willkommen zurück,", login_username)
                    st.session_state['authenticated'] = True
                    st.session_state['username'] = login_username  # Speichern des Benutzernamens in st.session_state
                else:
                    st.error("Ungültige Anmeldeinformationen!")
        return
    
    st.title("To-do Liste")

    if st.button("Ausloggen"):
        logout()
        return

    # Überprüfen, ob der Benutzername im Session State ist
    if 'username' in st.session_state:
        username = st.session_state['username']
    else:
        st.error("Fehler: Benutzername nicht gefunden. Bitte erneut anmelden.")
        return
    
    # Platzieren des Bildes oben rechts
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        st.image("https://cdn.icon-icons.com/icons2/2416/PNG/512/heart_list_task_to_do_icon_146658.png")
    
   # Füge der linken Spalte eine hellrosa Hintergrundfarbe hinzu
    with col1:
        st.markdown(
            """
            <style>
            [data-testid="stVerticalBlock"] > div:first-child {
                background-color: #CAC9E1;
                padding: 10px;
                border-radius: 5px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    # Aktuelle Tagesansicht anzeigen
    show_current_day_view()

    # Date selection
    selected_date = st.date_input("Datum", value=datetime.today())

    if selected_date:
        year, month, day = selected_date.year, selected_date.month, selected_date.day
        selected_date_str = selected_date.strftime("%Y-%m-%d")

        # Show calendar
        st.subheader(calendar.month_name[month] + " " + str(year))
        cal = calendar.monthcalendar(year, month)
        for week in cal:
            cols = st.columns(7)
            for day in week:
                if day != 0:
                    date = datetime(year, month, day).strftime("%Y-%m-%d")
                    events = show_events(username, date)
                    button_text = str(day)
                    if events:
                        # Überprüfen, ob eine Veranstaltung mit hoher Priorität vorhanden ist
                        has_high_priority_event = any(event["priority"] == 3 for event in events)
                        if has_high_priority_event:
                            button_text += " 🔴"  # Symbol 🔴 für hohe Priorität hinzufügen
                        else:
                            button_text += " 🔵"
                        if cols[calendar.weekday(year, month, day)].button(button_text):
                            show_day_view(date)
                    else:
                        if cols[calendar.weekday(year, month, day)].button(button_text):
                            show_day_view(date)

        # Event hinzufügen
        st.subheader("Neuen Termin hinzufügen")
        event_description = st.text_input("Terminbeschreibung")
        priority = st.selectbox("Priorität", [1, 2, 3], format_func=lambda x: "Niedrig" if x == 1 else "Mittel" if x == 2 else "Hoch")
        if st.button("Hinzufügen"):
            if event_description:
                add_event(username, selected_date_str, event_description, priority)
                st.success("Termin hinzugefügt!")
            else:
                st.error("Bitte eine Terminbeschreibung eingeben.")

        # Events für den ausgewählten Tag abrufen und anzeigen
        st.subheader("Termine für den ausgewählten Tag")
        events = show_events(username, selected_date_str)
        if events:
            for event in events:
                event_id = event["id"]
                event_text = f"{event['event']} (Priorität: {'Niedrig' if event['priority'] == 1 else 'Mittel' if event['priority'] == 2 else 'Hoch'})"
                if st.button(f"Löschen: {event_text}", key=f"delete_{event_id}"):
                    if delete_event(event_id):
                        st.success(f"Termin mit ID {event_id} erfolgreich gelöscht.")
                        # Events nach dem Löschen aktualisieren
                        events = show_events(username, selected_date_str)
                    else:
                        st.error(f"Fehler beim Löschen des Termins mit ID {event_id}.")
        else:
            st.write("Keine Termine für diesen Tag.")
    
if __name__ == "__main__":
    main()
