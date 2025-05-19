# Handles the basic display of habits and user interface elements.
# For advanced visualization features, see habit_visualization.py

def display_logs(logs, habit_streaks):
    """Display all logged entries with streaks."""
    if not logs:
        print("\nNo logs found!")
        return
        
    print("\nAll recorded logs:")
    try:
        # Group logs by date
        dates = sorted(set(log[1] for log in logs if isinstance(log, (list, tuple)) and len(log) >= 2))
        for date in dates:
            print(f"\nDate: {date}")
            for log in logs:
                if isinstance(log, (list, tuple)) and len(log) >= 3 and log[1] == date:
                    habit, _, completed = log
                    status = "✓" if completed else "✗"
                    streak = habit_streaks.get(habit, 0) if isinstance(habit_streaks, dict) else 0
                    streak_display = f"🔥 {streak}" if streak > 0 else ""
                    print(f"  {habit}: {status} {streak_display}")
    except Exception as e:
        print(f"\nError displaying logs: {e}")

def display_app_info():
    """Display detailed information about the application."""
    from habit_engine import (
        __app_name__, __version__, __author__, __description__,
        __copyright__, __license__, __website__, __release_date__,
        __features__, __credits__
    )
    
    print("\n" + "="*50)
    print(f"{__app_name__} v{__version__}")
    print("="*50)
    
    print("\nDescription:")
    print(f"  {__description__}")
    
    print("\nAuthor & Copyright:")
    print(f"  {__author__}")
    print(f"  {__copyright__}")
    
    print("\nRelease Information:")
    print(f"  Version: {__version__}")
    print(f"  Release Date: {__release_date__}")
    print(f"  License: {__license__}")
    print(f"  Website: {__website__}")
    
    print("\nFeatures:")
    for feature in __features__:
        print(f"  • {feature}")
    
    print("\nCredits:")
    for credit in __credits__:
        print(f"  • {credit}")
    
    print("\n" + "="*50)