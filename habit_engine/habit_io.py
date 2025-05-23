# Handles all reading and writing of habits to a file.

import json
import os
import stat
import shutil

import sys
from colorama import Fore, Style

# Detect base path depending on whether the app is frozen (compiled with PyInstaller) or not
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# File paths
DATA_DIR = os.path.join(BASE_DIR, 'data')
PLOTS_DIR = os.path.join(DATA_DIR, 'plots')
HABITS_FILE = os.path.join(DATA_DIR, 'habits.json')
LOGS_FILE = os.path.join(DATA_DIR, 'logs.json')
STREAKS_FILE = os.path.join(DATA_DIR, 'streaks.json')

# Core files to protect
CORE_FILES = [
    os.path.join(os.path.dirname(__file__), '__init__.py'),
    os.path.join(os.path.dirname(__file__), 'habit_setup.py'),
    os.path.join(os.path.dirname(__file__), 'habit_io.py'),
    os.path.join(os.path.dirname(__file__), 'habit_logic.py'),
    os.path.join(os.path.dirname(__file__), 'habit_display.py'),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main.py'),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.md')
]

def make_files_readonly():
    """Make all core application files read-only."""
    success = True
    protected_files = []
    for file_path in CORE_FILES:
        try:
            if os.path.exists(file_path):
                # Get current permissions
                current_permissions = os.stat(file_path).st_mode
                # Remove write permissions while preserving other permissions
                readonly_permissions = current_permissions & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
                # Apply new permissions
                os.chmod(file_path, readonly_permissions)
                protected_files.append(os.path.basename(file_path))
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Error setting read-only for {os.path.basename(file_path)}: {e}{Style.RESET_ALL}")
            success = False
    
    if protected_files:
        print(f"{Fore.LIGHTGREEN_EX}Protected {len(protected_files)} core files.{Style.RESET_ALL}")
    return success

def make_files_writable():
    """Make all core application files writable again."""
    success = True
    writable_files = []
    for file_path in CORE_FILES:
        try:
            if os.path.exists(file_path):
                # Get current permissions
                current_permissions = os.stat(file_path).st_mode
                # Add write permissions while preserving other permissions
                writable_permissions = current_permissions | stat.S_IWUSR
                # Apply new permissions
                os.chmod(file_path, writable_permissions)
                writable_files.append(os.path.basename(file_path))
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Error setting writable for {os.path.basename(file_path)}: {e}{Style.RESET_ALL}")
            success = False
    
    if writable_files:
        print(f"{Fore.LIGHTGREEN_EX}Unlocked {len(writable_files)} core files for development.{Style.RESET_ALL}")
    return success

def initialize_data_files():
    """Initialize all necessary data files if they don't exist."""
    try:
        # Ensure data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(PLOTS_DIR, exist_ok=True)
        
        # Initialize habits.json if it doesn't exist
        if not os.path.exists(HABITS_FILE):
            with open(HABITS_FILE, 'w') as file:
                json.dump([], file)
        
        # Initialize logs.json if it doesn't exist
        if not os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, 'w') as file:
                json.dump([], file)
        
        # Initialize streaks.json if it doesn't exist
        if not os.path.exists(STREAKS_FILE):
            with open(STREAKS_FILE, 'w') as file:
                json.dump({}, file)
        
        # Make core files read-only
        make_files_readonly()
                
        return True
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error initializing data files: {e}{Style.RESET_ALL}")
        return False

def load_habits():
    """Loads the habits list from file."""
    try:
        if os.path.exists(HABITS_FILE):
            with open(HABITS_FILE, 'r') as file:
                habits = json.load(file)
                return [str(habit) for habit in habits] if isinstance(habits, list) else []
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error loading habits: {e}{Style.RESET_ALL}")
    return []

def save_habits(habits_list):
    """Saves the habits list to file."""
    try:
        # Validate habits list
        if not isinstance(habits_list, list):
            print(f"{Fore.LIGHTRED_EX}Error: Invalid habits data format{Style.RESET_ALL}")
            return False
            
        with open(HABITS_FILE, 'w') as file:
            json.dump(habits_list, file, indent=2)
        return True
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error saving habits: {e}{Style.RESET_ALL}")
        return False

def load_habit_streaks():
    """Loads the habit streaks from file."""
    try:
        if os.path.exists(STREAKS_FILE):
            with open(STREAKS_FILE, 'r') as file:
                streaks = json.load(file)
                # Ensure all values are integers
                return {str(k): int(v) for k, v in streaks.items()} if isinstance(streaks, dict) else {}
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error loading streaks: {e}{Style.RESET_ALL}")
    return {}

def load_daily_logs():
    """Load daily logs from file."""
    try:
        if os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, 'r') as file:
                logs = json.load(file)
                # Validate log format
                if isinstance(logs, list):
                    valid_logs = []
                    for log in logs:
                        if isinstance(log, list) and len(log) == 3:
                            habit, date, completed = log
                            valid_logs.append([str(habit), str(date), bool(completed)])
                    return valid_logs
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error loading logs: {e}{Style.RESET_ALL}")
    return []

def save_daily_logs(logs, streaks):
    """Save daily logs and streaks to files."""
    try:
        # Validate logs and streaks
        if not isinstance(logs, list) or not isinstance(streaks, dict):
            print(f"{Fore.LIGHTRED_EX}Error: Invalid data format{Style.RESET_ALL}")
            return False
            
        with open(LOGS_FILE, 'w') as file:
            json.dump(logs, file, indent=2)
        with open(STREAKS_FILE, 'w') as file:
            json.dump(streaks, file, indent=2)
        return True
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error saving logs: {e}{Style.RESET_ALL}")
        return False

def reset_app_data():
    """Reset all application data including habits, logs, streaks, and plots."""
    try:
        # Reset JSON files
        if os.path.exists(HABITS_FILE):
            with open(HABITS_FILE, 'w') as file:
                json.dump([], file)
        
        if os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, 'w') as file:
                json.dump([], file)
                
        if os.path.exists(STREAKS_FILE):
            with open(STREAKS_FILE, 'w') as file:
                json.dump({}, file)
        
        # Clear plots directory
        if os.path.exists(PLOTS_DIR):
            shutil.rmtree(PLOTS_DIR)
            os.makedirs(PLOTS_DIR, exist_ok=True)
            
        return True
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error resetting application data: {e}{Style.RESET_ALL}")
        return False

def clear_tracking_data():
    """Clear all tracking data (logs, streaks, and plots) but keep habits."""
    try:
        # Clear logs
        if os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, 'w') as file:
                json.dump([], file)
                
        # Clear streaks
        if os.path.exists(STREAKS_FILE):
            with open(STREAKS_FILE, 'w') as file:
                json.dump({}, file)
        
        # Clear plots directory
        if os.path.exists(PLOTS_DIR):
            shutil.rmtree(PLOTS_DIR)
            os.makedirs(PLOTS_DIR, exist_ok=True)
            
        return True
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error clearing tracking data: {e}{Style.RESET_ALL}")
        return False