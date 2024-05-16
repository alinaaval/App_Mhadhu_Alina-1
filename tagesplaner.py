import streamlit as st
import sqlite3
import calendar
from datetime import datetime
import pandas as pd

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
    cal_df = pd.DataFrame(cal)
    cal_df = cal_df.replace(0, '')
    cal_df.columns = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
    return cal_df

def app():
    # Custom CSS for pastel pink gradient and other styling
    st.markdown("""
        <style>
        html, body, [class*="css"] {
            height: 100%;
            background: linear-gradient(180deg, #FFC0CB, #FFB6C1, #FF69B4, #FF1493, #FFC0CB);
            color: #4B0082;
        }
        .low-importance {
            background-color: #D3FFD3;
        }
        .medium-importance {
            background-color: #FFFF99;
        }
        .high-importance {
            background-color: #FF9999;
        }
        .urgent-priority {
            border: 2px solid red;
            background-color: #FF9999;
        }
        .can-wait-priority {
            border: 2px solid green;
        }
        </style>
        """, unsafe_allow_html=True)

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
                
                # Öffne den Kalender in einem neuen Fenster
                st.sidebar.title("Kalender")
                today = datetime.today()
                year, month = today.year, today.month
                cal_df = calendar_view(year, month)
                st.sidebar.write("**Kalenderansicht für", calendar.month_name[month], year, ":**")
                st.sidebar.dataframe(cal_df)
            else:
                st.error("Ungültige Anmeldeinformationen!")

if __name__ == "__main__":
    app()
