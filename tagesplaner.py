import streamlit as st
import pandas as pd
import calendar
from datetime import datetime

# Global DataFrames initialized
users = pd.DataFrame(columns=['username', 'password'])
tasks = pd.DataFrame(columns=['username', 'date', 'description', 'importance'])
events = pd.DataFrame(columns=['username', 'date', 'description', 'priority'])

import streamlit as st
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

# Streamlit-Anwendung
def main():
    st.title("Benutzerregistrierung und -anmeldung")

    # Benutzerregistrierung
    st.subheader("Registrierung")
    new_username = st.text_input("Benutzername")
    new_password = st.text_input("Passwort", type="password")
    if st.button("Registrieren"):
        if register(new_username, new_password):
            st.success("Registrierung erfolgreich!")
        else:
            st.error("Benutzername bereits vergeben!")

    # Benutzeranmeldung
    st.subheader("Anmeldung")
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")
    if st.button("Anmelden"):
        if login(username, password):
            st.success("Anmeldung erfolgreich!")
            st.write("Willkommen zurück,", username)
        else:
            st.error("Ungültige Anmeldeinformationen!")

username = st.text_input("Benutzername", key="username_input")


if __name__ == "__main__":
    main()

