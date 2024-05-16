import streamlit as st
import pandas as pd
import calendar

# Funktion zur Erstellung eines Kalenderansichts für den gegebenen Monat und Jahr
def calendar_view(year, month):
    cal = calendar.monthcalendar(year, month)
    cal_df = pd.DataFrame(cal)
    cal_df = cal_df.replace(0, '')
    cal_df.columns = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
    return cal_df

# Streamlit-Anwendung
def main():
    st.title("Kalender App")

    # Eingabefelder für Jahr und Monat
    year = st.number_input("Jahr", min_value=1900, max_value=2100, value=2024)
    month = st.selectbox("Monat", range(1, 13))

    # Anzeige des Kalenders für das ausgewählte Jahr und Monat
    cal_df = calendar_view(year, month)
    st.write("**Kalenderansicht für", calendar.month_name[month], year, ":**")
    st.dataframe(cal_df)

    # Eingabefeld für eine Aufgabe an einem bestimmten Tag
    selected_day = st.number_input("Tag", min_value=1, max_value=31)
    task = st.text_input("Aufgabe für den ausgewählten Tag")

    # Button zum Speichern der Aufgabe
    if st.button("Aufgabe speichern"):
        st.success(f"Aufgabe '{task}' für den {selected_day}.{month}.{year} gespeichert!")

if __name__ == "__main__":
    main()
