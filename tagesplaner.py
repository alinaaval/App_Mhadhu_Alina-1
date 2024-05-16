import streamlit as st
import pandas as pd
import calendar

# Funktion zur Erstellung eines Kalenderansichts für den gegebenen Monat und Jahr
def calendar_view(year, month, tasks):
    cal = calendar.monthcalendar(year, month)
    weeks_in_month = len(cal)
    cal_df = pd.DataFrame(cal)
    cal_df = cal_df.replace(0, '')
    cal_df.columns = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

    # Farben je nach Aufgabenpriorität
    for day in range(1, 32):
        if day in tasks:
            priority = tasks[day]['priority']
            if priority == 'Hoch':
                cal_df[cal_df == day] = f'<div style="background-color: #FF9999; border-radius: 50%; padding: 5px;">{day}</div>'
            elif priority == 'Mittel':
                cal_df[cal_df == day] = f'<div style="background-color: #FFFF99; border-radius: 50%; padding: 5px;">{day}</div>'
            elif priority == 'Niedrig':
                cal_df[cal_df == day] = f'<div style="background-color: #D3FFD3; border-radius: 50%; padding: 5px;">{day}</div>'

    return cal_df, weeks_in_month

# Streamlit-Anwendung
def main():
    st.title("Kalender App")

    # Eingabefelder für Jahr und Monat
    year = st.number_input("Jahr", min_value=1900, max_value=2100, value=2024)
    month = st.selectbox("Monat", range(1, 13))

    # Dummy-Aufgaben für Testzwecke
    tasks = {
        5: {'priority': 'Hoch'},
        10: {'priority': 'Mittel'},
        15: {'priority': 'Niedrig'}
    }

    # Anzeige des Kalenders für das ausgewählte Jahr und Monat
    cal_df, weeks_in_month = calendar_view(year, month, tasks)
    st.write("**Kalenderansicht für", calendar.month_name[month], year, ":**")

    # CSS für größere Zellen im Kalender
    st.markdown("""
        <style>
        .calendar-table th, .calendar-table td {
            padding: 10px;
            text-align: center;
            font-size: 16px;
        }
        </style>
        """, unsafe_allow_html=True)

    # Erstellung des interaktiven Kalenders
    with st.markdown('<div class="calendar-table">', unsafe_allow_html=True):
        for i in range(weeks_in_month):
            st.write(cal_df.iloc[i, :])

    # Eingabefeld für eine Aufgabe an einem bestimmten Tag
    selected_day = st.number_input("Tag", min_value=1, max_value=31)
    task = st.text_input("Aufgabe für den ausgewählten Tag")

    # Dropdown für die Priorität der Aufgabe
    priority = st.selectbox("Priorität", ['Hoch', 'Mittel', 'Niedrig'])

    # Button zum Speichern der Aufgabe
    if st.button("Aufgabe speichern"):
        tasks[selected_day] = {'priority': priority}
        st.success(f"Aufgabe '{task}' für den {selected_day}.{month}.{year} gespeichert!")

if __name__ == "__main__":
    main()
