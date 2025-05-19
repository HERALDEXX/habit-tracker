from datetime import datetime
import ast
import sys

def debug_print(message):
    print(f"[DEBUG]: {message}")

debug_print("HERALDEXX HABIT TRACKER v1.0.0 is running...")

# Habits Storage
habits = []

# Storage Variable Global Initialization 
# (True storage located at the bottom of the file)
daily_logs = []
habit_streaks = {}

def load_habits():
    """Loads the habits list from the current script file."""
    try:
        with open(__file__, 'r') as file:
            content = file.read()
            if 'habits = [' in content:
                start = content.find('habits = [')
                if start != -1:
                    end = content.find(']', start) + 1
                    if end != 0:
                        habits_str = content[start:end].replace('habits = ', '')
                        return ast.literal_eval(habits_str)
    except Exception as e:
        print(f"Error loading habits: {e}")
    return []

def save_habits(habits_list):
    """Saves the habits list to the current script file."""
    try:
        with open(__file__, 'r') as file:
            lines = file.readlines()
        
        with open(__file__, 'w') as file:
            for line in lines:
                if not line.startswith(' ') and line.strip().startswith('habits ='):
                    file.write(f'habits = {habits_list}\n')
                else:
                    file.write(line)
        return True
    except Exception as e:
        print(f"Error saving habits: {e}")
        return False

def load_habit_streaks():
    """Loads the habit streaks from the current script file."""
    try:
        with open(__file__, 'r') as file:
            content = file.read()
            if 'habit_streaks = {' in content:
                start = content.find('habit_streaks = {')
                if start != -1:
                    end = content.find('}', start) + 1
                    if end != 0:
                        streaks_str = content[start:end].replace('habit_streaks = ', '')
                        return ast.literal_eval(streaks_str)
    except Exception as e:
        print(f"Error loading streaks: {e}")
    return {}

def setup_habits():
    """Prompts user to input their daily habits (2-10 habits)."""
    print("\n=== Setup Your Daily Habits ===")
    
    # Get number of habits to track
    while True:
        try:
            num_habits = int(input("How many habits would you like to track? (2-10): "))
            if 2 <= num_habits <= 10:
                break
            print("Please enter a number between 2 and 10.")
        except ValueError:
            print("Please enter a valid number.")
    
    print(f"\nPlease input your {num_habits} daily habits:")
    new_habits = []
    for i in range(num_habits):
        while True:
            habit = input(f"Habit #{i+1}: ").strip()
            if habit and habit not in new_habits:
                new_habits.append(habit)
                break
            elif habit in new_habits:
                print("You've already added this habit. Please enter a different one.")
            else:
                print("Please enter a valid habit.")
    return new_habits

def load_daily_logs():
    """Load daily logs from the script file."""
    try:
        with open(__file__, 'r') as file:
            content = file.read()
            if 'daily_logs = [' in content:
                start = content.find('daily_logs = [')
                if start != -1:
                    end = content.find(']', start) + 1
                    if end != 0:
                        logs_str = content[start:end].replace('daily_logs = ', '')
                        return ast.literal_eval(logs_str)
    except Exception as e:
        print(f"Error loading logs: {e}")
    return []

def save_daily_logs(logs):
    """Save daily logs to the script file."""
    try:
        with open(__file__, 'r') as file:
            lines = file.readlines()
        
        with open(__file__, 'w') as file:
            # Write everything until storage section
            for line in lines:
                if line.strip().startswith('# Daily logs storage'):
                    break
                file.write(line)
            
            # Write storage section
            file.write('\n# Daily logs storage\n')
            file.write(f'daily_logs = {logs}\n\n')
            file.write('# Habit streaks storage\n')
            file.write(f'habit_streaks = {habit_streaks}\n')
        return True
    except Exception as e:
        print(f"Error saving logs: {e}")
        return False

def log_habits():
    """Log completion status for each habit."""
    today = datetime.now().strftime('%Y-%m-%d')
    new_logs = []
    
    print("\n=== Daily Habit Check-in ===")
    print(f"Date: {today}")
    
    for habit in habits:
        while True:
            response = input(f"\nDid you complete '{habit}' today? (yes/no or y/n): ").lower()
            if response in ['y', 'yes']:
                completed = True
                new_logs.append((habit, today, completed))
                break
            elif response in ['n', 'no']:
                completed = False
                new_logs.append((habit, today, completed))
                break
            print("Please enter 'yes' or 'no' (or 'y' or 'n')")
    
    return new_logs

def update_streaks(logs):
    """Updates habit streaks based on daily logs."""
    global habit_streaks
    
    # Initialize streaks for new habits
    for habit in habits:
        if habit not in habit_streaks:
            habit_streaks[habit] = 0
    
    # Get all dates in chronological order
    dates = sorted(set(log[1] for log in logs))
    if not dates:
        return
    
    # Process logs date by date for each habit
    for habit in habits:
        current_streak = 0
        last_completed_date = None
        
        # Go through dates in reverse to count current streak
        for date in reversed(dates):
            # Find log for this habit on this date
            habit_log = next((log for log in logs if log[0] == habit and log[1] == date), None)
            
            if habit_log:
                _, log_date, completed = habit_log
                current_date = datetime.strptime(log_date, '%Y-%m-%d')
                
                if completed:
                    if last_completed_date is None:
                        # First completed date in the streak
                        current_streak = 1
                        last_completed_date = current_date
                    else:
                        # Check if this date is consecutive with last completed date
                        days_between = (last_completed_date - current_date).days
                        if days_between == 1:
                            # Consecutive day, add to streak
                            current_streak += 1
                            last_completed_date = current_date
                        else:
                            # Break in streak, we can stop checking earlier dates
                            break
                else:
                    # Habit not completed, streak ends
                    break
        
        # Update the streak for this habit
        habit_streaks[habit] = current_streak

def display_logs(logs):
    """Display all logged entries with streaks."""
    if not logs:
        print("\nNo logs found!")
        return
        
    print("\nAll recorded logs:")
    # Group logs by date
    dates = sorted(set(log[1] for log in logs))
    for date in dates:
        print(f"\nDate: {date}")
        for log in logs:
            if log[1] == date:
                habit, _, completed = log
                status = "✓" if completed else "✗"
                streak = habit_streaks.get(habit, 0)
                streak_display = f"🔥 {streak}" if streak > 0 else ""
                print(f"  {habit}: {status} {streak_display}")

def clear_logs():
    """Clear all stored logs"""
    try:
        with open(__file__, 'r') as file:
            lines = file.readlines()
        
        with open(__file__, 'w') as file:
            # Write all lines until storage section
            for line in lines:
                if line.strip().startswith('# Daily logs storage'):
                    break
                file.write(line)
            
            # Write empty storage
            file.write('\n# Daily logs storage\n')
            file.write('daily_logs = []\n\n')
            file.write('# Habit streaks storage\n')
            file.write('habit_streaks = {}\n')
        print("\nAll logs have been cleared successfully!")
        return True
    except Exception as e:
        print(f"Error clearing logs: {e}")
        return False

def reset_all():
    """Reset everything - clear habits, logs, and streaks."""
    try:
        with open(__file__, 'r') as file:
            lines = file.readlines()
        
        with open(__file__, 'w') as file:
            # Write non-storage content
            for line in lines:
                if line.strip().startswith('habits ='):
                    file.write('habits = []\n')
                elif line.strip().startswith('# Daily logs storage'):
                    break
                else:
                    file.write(line)
            
            # Write empty storage sections
            file.write('\n# Daily logs storage\n')
            file.write('daily_logs = []\n\n')
            file.write('# Habit streaks storage\n')
            file.write('habit_streaks = {}\n')
        print("\nAll habits, logs, and streaks have been reset!")
        return True
    except Exception as e:
        print(f"Error resetting data: {e}")
        return False

if __name__ == "__main__":
    # Load habits and streaks
    loaded_habits = load_habits()
    if loaded_habits:
        habits.clear()
        habits.extend(loaded_habits)
    
    # Load habit streaks and daily logs
    loaded_streaks = load_habit_streaks()
    if loaded_streaks:
        habit_streaks.clear()
        habit_streaks.update(loaded_streaks)
    
    daily_logs = load_daily_logs()
    # Update streaks based on existing logs
    if daily_logs:
        update_streaks(daily_logs)
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-v-logs', '--view-logs']:
            display_logs(daily_logs)
            sys.exit(0)
        elif sys.argv[1] in ['-c-logs', '--clear-logs']:
            clear_logs()
            habit_streaks.clear()  # Reset streaks when logs are cleared
            sys.exit(0)
        elif sys.argv[1] in ['-r', '--reset']:
            if reset_all():
                print("\nProgram has been reset. Run without arguments to start fresh.")
                sys.exit(0)
            else:
                print("\nWarning: There was an issue resetting the program.")
                sys.exit(1)
        else:
            print("Invalid option. Use:")
            print("  -v-logs or --view-logs to view logs")
            print("  -c-logs or --clear-logs to clear all logs")
            print("  -r or --reset to reset everything (habits, logs, and streaks)")
            sys.exit(0)
    
    # Regular program flow - check if habits need to be set up
    if not habits:
        print("No habits found! Let's set up your daily habits first.")
        new_habits = setup_habits()
        habits.clear()
        habits.extend(new_habits)
        if save_habits(habits):
            print("\nHabits saved successfully!")
            # Initialize streaks for new habits
            for habit in habits:
                habit_streaks[habit] = 0
            save_daily_logs([])  # Save empty logs and initialize streaks
        else:
            print("\nWarning: There was an issue saving the habits.")
            sys.exit(1)
    
    # Normal daily check-in flow
    new_logs = log_habits()
    daily_logs.extend(new_logs)
    update_streaks(daily_logs)  # Update streaks with new logs
    
    if save_daily_logs(daily_logs):
        print("\nToday's logs have been recorded successfully!")
        display_logs(daily_logs)
    else:
        print("\nWarning: There was an issue saving the logs.")




# Daily logs storage
daily_logs = []

# Habit streaks storage
habit_streaks = {}
