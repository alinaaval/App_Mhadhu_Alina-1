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
                    date = datetime(year, month, day).strftime("%Y-%m-%d")
                    events = show_events(username, date)
                    button_text = str(day)
                    if events:
                        priority = max(event["priority"] for event in events)
                        button_color = "red" if priority == 3 else None
                        if cols[calendar.weekday(year, month, day)].button(button_text, key=f"day_button_{date}", help="Termine vorhanden", help_color=button_color):
                            show_day_view(date)
                            st.write("Termine:")
                            for event in events:
                                priority = event["priority"]
                                priority_text = "Niedrig" if priority == 1 else "Mittel" if priority == 2 else "Hoch"
                                st.write(f"- {event['event']} (Priorität: {priority_text})")
                    else:
                        if cols[calendar.weekday(year, month, day)].button(button_text, key=f"day_button_{date}"):
                            show_day_view(date)
                            st.write("Keine Termine für diesen Tag.")

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

if __name__ == "__main__":
    main()
