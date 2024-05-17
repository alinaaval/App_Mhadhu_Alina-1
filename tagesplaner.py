import streamlit as st
import calendar
from datetime import datetime
import sqlite3

# Verbindung zur SQLite-Datenbank herstellen (oder erstellen, falls nicht vorhanden)
conn = sqlite3.connect('user_data.db')
c = conn.cursor()

# Tabellen für Benutzer und Kalendereinträge erstellen, falls sie noch nicht existieren
def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (id INTEGER PRIMARY KEY, username TEXT, date TEXT, event TEXT, priority INTEGER)''')
    conn.commit()

create_tables()

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

# Funktion zum Ausloggen
def logout():
    st.session_state['authenticated'] = False
    if 'username' in st.session_state:
        del st.session_state['username']

# Funktion zur Anzeige von Terminen für einen bestimmten Tag
def show_events_for_day(username, date):
    try:
        c.execute("SELECT event, priority FROM events WHERE username=? AND date=?", (username, date))
        events = c.fetchall()
        return [{"event": event[0], "priority": event[1]} for event in events]
    except sqlite3.Error as e:
        st.error(f"Fehler beim Abrufen der Termine: {e}")
        return []

# Funktion zur Anzeige der Tagesansicht
def show_day_view(date, username):
    st.title("Tagesansicht")
    st.write(f"Anzeigen von Informationen für {date}")

    # Termine für den ausgewählten Tag abrufen
    events = show_events_for_day(username, date)

    if events:
        st.write("Termine:")
        for event in events:
            priority = event["priority"]
            priority_text = "Niedrig" if priority == 1 else "Mittel" if priority == 2 else "Hoch"
            st.write(f"- {event['event']} (Priorität: {priority_text})")
    else:
        st.write("Keine Termine für diesen Tag.")

# Funktion zur Überprüfung, ob für einen bestimmten Tag Termine existieren
def has_events(username, date):
    try:
        c.execute("SELECT COUNT(*) FROM events WHERE username=? AND date=?", (username, date))
        count = c.fetchone()[0]
        return count > 0
    except sqlite3.Error as e:
        st.error(f"Fehler beim Überprüfen der Termine: {e}")
        return False

# Funktion zur Terminhinzufügung
def add_event(username, date, event, priority):
    try:
        c.execute("INSERT INTO events (username, date, event, priority) VALUES (?, ?, ?, ?)", (username, date, event, priority))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Fehler beim Hinzufügen des Termins: {e}")

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

    st.title("Kalender App")

    if st.button("Ausloggen"):
        logout()
        return

    # Überprüfen, ob der Benutzername im Session State ist
    if 'username' in st.session_state:
        username = st.session_state['username']
    else:
        st.error("Fehler: Benutzername nicht gefunden. Bitte erneut anmelden.")
        return

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
                    events = show_events_for_day(username, date)
                    button_text = str(day)
                    if events:
                        button_text += " 🔵"
                    if cols[calendar.weekday(year, month, day)].button(button_text):
                        show_day_view(date, username)
                    else:
                        show_day_view(date, username)

        # Event hinzufügen
        st.subheader("Neuen Termin hinzufügen")
        event_description = st.text_input("Terminbeschreibung")
        priority = st.radio("Priorität:", ("Niedrig", "Mittel", "Hoch"))
        if st.button("Hinzufügen"):
            if event_description:
                priority_mapping = {"Niedrig": 1, "Mittel": 2, "Hoch": 3}
                priority_value = priority_mapping[priority]
                add_event(username, selected_date_str, event_description, priority_value)
                st.success("Termin hinzugefügt!")
            else:
                st.error("Bitte eine Terminbeschreibung eingeben
