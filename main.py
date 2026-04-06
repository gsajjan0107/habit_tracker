from storage import load_habits
from habits import add_habit, delete_habit, rename_habit, mark_habit_done
from ui import show_habits, dashboard
from utils import get_valid_habit, get_multiple_habits


def main():
    
    logs = load_habits()

    while True:
    
        print("""
---Habit Tracker---
1 Add habit 
2 Delete habit
3 Rename habit
4 Mark habit done
5 View dashboard
6 Exit
""")
        while True:
            choice = input("Choice: ")
            if choice in {"1","2","3","4","5","6"}:
                break
            print("Please enter a valid option number.")


        if choice == "1":
            habit = input("New habit: ")
            add_habit(habit, logs)


        elif choice == "2":
            if not logs:
                print("No habits found. Add one first.")
                continue

            show_habits(logs)
            habit = get_valid_habit("Habit number: ")
            delete_habit(habit, logs)


        elif choice == "3":
            if not logs:
                print("No habits found. Add one first.")
                continue
            
            show_habits(logs)
            habit = get_valid_habit("Habit number: ")
            new = input("New name: ")
            rename_habit(habit, new, logs)


        elif choice == "4":
            if not logs:
                print("No habits found. Add one first.")
                continue

            show_habits(logs)
            habits = get_multiple_habits(logs)
            
            for habit in habits:
                mark_habit_done(habit, logs)


        elif choice == "5":
            dashboard(logs)


        elif choice == "6":
            break

if __name__ == "__main__":
    main()