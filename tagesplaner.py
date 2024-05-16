import streamlit as st
import pandas as pd
from datetime import datetime

import streamlit as st
import sqlite3
import calendar

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

# Funktion zur Erstellung eines Kalenderansichts für den gegebenen Monat und Jahr
def calendar_view(year, month):
    cal = calendar.monthcalendar(year, month)
    return cal

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
                
                # Zeige den Kalender für den aktuellen Monat an
                today = datetime.today()
                year, month = today.year, today.month
                cal = calendar_view(year, month)
                st.write("**Kalenderansicht:**")
                for week in cal:
                    for day in week:
                        if day == 0:
                            st.write("  ", end="")
                        else:
                            st.write(f"{day:2}", end="  ")
                    st.write()

            else:
                st.error("Ungültige Anmeldeinformationen!")

if __name__ == "__main__":
    main()
