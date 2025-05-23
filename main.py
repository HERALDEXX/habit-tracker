# Contains the main entry point for the Habit Tracker application.
import sys
from colorama import init, Fore, Style
import time
import msvcrt  # For Windows console handling
# Import all necessary functions from modules
from habit_engine.__init__ import __version__, __app_name__, __copyright__
from habit_engine.habit_setup import setup_habits
from habit_engine.habit_io import (
    load_habits,
    save_habits,
    load_habit_streaks,
    load_daily_logs,
    save_daily_logs,
    initialize_data_files,
    make_files_writable,
    make_files_readonly,
    reset_app_data,
    clear_tracking_data
)
from habit_engine.habit_logic import (
    update_streaks,
    log_habits
)
from habit_engine.habit_display import (
    display_logs,
    display_app_info
)
from habit_engine.habit_visualization import visualize_habit_streak

init()

def debug_print(message):
    print(f"{Fore.LIGHTCYAN_EX}[DEBUG]: {message}{Style.RESET_ALL}")

def wait_for_key():
    """Wait for a keypress on Windows."""
    if sys.platform == 'win32':
        print(f"\n{Fore.LIGHTWHITE_EX}Press any key to exit...{Style.RESET_ALL}")
        sys.stdout.flush()
        while True:
            if msvcrt.kbhit():
                msvcrt.getch()  # Get the pressed key
                break
            time.sleep(0.1)  # Reduce CPU usage

def handle_program_exit(exit_code=0, message=None):
    """Handle program exit with optional message."""
    try:
        # Show message first if provided
        if message:
            if exit_code == 0:
                print(f"{Fore.LIGHTGREEN_EX}{message}{Style.RESET_ALL}")
            else:
                print(f"{Fore.LIGHTRED_EX}{message}{Style.RESET_ALL}")
        
        # For all platforms when running as a binary
        if getattr(sys, 'frozen', False):
            # Ensure all output is flushed
            sys.stdout.flush()
            sys.stderr.flush()
            
            if sys.platform == 'win32':
                wait_for_key()
            else:
                print(f"\n{Fore.LIGHTWHITE_EX}Press Enter to exit...{Style.RESET_ALL}")
                sys.stdout.flush()
                try:
                    input()
                except (EOFError, KeyboardInterrupt):
                    pass
        
        # Final cleanup
        print(Style.RESET_ALL, end='')
        sys.stdout.flush()
        sys.exit(exit_code)
    except Exception:
        # Last resort: add delay before exit
        time.sleep(2)
        sys.exit(exit_code)

debug_print(f"{__app_name__} v{__version__} is running...")
debug_print(f"{__copyright__}")

if __name__ == "__main__": 
    try:
        # Initialize data storage
        if not initialize_data_files():
            handle_program_exit(1, "\nError: Failed to initialize data storage")
            
        # Load habits and streaks
        habits = load_habits()
        habit_streaks = load_habit_streaks()
        daily_logs = load_daily_logs()

        # Update streaks based on existing logs
        if daily_logs:
            update_streaks(daily_logs, habits, habit_streaks)
        
        # Handle command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] in ['-v-logs', '--view-logs']:
                display_logs(daily_logs, habit_streaks)
                handle_program_exit()
            elif sys.argv[1] in ['-c-logs', '--clear-logs']:
                if clear_tracking_data():
                    handle_program_exit(message="\nAll tracking data (logs, streaks, and plots) cleared successfully!")
                handle_program_exit(1, "\nError: Failed to clear tracking data")
            elif sys.argv[1] in ['-r', '--reset']:
                if reset_app_data():
                    handle_program_exit(message="\nProgram has been reset. All data and plots cleared. Run without arguments to start fresh.")
                handle_program_exit(1, "\nError: Failed to reset program data")
            elif sys.argv[1] in ['-i', '--info']:
                display_app_info()
                handle_program_exit()
            elif sys.argv[1] in ['--dev']:
                if make_files_writable():
                    handle_program_exit(message="\nCore files are now writable for development.")
                handle_program_exit(1, "\nError: Failed to make files writable")
            elif sys.argv[1] in ['--lock']:
                if make_files_readonly():
                    handle_program_exit(message="\nCore files are now read-only and protected.")
                handle_program_exit(1, "\nError: Failed to make files read-only")
            elif sys.argv[1] in ['-p', '--plot']:
                if not habits:
                    handle_program_exit(1, "\nNo habits found. Please set up habits first.")
                print(f"\n{Fore.LIGHTWHITE_EX}Available habits:{Style.RESET_ALL}")
                for i, habit in enumerate(habits, 1):
                    print(f"{Fore.LIGHTMAGENTA_EX}{i}. {Fore.LIGHTBLUE_EX}{habit}{Style.RESET_ALL}")
                try:
                    print(f"\n{Fore.LIGHTGREEN_EX}Enter the number of the habit to visualize: {Style.RESET_ALL}", end='')
                    choice = input().strip()
                    idx = int(choice) - 1
                    if 0 <= idx < len(habits):
                        plot_filename = visualize_habit_streak(daily_logs, habits[idx])
                        if plot_filename:
                            message = f"\nVisualization created successfully! Check your data/plots/ directory for {plot_filename}"
                            handle_program_exit(0, message)
                        else:
                            handle_program_exit(1)
                    else:
                        handle_program_exit(1, "\nInvalid habit number selected.")
                except (ValueError, IndexError):
                    handle_program_exit(1, "\nInvalid input. Please enter a valid number.")
            else:
                print(f"{Fore.LIGHTWHITE_EX}Invalid option. Use:{Style.RESET_ALL}")
                print(f"  {Fore.LIGHTMAGENTA_EX}-i{Style.RESET_ALL} or {Fore.LIGHTMAGENTA_EX}--info{Style.RESET_ALL} to display application information")
                print(f"  {Fore.LIGHTMAGENTA_EX}-v-logs{Style.RESET_ALL} or {Fore.LIGHTMAGENTA_EX}--view-logs{Style.RESET_ALL} to view logs")
                print(f"  {Fore.LIGHTMAGENTA_EX}-c-logs{Style.RESET_ALL} or {Fore.LIGHTMAGENTA_EX}--clear-logs{Style.RESET_ALL} to clear all logs")
                print(f"  {Fore.LIGHTMAGENTA_EX}-r{Style.RESET_ALL} or {Fore.LIGHTMAGENTA_EX}--reset{Style.RESET_ALL} to reset everything (habits, logs, and streaks)")
                print(f"  {Fore.LIGHTMAGENTA_EX}-p{Style.RESET_ALL} or {Fore.LIGHTMAGENTA_EX}--plot{Style.RESET_ALL} to visualize habit streaks")
                print(f"  {Fore.LIGHTMAGENTA_EX}--dev{Style.RESET_ALL} to make core files writable for development")
                print(f"  {Fore.LIGHTMAGENTA_EX}--lock{Style.RESET_ALL} to make core files read-only again")
                handle_program_exit(1)
        
        # Regular program flow - check if habits need to be set up
        if not habits:
            print(f"{Fore.LIGHTCYAN_EX}No habits found! Let's set up your daily habits first.{Style.RESET_ALL}")
            habits = setup_habits()
            if not habits:  # If setup was cancelled or failed
                handle_program_exit(1, "\nError: Failed to set up habits")
                
            if save_habits(habits):
                print(f"\n{Fore.LIGHTGREEN_EX}Habits saved successfully!{Style.RESET_ALL}")
            else:
                handle_program_exit(1, "\nError: Failed to save habits")

        # Normal daily check-in flow
        new_logs = log_habits(habits)
        if not new_logs:  # If logging was cancelled or failed
            handle_program_exit(1, "\nHabit logging cancelled or failed")
            
        daily_logs.extend(new_logs)
        update_streaks(daily_logs, habits, habit_streaks)
        
        if save_daily_logs(daily_logs, habit_streaks):
            print(f"\n{Fore.LIGHTGREEN_EX}Today's logs have been recorded successfully!{Style.RESET_ALL}")
            display_logs(daily_logs, habit_streaks)
        else:
            handle_program_exit(1, "\nError: Failed to save logs")
            
    except KeyboardInterrupt:
        handle_program_exit(message="\nProgram interrupted by user.")
    except Exception as e:
        handle_program_exit(1, f"\nUnexpected error: {str(e)}")