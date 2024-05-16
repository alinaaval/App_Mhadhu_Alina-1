import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta

import sqlite3

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

# Funktion zum Ausloggen
def logout():
    st.session_state['authenticated'] = False

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
                else:
                    st.error("Ungültige Anmeldeinformationen!")
        return

    st.title("Kalender App")

    if st.button("Ausloggen"):
        logout()
        return

    # Date selection
    selected_date = st.date_input("Datum", value=datetime.today())

    if selected_date:
        year, month, _ = selected_date.year, selected_date.month, selected_date.day

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

        # Previous and Next Month Buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Vorheriger Monat"):
                year, month = previous_month(year, month)
                selected_date = datetime(year, month, 1)
        with col3:
            if st.button("Nächster Monat"):
                year, month = next_month(year, month)
                selected_date = datetime(year, month, 1)

# Funktion zur Aufgabenhinzufügung
def add_task(username, date, task):
    c.execute("INSERT INTO tasks (username, date, task) VALUES (?, ?, ?)", (username, date, task))
    conn.commit()

# Funktion zur Terminhinzufügung
def add_event(username, date, event):
    # Hier können Sie den Code zum Hinzufügen eines Termins in die Datenbank einfügen
    pass

# Funktion zum Abrufen aller Aufgaben für einen bestimmten Benutzer und ein bestimmtes Datum
def get_tasks(username, date):
    c.execute("SELECT task FROM tasks WHERE username=? AND date=?", (username, date))
    return c.fetchall()

# Funktion zum Abrufen aller Termine für einen bestimmten Benutzer und ein bestimmtes Datum
def get_events(username, date):
    # Hier können Sie den Code zum Abrufen aller Termine für einen Benutzer und ein Datum einfügen
    return []

# Funktion zur Anzeige der Tagesansicht
def show_day_view(date):
    st.title("(date)")
    st.write(f"Anzeigen von Informationen für {date}")

    # Aufgaben anzeigen
    tasks = get_tasks(st.session_state['username'], date.strftime("%Y-%m-%d"))
    if tasks:
        st.subheader("Aufgaben:")
        for task in tasks:
            st.write(task[0])

    # Termine anzeigen
    events = get_events(st.session_state['username'], date.strftime("%Y-%m-%d"))
    if events:
        st.subheader("Termine:")
        for event in events:
            st.write(event[0])

    # Formular zum Hinzufügen von Aufgaben
    new_task = st.text_input("Neue Aufgabe eingeben:")
    if st.button("Aufgabe hinzufügen"):
        add_task(st.session_state['username'], date.strftime("%Y-%m-%d"), new_task)
        st.success("Aufgabe hinzugefügt!")

    # Formular zum Hinzufügen von Terminen
    new_event = st.text_input("Neuer Termin eingeben:")
    if st.button("Termin hinzufügen"):
        add_event(st.session_state['username'], date.strftime("%Y-%m-%d"), new_event)
        st.success("Termin hinzugefügt!")


if __name__ == "__main__":
    main()
