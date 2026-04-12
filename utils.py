def get_valid_habit(logs, message):

    habits = list(logs.keys())

    while True:
        try:
            num = int(input(message))
            if 1 <= num <= len(habits):
                return habits[num - 1]
            print("Invalid habit number.")
        except ValueError:
            print("Please enter a number.")
            

def get_multiple_habits(logs):

    habits = list(logs.keys())

    while True:
        try:
            nums = set(map(int, input("Enter habit numbers: ").split()))

            valid = []
            for n in nums:
                if 1 <= n <= len(habits):
                    valid.append(habits[n-1])
                else:
                    print(f"{n} is invalid.")
            
            if not valid:
                print("No valid habits selected.")
                continue
                    
            return valid

        except ValueError:
            print("Enter numbers separated by spaces.")