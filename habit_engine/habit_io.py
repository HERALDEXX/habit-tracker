# Handles all reading and writing of habits to a file.

import json
import os
import stat
import shutil
from datetime import datetime
from pathlib import Path

import sys
from colorama import Fore, Style

DEFAULT_SETTINGS = {
    "appearance_mode": "System",
    "autosave_interval": 30,
    "daily_reminder_enabled": 0,
    "reminder_time": "09:00",
    "chart_style": "Line Plot",
    "show_streak_annotations": True,
    "chart_date_range": "Last 30 Days"
}    

# Detect base path depending on whether the app is frozen (compiled with PyInstaller) or not
if getattr(sys, 'frozen', False):
    # When running as executable, use user's home directory
    BASE_DIR = os.path.join(os.path.expanduser('~'), '.heraldexx-habit-tracker')
else:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Define data directory relative to the base directory
DATA_DIR = os.path.join(BASE_DIR, "data")
PLOTS_DIR = os.path.join(DATA_DIR, "plots")

# For assets, we need to handle PyInstaller's _MEIPASS
if getattr(sys, 'frozen', False):
    ASSETS_DIR = os.path.join(sys._MEIPASS, "assets")
else:
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Ensure data directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

# Define file paths using os.path for cross-platform compatibility
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")
HABITS_FILE = os.path.join(DATA_DIR, "habits.json")
LOGS_FILE = os.path.join(DATA_DIR, "logs.json")
STREAKS_FILE = os.path.join(DATA_DIR, "streaks.json")

# Core files to protect
CORE_FILES = [
    os.path.join(os.path.dirname(__file__), '__init__.py'),
    os.path.join(os.path.dirname(__file__), 'habit_setup.py'),
    os.path.join(os.path.dirname(__file__), 'habit_io.py'),
    os.path.join(os.path.dirname(__file__), 'habit_logic.py'),
    os.path.join(os.path.dirname(__file__), 'habit_display.py'),
    os.path.join(os.path.dirname(__file__), 'gui.py'),
    os.path.join(os.path.dirname(__file__), 'habit_visualization.py'),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main.py'),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.md'),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'LICENSE')
]

def _write_defaults():
    """Helper to write DEFAULT_SETTINGS to settings.json"""
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_SETTINGS, f, indent=2)

def load_settings():
    """
    Load settings.json from disk. If it doesn’t exist, create it
    with defaults and return the defaults.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(SETTINGS_PATH):
        _write_defaults()
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, val in DEFAULT_SETTINGS.items():
            data.setdefault(key, val)
        return data.copy()    
    except (json.JSONDecodeError, IOError):
        # If file is corrupted, overwrite with defaults
        _write_defaults()
        return DEFAULT_SETTINGS.copy()

def save_settings(settings: dict):
    """
    Overwrite settings.json with the provided dict.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)   

def get_asset_path(filename):
    """Get the correct path to an asset file that works in both development and PyInstaller modes."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.join(sys._MEIPASS, 'assets', filename)
    else:
        # Running in development
        return os.path.join(ASSETS_DIR, filename)

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

def save_with_backup(file_path, data):
    """Save data with backup to prevent corruption"""
    backup_path = file_path + '.bak'
    temp_path = file_path + '.tmp'
    try:
        # First write to temporary file
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
            
        # If original exists, create backup
        if os.path.exists(file_path):
            try:
                os.replace(file_path, backup_path)
            except:
                os.remove(backup_path)
                os.replace(file_path, backup_path)
                
        # Move temp file to final location
        try:
            os.replace(temp_path, file_path)
        except:
            os.remove(file_path)
            os.replace(temp_path, file_path)
            
        # Success - remove backup
        if os.path.exists(backup_path):
            os.remove(backup_path)
            
        return True
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error in save_with_backup: {e}{Style.RESET_ALL}")
        # Try to restore from backup
        if os.path.exists(backup_path):
            try:
                os.replace(backup_path, file_path)
            except:
                pass
        return False
    finally:
        # Cleanup temp files
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

def try_load_json(file_path, backup_path=None):
    """Try to load JSON file with backup recovery"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
    except:
        if backup_path and os.path.exists(backup_path):
            try:
                with open(backup_path, 'r') as f:
                    data = json.load(f)
                # Restore from backup
                save_with_backup(file_path, data)
                return data
            except:
                pass
    return None

def load_habits():
    """Loads the habits list from file with backup recovery."""
    try:
        habits = try_load_json(HABITS_FILE, HABITS_FILE + '.bak')
        return [str(habit) for habit in habits] if isinstance(habits, list) else []
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error loading habits: {e}{Style.RESET_ALL}")
        return []

def save_habits(habits_list):
    """Saves the habits list to file with backup protection."""
    try:
        # Validate habits list
        if not isinstance(habits_list, list):
            print(f"{Fore.LIGHTRED_EX}Error: Invalid habits data format{Style.RESET_ALL}")
            return False
            
        return save_with_backup(HABITS_FILE, habits_list)
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error saving habits: {e}{Style.RESET_ALL}")
        return False

def load_habit_streaks():
    """Loads the habit streaks from file with backup recovery."""
    try:
        streaks = try_load_json(STREAKS_FILE, STREAKS_FILE + '.bak')
        return {str(k): int(v) for k, v in streaks.items()} if isinstance(streaks, dict) else {}
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error loading streaks: {e}{Style.RESET_ALL}")
        return {}

def load_daily_logs():
    """Load daily logs from file with backup recovery."""
    try:
        logs = try_load_json(LOGS_FILE, LOGS_FILE + '.bak')
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
    """Save daily logs and streaks to files with backup protection."""
    try:
        # Validate logs and streaks
        if not isinstance(logs, list) or not isinstance(streaks, dict):
            print(f"{Fore.LIGHTRED_EX}Error: Invalid data format{Style.RESET_ALL}")
            return False
            
        # Save both files with backup protection
        logs_saved = save_with_backup(LOGS_FILE, logs)
        streaks_saved = save_with_backup(STREAKS_FILE, streaks)
        
        return logs_saved and streaks_saved
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
            
        # Reinitialize settings
        save_settings(DEFAULT_SETTINGS.copy())
        
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
    