from storage import load_habits, save_habits
from habits import add_habit, delete_habit, rename_habit, mark_habit_done
from ui import format_habits, format_dashboard
from utils import get_habit_by_index, get_multiple_by_indices


def select_single_habit(logs):
    if not logs:
        print("No habits found. Add one first.")
        return None

    print(format_habits(logs))

    while True:
        try:
            num = int(input("Habit number: "))
            habit = get_habit_by_index(logs, num)
            if habit:
                return habit
            print("Invalid habit number.")
        except ValueError:
            print("Enter a number.")


def main():
    
    success, logs = load_habits()

    if not success:
        print("Could not load habits file. Starting fresh.")

    while True:
    
        while True:
            print("""
---Habit Tracker---
1. Add habit 
2. Delete habit
3. Rename habit
4. Mark habit done
5. View dashboard
6. Exit
""")
            choice = input("Choice: ").strip()
            if choice in {"1","2","3","4","5","6"}:
                break
            print("Please enter a valid option number.")


        if choice == "1":
            habit = input("New habit: ")
            success, message = add_habit(habit, logs)
            print(message)

            if success:
                success, message = save_habits(logs)
                print(message)


        elif choice == "2":
            habit = select_single_habit(logs)
            if not habit:
                continue

            success, message = delete_habit(habit, logs)
            print(message)

            if success:
                success, message = save_habits(logs)
                print(message)

        elif choice == "3":
            habit = select_single_habit(logs)
            if not habit:
                continue

            new = input("New name: ")
            success, message = rename_habit(habit, new, logs)
            print(message)
            
            if success:
                success, message = save_habits(logs)
                print(message)


        elif choice == "4":
            if not logs:
                print("No habits found. Add one first.")
                continue

            print(format_habits(logs))

            try:
                nums = list(map(int, input("Enter numbers: ").split()))
            except ValueError:
                print("Enter numbers only.")
                continue

            valid, invalid = get_multiple_by_indices(logs, nums)

            for n in invalid:
                print(f"{n} is invalid.")

            for habit in valid:
                success, message = mark_habit_done(habit, logs)
                print(message)

            if valid:
                success, message = save_habits(logs)
                print(message)
            else:
                print("No valid habits selected.")
                continue


        elif choice == "5":
            print(format_dashboard(logs))


        elif choice == "6":
            break

if __name__ == "__main__":
    main()