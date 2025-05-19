# Handles advanced data visualization features using matplotlib.
# This module is separate from habit_display.py to:
# 1. Keep matplotlib dependency isolated
# 2. Maintain separation of concerns
# 3. Allow for future expansion of visualization features

import matplotlib.pyplot as plt
from datetime import datetime
import os

def visualize_habit_streak(logs, habit_name):
    """Create a visualization of habit completion over time."""
    try:
        # Filter logs for the specified habit
        habit_logs = [(log[1], log[2]) for log in logs if log[0] == habit_name]
        
        if not habit_logs:
            print(f"\nNo data found for habit: {habit_name}")
            return False
            
        # Sort logs by date
        habit_logs.sort(key=lambda x: datetime.strptime(x[0], '%Y-%m-%d'))
        
        # Extract dates and completion status
        dates = [datetime.strptime(date, '%Y-%m-%d') for date, _ in habit_logs]
        completions = [1 if completed else 0 for _, completed in habit_logs]
        
        # Create the plot
        plt.figure(figsize=(12, 6))
        plt.plot(dates, completions, 'bo-', label='Completed')
        
        # Customize the plot
        plt.title(f'Habit Completion Timeline: {habit_name}')
        plt.xlabel('Date')
        plt.ylabel('Completion Status')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Rotate date labels for better readability
        plt.xticks(rotation=45)
        
        # Add legend
        plt.legend()
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Get plots directory path from habit_io
        from habit_engine.habit_io import PLOTS_DIR
        os.makedirs(PLOTS_DIR, exist_ok=True)
        
        # Generate timestamp-based filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = habit_name.lower().replace(" ", "_")
        plot_filename = f'{base_filename}_{timestamp}.png'
        plot_path = os.path.join(PLOTS_DIR, plot_filename)
        
        # Save the plot
        plt.savefig(plot_path)
        plt.close()
        
        print(f"\nVisualization saved as: {plot_filename}")
        return True
        
    except Exception as e:
        print(f"\nError creating visualization: {e}")
        return False