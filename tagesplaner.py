import streamlit as st
import sqlite3
import calendar
from datetime import datetime

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
                          
        selected_date = st.session_state['selected_date']
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Previous"):
                selected_date = selected_date.replace(day=1) - pd.DateOffset(months=1)
                st.session_state['selected_date'] = selected_date
        with col2:
            st.write(selected_date.strftime("%B %Y"))
        with col3:
            if st.button("Next"):
                selected_date = selected_date.replace(day=28) + pd.DateOffset(days=4)  # ensures it moves to the next month
                selected_date = selected_date.replace(day=1)
                st.session_state['selected_date'] = selected_date

        # Show calendar
        cal = calendar_view(selected_date.year, selected_date.month)
        st.write("**Click on a day to add/view tasks and events**")
        for week in cal:
            cols = st.columns(7)
            for day, col in zip(week, cols):
                with col:
                    if day != 0:
                        date_str = f"{selected_date.year}-{selected_date.month:02}-{day:02}"
                        button_label = f"{day}"
                        day_tasks = get_tasks_by_date(st.session_state['username'], date_str)
                        day_events = get_events_by_date(st.session_state['username'], date_str)
                        if not day_tasks.empty or not day_events.empty:
                            task_importance = day_tasks['importance'].values if not day_tasks.empty else 

            else:
                st.error("Ungültige Anmeldeinformationen!")

if __name__ == "__main__":
    app()
