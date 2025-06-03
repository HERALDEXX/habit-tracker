# Contains the logic for managing habits and their associated data.
from datetime import datetime, timedelta
from colorama import Fore, Style

def validate_date_format(date_str):
    """Validate that a date string is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_habit_data(habits, habit_streaks):
    """Validate habits and streaks data structure"""
    if not isinstance(habits, list):
        return False, "Invalid habits data type"
    if not isinstance(habit_streaks, dict):
        return False, "Invalid streaks data type"
    
    # Validate habit names
    for habit in habits:
        if not isinstance(habit, str):
            return False, "Invalid habit name type"
        if not habit.strip():
            return False, "Empty habit name"
        if len(habit) > 50:
            return False, "Habit name too long"
            
    # Validate streak values
    for habit, streak in habit_streaks.items():
        if not isinstance(habit, str):
            return False, "Invalid streak habit name type"
        if not isinstance(streak, int):
            return False, "Invalid streak value type"
        if streak < 0:
            return False, "Negative streak value"
            
    return True, None

def validate_log_entry(log):
    """Validate a single log entry"""
    try:
        if not isinstance(log, (list, tuple)) or len(log) != 3:
            return False, "Invalid log entry format"
            
        habit, date, completed = log
        
        if not isinstance(habit, str) or not habit.strip():
            return False, "Invalid habit name in log"
            
        if not isinstance(date, str) or not validate_date_format(date):
            return False, "Invalid date format in log"
            
        if not isinstance(completed, bool):
            return False, "Invalid completion status in log"
            
        return True, None
    except Exception:
        return False, "Error validating log entry"

def update_streaks(logs, habits, habit_streaks):
    """Updates habit streaks based on daily logs with enhanced validation."""
    # Validate input data
    valid, error = validate_habit_data(habits, habit_streaks)
    if not valid:
        print(f"{Fore.LIGHTRED_EX}Error: {error}{Style.RESET_ALL}")
        return False
    
    try:
        # Initialize streaks for new habits
        for habit in habits:
            if habit not in habit_streaks:
                habit_streaks[habit] = 0
        
        # Filter and validate logs
        valid_logs = []
        for log in logs:
            log_valid, error = validate_log_entry(log)
            if log_valid:
                valid_logs.append(log)
            else:
                print(f"{Fore.LIGHTRED_EX}Warning: Skipping invalid log - {error}{Style.RESET_ALL}")
        
        # Get all valid dates in chronological order
        dates = sorted(set(
            log[1] for log in valid_logs 
            if log[0] in habits  # Only consider logs for current habits
        ))
        
        if not dates:
            return True  # No logs to process
        
        # Process logs date by date for each habit
        today = datetime.now().date()
        
        for habit in habits:
            current_streak = 0
            last_completed_date = None
            
            # Go through dates in reverse to count current streak
            for date in reversed(dates):
                log_date = datetime.strptime(date, '%Y-%m-%d').date()
                
                # Don't count future dates
                if log_date > today:
                    continue
                
                # Find log for this habit on this date
                habit_log = next((
                    log for log in valid_logs 
                    if log[0] == habit and log[1] == date
                ), None)
                
                if habit_log:
                    _, _, completed = habit_log
                    
                    if completed:
                        if last_completed_date is None:
                            current_streak = 1
                            last_completed_date = log_date
                        else:
                            days_between = (last_completed_date - log_date).days
                            if days_between == 1:  # Consecutive days
                                current_streak += 1
                                last_completed_date = log_date
                            else:  # Break in streak
                                break
                    else:  # Not completed
                        break
            
            # Update streak for this habit
            habit_streaks[habit] = current_streak
            
        return True
        
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error updating streaks: {e}{Style.RESET_ALL}")
        return False

def log_habits(habits):
    """Log completion status for each habit with validation."""
    if not isinstance(habits, list):
        print(f"{Fore.LIGHTRED_EX}Error: Invalid habits data format{Style.RESET_ALL}")
        return None
    
    if not habits:
        print(f"{Fore.LIGHTRED_EX}Error: No habits to log{Style.RESET_ALL}")
        return None
        
    today = datetime.now().strftime('%Y-%m-%d')
    new_logs = []
    
    print(f"\n{Fore.LIGHTWHITE_EX}=== Daily Habit Check-in ==={Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}Date: {today}{Style.RESET_ALL}")
    
    try:
        for habit in habits:
            if not isinstance(habit, str) or not habit.strip():
                print(f"{Fore.LIGHTRED_EX}Warning: Skipping invalid habit{Style.RESET_ALL}")
                continue
                
            while True:
                print(f"\n{Fore.LIGHTGREEN_EX}Did you complete '{Fore.LIGHTBLUE_EX}{habit}{Fore.LIGHTGREEN_EX}' today? (yes/no or y/n): {Style.RESET_ALL}", end='')
                response = input().lower().strip()
                
                if response in ['y', 'yes', 'n', 'no']:
                    completed = response in ['y', 'yes']
                    new_logs.append([str(habit), today, completed])
                    break
                    
                print(f"{Fore.LIGHTRED_EX}Please enter 'yes' or 'no' (or 'y' or 'n'){Style.RESET_ALL}")
                
    except KeyboardInterrupt:
        print(f"\n{Fore.LIGHTRED_EX}Log entry cancelled.{Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error logging habits: {e}{Style.RESET_ALL}")
        return None
    
    return new_logs if new_logs else None