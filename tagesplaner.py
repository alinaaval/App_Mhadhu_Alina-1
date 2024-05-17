import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta

import sqlite3

# Verbindung zur SQLite-Datenbank herstellen (oder erstellen, falls nicht vorhanden)
conn = sqlite3.connect('user_data.db')
c = conn.cursor()

# Tabellen für Benutzer und Kalendereinträge erstellen, falls sie noch nicht existieren
def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    
    # Tabelle events neu erstellen
    c.execute('''DROP TABLE IF EXISTS events''')
    c.execute('''CREATE TABLE events
                 (id INTEGER PRIMARY KEY, username TEXT, date TEXT, event TEXT)''')
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

# Funktion zur Anzeige der Tagesansicht
def show_day_view(date):
    st.title("Tagesansicht")
    st.write(f"Anzeigen von Informationen für {date}")

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

# Funktion zur Terminhinzufügung
def add_event(username, date, event):
    try:
        c.execute("INSERT INTO events (username, date, event) VALUES (?, ?, ?)", (username, date, event))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Fehler beim Hinzufügen des Termins: {e}")

# Funktion zur Anzeige von Terminen
def show_events(username, date):
    try:
        c.execute("SELECT event FROM events WHERE username=? AND date=?", (username, date))
        events = c.fetchall()
        return [event[0] for event in events]
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
                    date = datetime(year, month, day)
                    if cols[calendar.weekday(year, month, day)].button(str(day)):
                        show_day_view(date)
                        events = show_events(username, date.strftime("%Y-%m-%d"))
                        if events:
                            st.write("Termine:")
                            for event in events:
                                st.write(event)
                        else:
                            st.write("Keine Termine für diesen Tag.")

        # Event hinzufügen
        st.subheader("Neuen Termin hinzufügen")
        event_description = st.text_input("Terminbeschreibung")
        if st.button("Hinzufügen"):
            if event_description:
                add_event(username, selected_date_str, event_description)
                st.success("Termin hinzugefügt!")
            else:
                st.error("Bitte eine Terminbeschreibung eingeben.")

if __name__ == "__main__":
    main()
