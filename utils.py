def get_habit_by_index(logs, index):
    habits = get_sorted_habits(logs)

    if 1 <= index <= len(habits):
        return habits[index - 1]
    
    return None


def get_multiple_by_indices(logs, indices):
    habits = get_sorted_habits(logs)

    valid = []
    invalid = []

    for n in indices:
        if 1 <= n <= len(habits):
            valid.append(habits[n-1])
        else:
            invalid.append(n)
    
    return valid, invalid


def get_sorted_habits(logs):
    return sorted(logs)