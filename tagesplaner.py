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

# Funktion für die große Kalenderauswahl
def large_calendar_input(label, min_date=None, max_date=None, key=None):
    """Custom implementation of a large calendar date input."""
    selected_date = st.date_input(label, min_value=min_date, max_value=max_date, key=key)
    return selected_date

# Funktion zur Erstellung eines Monatskalenders
def calendar_view(year, month):
    """Create a calendar view for the given month and year."""
    cal = calendar.monthcalendar(year, month)
    return cal

# Funktion zur Ermittlung des vorherigen Monats
def previous_month(current_year, current_month):
    """Get the previous month."""
    previous_month_year = current_year
    previous_month = current_month - 1
    if previous_month < 1:
        previous_month = 12
        previous_month_year -= 1
    return previous_month_year, previous_month

# Funktion zur Ermittlung des nächsten Monats
def next_month(current_year, current_month):
    """Get the next month."""
    next_month_year = current_year
    next_month = current_month + 1
    if next_month > 12:
        next_month = 1
        next_month_year += 1
    return next_month_year, next_month

# Streamlit-Anwendung
def main():
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

                # Kalender App nach erfolgreicher Anmeldung anzeigen
                app()
            else:
                st.error("Ungültige Anmeldeinformationen!")

def app():
    st.title("Kalender App")

    # Date selection
    selected_date = large_calendar_input("Datum")

    if selected_date:
        year, month, _ = selected_date.year, selected_date.month, selected_date.day

        # Show calendar
        st.subheader(calendar.month_name[month] + " " + str(year))
        cal = calendar_view(year, month)
        cols = st.columns(7)
        for week in cal:
            for day in week:
                if day != 0:
                    cols[calendar.weekday(year, month, day)].write(str(day))

        # Previous and Next Month Buttons
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("Vorheriger Monat"):
                year, month = previous_month(year, month)
                selected_date = datetime(year, month, 1)
        with col3:
            if st.button("Nächster Monat"):
                year, month = next_month(year, month)
                selected_date = datetime(year, month, 1)

if __name__ == "__main__":
    main()
