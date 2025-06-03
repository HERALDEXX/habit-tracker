# Contains the main entry point for the Habit Tracker application.
import sys, os
from colorama import init, Fore, Style
import time
import platform

# Cross-platform console input handling
if platform.system() == "Windows":
    import msvcrt
else:
    import sys
    import tty
    import termios

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.encode()

# Import all necessary functions from modules
from habit_engine.__init__ import __version__, __app_name__, __copyright__
from habit_engine.habit_setup import setup_habits
from habit_engine.habit_io import (
    load_settings,
    load_habits,
    save_habits,
    load_habit_streaks,
    load_daily_logs,
    save_daily_logs,
    initialize_data_files,
    DATA_DIR,
    PLOTS_DIR,
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
    display_app_info,
    display_license
)

# Only import visualization when needed
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
    else:
        print(f"\n{Fore.LIGHTWHITE_EX}Press Enter to exit...{Style.RESET_ALL}")
        sys.stdout.flush()
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass

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

def run_gui_mode():
    """Run the application in GUI mode."""
    try:
        # Initialize data storage
        if not initialize_data_files():
            handle_program_exit(1, "\nError: Failed to initialize data storage")
            
        # Only import GUI when needed
        from habit_engine.gui import HabitTrackerGUI
            
        # Create and run GUI
        app = HabitTrackerGUI(
            load_habits_fn=load_habits,
            save_habits_fn=save_habits,
            load_logs_fn=load_daily_logs,
            save_logs_fn=save_daily_logs,
            update_streaks_fn=update_streaks,
            load_streaks_fn=load_habit_streaks,
            visualize_fn=visualize_habit_streak
        )
        app.run()
        
    except Exception as e:
        handle_program_exit(1, f"\nUnexpected error in GUI mode: {str(e)}")

def run_cli_mode():
    """Run the application in CLI mode."""
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
                    handle_program_exit(message="\nProgram has been reset. All data and plots cleared.\nSettings have been restored to default.\nRun without arguments to start fresh.")
                handle_program_exit(1, "\nError: Failed to reset program data")
            elif sys.argv[1] in ['-i', '--info']:
                display_app_info()
                handle_program_exit()
            elif sys.argv[1] in ['-l', '--license']:
                display_license()
                handle_program_exit()
            elif sys.argv[1] in ['-h', '--help']:
                display_help()
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
                        # Check if there are any logs for this habit
                        habit_logs = [log for log in daily_logs if log[0] == habits[idx]]
                        if not habit_logs:
                            handle_program_exit(1, "\nNo tracking data found for this habit yet.")
                        
                        print(f"\n{Fore.LIGHTCYAN_EX}Generating visualization...{Style.RESET_ALL}")
                        plot_filename = visualize_habit_streak(daily_logs, habits[idx])
                        if plot_filename:
                            path = os.path.abspath(PLOTS_DIR)
                            message = f"\nVisualization created successfully! Plot for '{habits[idx]}' is saved in {path}."
                            handle_program_exit(0, message)
                        else:
                            handle_program_exit(1, "\nFailed to create visualization.")
                    else:
                        handle_program_exit(1, "\nInvalid habit number selected.")
                except (ValueError, IndexError):
                    handle_program_exit(1, "\nInvalid input. Please enter a valid number.")
                except KeyboardInterrupt:
                    handle_program_exit(message="\nVisualization cancelled by user.")
                except Exception as e:
                    handle_program_exit(1, f"\nError creating visualization: {str(e)}")
            elif sys.argv[1] in ['--cli']:
                pass  # Continue with CLI mode
            elif sys.argv[1] in ['--gui']:
                run_gui_mode()
                return
            else:
                print(f"{Fore.LIGHTWHITE_EX}Invalid option. Use {Fore.LIGHTMAGENTA_EX}-h{Style.RESET_ALL} or {Fore.LIGHTMAGENTA_EX}--help{Style.RESET_ALL} to see all available commands.")
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

def display_help():
    """Display detailed help information about the application and its commands."""
    print(f"\n{Fore.LIGHTCYAN_EX}==================================================")
    print(f"HERALDEXX HABIT TRACKER v{__version__} - Help")
    print(f"=================================================={Style.RESET_ALL}")
    print("\nUsage: python main.py [OPTIONS]")
    
    print(f"\n{Fore.LIGHTMAGENTA_EX}Mode Selection:{Style.RESET_ALL}")
    print("  --gui              Run in graphical user interface mode (default)")
    print("  --cli              Force command-line interface mode")
    
    print(f"\n{Fore.LIGHTMAGENTA_EX}Information Commands:{Style.RESET_ALL}")
    print("  -h, --help         Display this help message")
    print("  -i, --info         Display application information")
    print("  -l, --license      Display the MIT license")
    
    print(f"\n{Fore.LIGHTMAGENTA_EX}Data Management:{Style.RESET_ALL}")
    print("  -v-logs, --view-logs    View habit tracking logs")
    print("  -c-logs, --clear-logs   Clear all tracking logs")
    print("  -r, --reset            Reset everything (habits, logs, and streaks)")
    
    print(f"\n{Fore.LIGHTMAGENTA_EX}Visualization:{Style.RESET_ALL}")
    print("  -p, --plot         Generate and view habit streak visualizations")
    
    print(f"\n{Fore.LIGHTMAGENTA_EX}Development Options:{Style.RESET_ALL}")
    print("  --dev              Make core files writable for development")
    print("  --lock             Make core files read-only (default state)")
    
    print(f"\n{Fore.LIGHTMAGENTA_EX}Examples:{Style.RESET_ALL}")
    print("  python main.py                 # Start in GUI mode")
    print("  python main.py --cli           # Start in CLI mode")
    print("  python main.py -v-logs         # View tracking logs")
    print("  python main.py -p              # Generate visualizations")
    
    print(f"\n{Fore.LIGHTMAGENTA_EX}Notes:{Style.RESET_ALL}")
    print("  - For Windows executable, Data is stored in 'C:\\Users\\<username>\\.heraldexx-habit-tracker\\data'.")
    print("  - For Linux/MacOS executables, Data is stored in '~/.heraldexx-habit-tracker/data'")
    print("  - For source code, Data is stored in the 'data/' directory in the project root.")
    print("")
    print("  - Visualizations are saved in the 'plots/' subdirectory of the 'data/' directory.")
    print("  - Use GUI mode for the best interactive experience")
    print("  - CLI mode is ideal for automation and scripting")
    
    print(f"\n{Fore.LIGHTCYAN_EX}For more information, visit:")
    print(f"https://github.com/heraldexx/habit-tracker{Style.RESET_ALL}\n")

if __name__ == "__main__": 
    # Process "--cli" or "--gui" mode first
    cli_mode = False
    args_to_process = sys.argv[1:]  # Copy arguments list
    
    if "--cli" in args_to_process:
        cli_mode = True
        args_to_process.remove("--cli")
    elif "--gui" in args_to_process:
        args_to_process.remove("--gui")
        cli_mode = False
    else:
        # Default to GUI unless other CLI arguments are present
        cli_mode = len(args_to_process) > 0
    
    # Update sys.argv with remaining args for CLI mode
    sys.argv[1:] = args_to_process
    
    # Run in appropriate mode
    if cli_mode:
        run_cli_mode()
    else:
        run_gui_mode()