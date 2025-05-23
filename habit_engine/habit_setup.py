from colorama import Fore, Style

# Handles the initial setup and configuration for the Habit Tracker application.

def setup_habits():
    """Prompts user to input their daily habits (2-10 habits)."""
    print(f"\n{Fore.LIGHTWHITE_EX}=== Setup Your Daily Habits ==={Style.RESET_ALL}")
    
    try:
        # Get number of habits to track
        while True:
            try:
                print(f"\n{Fore.LIGHTGREEN_EX}How many habits would you like to track? (2-10): {Style.RESET_ALL}", end='')
                num_habits = int(input().strip())
                if 2 <= num_habits <= 10:
                    break
                print(f"{Fore.LIGHTRED_EX}Please enter a number between 2 and 10.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.LIGHTRED_EX}Please enter a valid number.{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.LIGHTRED_EX}Setup cancelled.{Style.RESET_ALL}")
                return []
        
        print(f"\n{Fore.LIGHTCYAN_EX}Please input your {num_habits} daily habits:{Style.RESET_ALL}")
        print(f"{Fore.LIGHTCYAN_EX}(Press Ctrl+C to cancel setup){Style.RESET_ALL}")
        new_habits = []
        
        for i in range(num_habits):
            while True:
                try:
                    print(f"{Fore.LIGHTGREEN_EX}Habit #{i+1}: {Style.RESET_ALL}", end='')
                    habit = input().strip()
                    if not habit:
                        print(f"{Fore.LIGHTRED_EX}Habit cannot be empty. Please enter a valid habit.{Style.RESET_ALL}")
                        continue
                        
                    if habit in new_habits:
                        print(f"{Fore.LIGHTRED_EX}You've already added this habit. Please enter a different one.{Style.RESET_ALL}")
                        continue
                        
                    # Basic validation of habit name
                    if len(habit) > 50:
                        print(f"{Fore.LIGHTRED_EX}Habit name too long. Please keep it under 50 characters.{Style.RESET_ALL}")
                        continue
                        
                    new_habits.append(habit)
                    break
                except KeyboardInterrupt:
                    print(f"\n{Fore.LIGHTRED_EX}Setup cancelled.{Style.RESET_ALL}")
                    return []
                    
        if new_habits:
            print(f"\n{Fore.LIGHTGREEN_EX}Habits configured successfully!{Style.RESET_ALL}")
            print(f"{Fore.LIGHTWHITE_EX}Your habits:{Style.RESET_ALL}")
            for i, habit in enumerate(new_habits, 1):
                print(f"{Fore.LIGHTBLUE_EX}{i}. {habit}{Style.RESET_ALL}")
                
        return new_habits
        
    except Exception as e:
        print(f"\n{Fore.LIGHTRED_EX}Unexpected error during setup: {str(e)}{Style.RESET_ALL}")
        return []