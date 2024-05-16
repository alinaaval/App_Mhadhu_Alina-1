import streamlit as st
import sqlite3
from datetime import datetime
from pytz import timezone
from dateutil.parser import parse
import pandas as pd

# Verbindung zur SQLite-Datenbank herstellen (oder erstellen, falls nicht vorhanden)
conn = sqlite3.connect('user_data.db')
c = conn.cursor()

# Tabelle für Benutzer erstellen, falls sie noch nicht existiert
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
conn.commit()

# Tabelle für Aufgaben und Termine erstellen, falls sie noch nicht existiert
c.execute('''CREATE TABLE IF NOT EXISTS tasks_events
             (id INTEGER PRIMARY KEY, username TEXT, date TEXT, description TEXT, priority TEXT)''')
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

# Funktion zur Hinzufügung einer Aufgabe oder eines Termins
def add_task_event(username, date, description, priority):
    c.execute("INSERT INTO tasks_events (username, date, description, priority) VALUES (?, ?, ?, ?)",
              (username, date, description, priority))
    conn.commit()

# Funktion zur Anzeige aller Aufgaben und Termine eines Benutzers
def get_tasks_events(username):
    c.execute("SELECT date, description, priority FROM tasks_events WHERE username=?", (username,))
    rows = c.fetchall()
    df = pd.DataFrame(rows, columns=['Date', 'Description', 'Priority'])
    return df

# Streamlit-Anwendung
def main():
    st.title("Kalender mit Aufgaben- und Terminverwaltung")

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
                
                # Kalender anzeigen
                st.subheader("Kalenderansicht")
                with st.spinner('Kalender wird geladen...'):
                    st.write("Hier ist der interaktive Kalender:")
                    st.write("Klicken Sie auf einen Tag, um eine Aufgabe oder einen Termin hinzuzufügen.")

                    # Anzeige des Fullcalendar-Widgets
                    st.write("""<div id='calendar'></div>""", unsafe_allow_html=True)

                    # JavaScript-Code für die Konfiguration des Fullcalendar-Widgets
                    js_code = f"""
                        <script>
                        document.addEventListener('DOMContentLoaded', function() {{
                            var calendarEl = document.getElementById('calendar');
                            var calendar = new FullCalendar.Calendar(calendarEl, {{
                                initialView: 'dayGridMonth',
                                selectable: true,
                                dateClick: function(info) {{
                                    var date = info.dateStr;
                                    var description = prompt('Beschreibung eingeben:');
                                    var priority = prompt('Priorität eingeben (Niedrig, Mittel, Hoch):');
                                    var username = '{login_username}';
                                    if (description && priority) {{
                                        var url = 'http://localhost:8501/add_task_event/' + username + '/' + date + '/' + description + '/' + priority;
                                        fetch(url);
                                        calendar.refetchEvents();
                                    }}
                                }},
                                eventSources: [{{
                                    url: 'http://localhost:8501/get_tasks_events/{login_username}',
                                    method: 'GET',
                                    extraParams: {{
                                        cacheBuster: new Date().toISOString()
                                    }},
                                    failure: function() {{
                                        alert('Fehler beim Laden von Aufgaben und Terminen.');
                                    }},
                                }}],
                            }});
                            calendar.render();
                        }});
                        </script>
                    """
                    st.write(js_code, unsafe_allow_html=True)
            else:
                st.error("Ungültige Anmeldeinformationen!")

if __name__ == "__main__":
    main()
