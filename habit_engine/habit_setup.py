# Handles the initial setup and configuration for the Habit Tracker application.

def setup_habits():
    """Prompts user to input their daily habits (2-10 habits)."""
    print("\n=== Setup Your Daily Habits ===")
    
    try:
        # Get number of habits to track
        while True:
            try:
                num_habits = int(input("\nHow many habits would you like to track? (2-10): ").strip())
                if 2 <= num_habits <= 10:
                    break
                print("Please enter a number between 2 and 10.")
            except ValueError:
                print("Please enter a valid number.")
            except KeyboardInterrupt:
                print("\nSetup cancelled.")
                return []
        
        print(f"\nPlease input your {num_habits} daily habits:")
        print("(Press Ctrl+C to cancel setup)")
        new_habits = []
        
        for i in range(num_habits):
            while True:
                try:
                    habit = input(f"Habit #{i+1}: ").strip()
                    if not habit:
                        print("Habit cannot be empty. Please enter a valid habit.")
                        continue
                        
                    if habit in new_habits:
                        print("You've already added this habit. Please enter a different one.")
                        continue
                        
                    # Basic validation of habit name
                    if len(habit) > 50:
                        print("Habit name too long. Please keep it under 50 characters.")
                        continue
                        
                    new_habits.append(habit)
                    break
                except KeyboardInterrupt:
                    print("\nSetup cancelled.")
                    return []
                    
        if new_habits:
            print("\nHabits configured successfully!")
            print("Your habits:")
            for i, habit in enumerate(new_habits, 1):
                print(f"{i}. {habit}")
                
        return new_habits
        
    except Exception as e:
        print(f"\nUnexpected error during setup: {str(e)}")
        return []