from datetime import datetime, timedelta
from collections import defaultdict

class Task:
    def __init__(self, name, priority, date):
        self.name = name
        self.priority = priority
        self.date = date
    
    def __repr__(self):
        return f"Task: {self.name}, Priority: {self.priority}, Date: {self.date}"

class DailyPlanner:
    def __init__(self):
        self.tasks = defaultdict(list)  # Verwende defaultdict, um Aufgaben nach Datum zu speichern

    def add_task(self, name, priority, date):
        task = Task(name, priority, date)
        self.tasks[date].append(task)
        # Aufgaben nach Priorität sortieren
        self.tasks[date].sort(key=lambda x: x.priority)

    def remove_task(self, date, name):
        if date in self.tasks:
            self.tasks[date] = [task for task in self.tasks[date] if task.name != name]
            if not self.tasks[date]:
                del self.tasks[date]

    def display_tasks(self, date):
        if date not in self.tasks or not self.tasks[date]:
            print(f"Keine Aufgaben am {date} vorhanden.")
        else:
            print(f"Aufgaben am {date} sortiert nach Priorität:")
            for task in self.tasks[date]:
                print(task)

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.daily_planner = DailyPlanner()

class CalendarApp:
    def __init__(self):
        self.users = {}
        self.logged_in_user = None

    def register_user(self, username, password):
        if username in self.users:
            print("Benutzername bereits vorhanden. Bitte wählen Sie einen anderen.")
        else:
            self.users[username] = User(username, password)
            print("Registrierung erfolgreich!")

    def login(self, username, password):
        if username in self.users and self.users[username].password == password:
            self.logged_in_user = self.users[username]
            print(f"Willkommen, {username}!")
        else:
            print("Ungültiger Benutzername oder Passwort.")

    def logout(self):
        if self.logged_in_user:
            print(f"Auf Wiedersehen, {self.logged_in_user.username}!")
            self.logged_in_user = None
        else:
            print("Sie sind derzeit nicht angemeldet.")

    def run(self):
        while True:
            print("\n1. Anmelden")
            print("2. Abmelden")
            print("3. Aufgabe hinzufügen")
            print("4. Aufgabe entfernen")
            print("5. Aufgaben anzeigen")
            print("6. Benutzer registrieren")
            print("7. Beenden")

            choice = input("Wählen Sie eine Option (1-7): ")

            if choice == "1":
                username = input("Benutzername: ")
                password = input("Passwort: ")
                self.login(username, password)
            
            elif choice == "2":
                self.logout()
            
            elif choice == "3":
                if not self.logged_in_user:
                    print("Sie müssen sich anmelden, um eine Aufgabe hinzuzufügen.")
                else:
                    name = input("Aufgabennamen eingeben: ")
                    priority = int(input("Priorität der Aufgabe eingeben (niedrigere Zahl = höhere Priorität): "))
                    date = input("Aufgabendatum eingeben (YYYY-MM-DD): ")
                    self.logged_in_user.daily_planner.add_task(name, priority, date)
                    print(f"Aufgabe '{name}' mit Priorität {priority} für den {date} hinzugefügt.")

            elif choice == "4":
                if not self.logged_in_user:
                    print("Sie müssen sich anmelden, um eine Aufgabe zu entfernen.")
                else:
                    date = input("Aufgabendatum eingeben (YYYY-MM-DD): ")
                    name = input("Aufgabennamen eingeben, um ihn zu entfernen: ")
                    self.logged_in_user.daily_planner.remove_task(date, name)
                    print(f"Aufgabe '{name}' am {date} entfernt.")

            elif choice == "5":
                if not self.logged_in_user:
                    print("Sie müssen sich anmelden, um Aufgaben anzuzeigen.")
                else:
                    date = input("Aufgabendatum eingeben (YYYY-MM-DD): ")
                    self.logged_in_user.daily_planner.display_tasks(date)

            elif choice == "6":
                username = input("Benutzername: ")
                password = input("Passwort: ")
                self.register_user(username, password)
            
            elif choice == "7":
                print("Programm wird beendet.")
                break
            
            else:
                print("Ungültige Option. Bitte wählen Sie eine gültige Option (1-7).")

if __name__ == "__main__":
    app = CalendarApp()
    app.run()
