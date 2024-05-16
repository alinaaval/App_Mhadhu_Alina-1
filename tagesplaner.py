import streamlit as st
import pandas as pd
from datetime import datetime

# Dummy-Daten für Termine und Ereignisse
events_data = {
    "Datum": ["2024-05-01", "2024-05-02", "2024-05-02", "2024-05-03"],
    "Zeit": ["10:00", "15:30", "09:00", "14:00"],
    "Beschreibung": ["Meeting", "Geburtstagsfeier", "Arzttermin", "Projektpräsentation"]
}

events_df = pd.DataFrame(events_data)

def show_agenda(start_date, end_date):
    st.subheader("Agendaansicht")
    filtered_events = events_df[(events_df['Datum'] >= start_date) & (events_df['Datum'] <= end_date)]
    
    if filtered_events.empty:
        st.write("Keine Termine in diesem Zeitraum.")
    else:
        for index, row in filtered_events.iterrows():
            st.write(f"**{row['Datum']} - {row['Zeit']}**: {row['Beschreibung']}")


def app():
    st.title("Agenda App")

    # Datumauswahl für den Zeitraum der Agendaansicht
    start_date = st.date_input("Startdatum", value=datetime.today())
    end_date = st.date_input("Enddatum", value=datetime.today())

    if start_date > end_date:
        st.error("Das Startdatum kann nicht nach dem Enddatum liegen.")
    else:
        show_agenda(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))


if __name__ == "__main__":
    app()
