import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta
import sqlite3

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
                    st.write(f"- {event['event']} (Priorität: {priority_text})")
            else:
                st.write("Keine Termine für heute.")

# Streamlit-Anwendung
def main():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        st.title("Benutzerregistrierung und -anmeldung")

        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Bild hinzufügen
            st.image("https://i0.wp.com/www.additudemag.com/wp-content/uploads/2018/03/For-Parents_DTPC-Motivation_bored-boy-at-desk_ts-866103068-cropped.jpeg", caption="Motivation", use_column_width=True)
            
            # Checkliste hinzufügen
            st.subheader("Motivations-Checkliste")
            st.checkbox("Aufstehen")
            st.checkbox("Frühstücken")
            st.checkbox("Tagesplanung")
            st.checkbox("Erstes To-Do erledigen")

        with col2:
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

if __name__ == "__main__":
    main()
