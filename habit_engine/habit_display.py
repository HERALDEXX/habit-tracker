from colorama import Fore, Style
import os

# Handles the basic display of habits and user interface elements.
# For advanced visualization features, see habit_visualization.py

def display_logs(logs, habit_streaks):
    """Display all logged entries with streaks."""
    if not logs:
        print(f"\n{Fore.LIGHTRED_EX}No logs found!{Style.RESET_ALL}")
        return
        
    print(f"\n{Fore.LIGHTWHITE_EX}All recorded logs:{Style.RESET_ALL}")
    try:
        # Group logs by date
        dates = sorted(set(log[1] for log in logs if isinstance(log, (list, tuple)) and len(log) >= 2))
        for date in dates:
            print(f"\n{Fore.LIGHTBLACK_EX}Date: {date}{Style.RESET_ALL}")
            for log in logs:
                if isinstance(log, (list, tuple)) and len(log) >= 3 and log[1] == date:
                    habit, _, completed = log
                    status = f"{Fore.GREEN}✓{Style.RESET_ALL}" if completed else f"{Fore.RED}✗{Style.RESET_ALL}"
                    streak = habit_streaks.get(habit, 0) if isinstance(habit_streaks, dict) else 0
                    streak_display = f"{Fore.YELLOW}🔥 {streak}{Style.RESET_ALL}" if streak > 0 else ""
                    print(f"  {Fore.LIGHTBLUE_EX}{habit}{Style.RESET_ALL}: {status} {streak_display}")
    except Exception as e:
        print(f"\n{Fore.LIGHTRED_EX}Error displaying logs: {e}{Style.RESET_ALL}")

def display_app_info():
    """Display detailed information about the application."""
    from habit_engine import (
        __app_name__, __version__, __author__, __description__,
        __copyright__, __license__, __website__, __release_date__,
        __gui_features__, __cli_features__, __credits__
    )
    
    print("\n" + "="*50)
    print(f"{Fore.LIGHTWHITE_EX}{__app_name__} v{__version__}{Style.RESET_ALL}")
    print("="*50)
    
    print(f"\n{Fore.LIGHTWHITE_EX}Description:{Style.RESET_ALL}")
    print(f"  {Fore.LIGHTCYAN_EX}{__description__}{Style.RESET_ALL}")
    
    print(f"\n{Fore.LIGHTWHITE_EX}Author & Copyright:{Style.RESET_ALL}")
    print(f"  {Fore.LIGHTCYAN_EX}{__author__}{Style.RESET_ALL}")
    print(f"  {Fore.LIGHTCYAN_EX}{__copyright__}{Style.RESET_ALL}")
    
    print(f"\n{Fore.LIGHTWHITE_EX}Release Information:{Style.RESET_ALL}")
    print(f"  {Fore.LIGHTCYAN_EX}Version: {__version__}{Style.RESET_ALL}")
    print(f"  {Fore.LIGHTCYAN_EX}Release Date: {__release_date__}{Style.RESET_ALL}")
    print(f"  {Fore.LIGHTCYAN_EX}License: {__license__}{Style.RESET_ALL}")
    print(f"  {Fore.LIGHTCYAN_EX}Website: {__website__}{Style.RESET_ALL}")
    
    print(f"\n{Fore.LIGHTWHITE_EX}Features:{Style.RESET_ALL}")
    print(f"\n  {Fore.LIGHTWHITE_EX}GUI Features:{Style.RESET_ALL}")
    for feature in __gui_features__:
        print(f"    {Fore.LIGHTCYAN_EX}• {feature}{Style.RESET_ALL}")
        
    print(f"\n  {Fore.LIGHTWHITE_EX}CLI Features:{Style.RESET_ALL}")
    for feature in __cli_features__:
        print(f"    {Fore.LIGHTCYAN_EX}• {feature}{Style.RESET_ALL}")
    
    print(f"\n{Fore.LIGHTWHITE_EX}Credits:{Style.RESET_ALL}")
    for credit in __credits__:
        print(f"  {Fore.LIGHTCYAN_EX}• {credit}{Style.RESET_ALL}")
    
    print("\n" + "="*50)

def display_license():
    """Display the MIT license text with PyInstaller compatibility"""
    try:
        # First try reading from file system (development mode)
        license_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'LICENSE')
        if os.path.exists(license_path):
            with open(license_path, 'r', encoding='utf-8') as file:
                license_text = file.read()
        else:
            # Fallback to embedded license text for compiled version
            from habit_engine.__init__ import __license_text__
            license_text = __license_text__

        print("\n" + "="*50)
        print(f"{Fore.LIGHTWHITE_EX}LICENSE{Style.RESET_ALL}")
        print("="*50 + "\n")
        print(f"{Fore.LIGHTCYAN_EX}{license_text}{Style.RESET_ALL}")
        print("="*50)
        return True
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error displaying license: {e}{Style.RESET_ALL}")
        return False