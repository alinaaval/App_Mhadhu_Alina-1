import streamlit as st
import calendar
import sqlite3
from datetime import datetime

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
                 (id INTEGER PRIMARY KEY, username TEXT, date TEXT, time TEXT, event TEXT, priority INTEGER)''')
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
    st.title("Tagesansicht")
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
                st.write(f"- {event['event']} (Zeit: {event['time']}, Priorität: {priority_text})")
        else:
            st.write("Keine Termine für diesen Tag.")

# Funktion zur Terminhinzufügung mit Priorität und Zeit
def add_event(username, date, event, time, priority):
    try:
        conn, c = get_db_connection()
        c.execute("INSERT INTO events (username, date, time, event, priority) VALUES (?, ?, ?, ?, ?)", (username, date, time, event, priority))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"Fehler beim Hinzufügen des Termins: {e}")

# Funktion zur Anzeige von Terminen
def show_events(username, date):
    try:
        conn, c = get_db_connection()
        c.execute("SELECT id, time, event, priority FROM events WHERE username=? AND date=?", (username, date))
        events = c.fetchall()
        conn.close()
        return [{"id": event[0], "time": event[1], "event": event[2], "priority": event[3]} for event in events]
    except sqlite3.Error as e:
        st.error(f"Fehler beim Abrufen der Termine: {e}")
        return []

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

    # Aktuelle Tagesansicht anzeigen
    show_day_view()

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

        # Events für das ausgewählte Datum abrufen und anzeigen
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
