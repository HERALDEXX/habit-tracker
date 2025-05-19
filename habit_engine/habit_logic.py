# Contains the logic for managing habits and their associated data.
## This module is responsible for the core functionality of the Habit Tracker application.

from datetime import datetime

def validate_date_format(date_str):
    """Validate that a date string is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def update_streaks(logs, habits, habit_streaks):
    """Updates habit streaks based on daily logs."""
    if not isinstance(habits, list) or not isinstance(habit_streaks, dict):
        print("Error: Invalid data format for habits or streaks")
        return
    
    # Initialize streaks for new habits
    for habit in habits:
        if habit not in habit_streaks:
            habit_streaks[habit] = 0
    
    try:
        # Get all valid dates in chronological order
        dates = sorted(set(
            log[1] for log in logs 
            if isinstance(log, (list, tuple)) 
            and len(log) >= 2 
            and validate_date_format(log[1])
        ))
        
        if not dates:
            return
        
        # Process logs date by date for each habit
        for habit in habits:
            current_streak = 0
            last_completed_date = None
            
            # Go through dates in reverse to count current streak
            for date in reversed(dates):
                # Find log for this habit on this date
                habit_log = next((
                    log for log in logs 
                    if isinstance(log, (list, tuple)) 
                    and len(log) >= 3 
                    and log[0] == habit 
                    and log[1] == date
                ), None)
                
                if habit_log:
                    _, log_date, completed = habit_log
                    current_date = datetime.strptime(log_date, '%Y-%m-%d')
                    
                    if completed:
                        if last_completed_date is None:
                            current_streak = 1
                            last_completed_date = current_date
                        else:
                            days_between = (last_completed_date - current_date).days
                            if days_between == 1:
                                current_streak += 1
                                last_completed_date = current_date
                            else:
                                break
                    else:
                        break
            
            habit_streaks[habit] = current_streak
    except Exception as e:
        print(f"Error updating streaks: {e}")

def log_habits(habits):
    """Log completion status for each habit."""
    if not isinstance(habits, list):
        print("Error: Invalid habits data format")
        return []
        
    today = datetime.now().strftime('%Y-%m-%d')
    new_logs = []
    
    print("\n=== Daily Habit Check-in ===")
    print(f"Date: {today}")
    
    try:
        for habit in habits:
            while True:
                response = input(f"\nDid you complete '{habit}' today? (yes/no or y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    completed = True
                    new_logs.append([str(habit), today, completed])
                    break
                elif response in ['n', 'no']:
                    completed = False
                    new_logs.append([str(habit), today, completed])
                    break
                print("Please enter 'yes' or 'no' (or 'y' or 'n')")
    except KeyboardInterrupt:
        print("\nLog entry cancelled.")
        return []
    except Exception as e:
        print(f"Error logging habits: {e}")
        return []
    
    return new_logs