# Handles advanced data visualization features using matplotlib.
# This module is separate from habit_display.py to:
# 1. Keep matplotlib dependency isolated
# 2. Maintain separation of concerns
# 3. Allow for future expansion of visualization features

from habit_engine.habit_io import PLOTS_DIR
import matplotlib
matplotlib.use('Agg')  # Force Agg backend for thread safety
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import threading
import os
import warnings
from colorama import Fore, Style
import sys
from collections import OrderedDict
import time

# Add thread lock for matplotlib operations
plt_lock = threading.Lock()

# Ignore matplotlib warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

def loading_animation():
    """Display a simple loading animation."""
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    while True:
        try:
            sys.stdout.write(f'\r{Fore.LIGHTCYAN_EX}Generating visualization... {chars[i]}{Style.RESET_ALL}')
            sys.stdout.flush()
            time.sleep(0.1)
            i = (i + 1) % len(chars)
        except:
            break

def visualize_habit_streak(logs, habit_name):
    """Create a visualization of the habit streak."""
    try:
        # Configure matplotlib backend with error handling
        try:
            import matplotlib
            matplotlib.use('Agg')  # Force Agg backend for thread safety
        except ImportError as e:
            print(f"Error loading matplotlib: {str(e)}")
            return None
        except Exception as e:
            print(f"Error configuring matplotlib backend: {str(e)}")
            return None

        # Use thread lock for matplotlib operations
        with plt_lock:
            plt.close('all')  # Clean up any existing plots
            
            # Filter logs for this habit
            habit_logs = [log for log in logs if log[0] == habit_name]
            if not habit_logs:
                return None
                
            # Get date range
            dates = sorted(set(log[1] for log in habit_logs))
            if not dates:
                return None
                
            start_date = datetime.strptime(dates[0], '%Y-%m-%d')
            end_date = datetime.strptime(dates[-1], '%Y-%m-%d')
            date_range = [(start_date + timedelta(days=x)).strftime('%Y-%m-%d')
                         for x in range((end_date - start_date).days + 1)]
            
            # Create completion data
            completion_data = []
            for date in date_range:
                log = next((log for log in habit_logs if log[1] == date), None)
                completion_data.append(1 if log and log[2] else 0)
                
            # Create plot
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(range(len(date_range)), completion_data, 
                   marker='o', linestyle='-', linewidth=2, 
                   markersize=8, label='Completed')
            
            # Customize plot
            ax.set_title(f'Habit Tracking: {habit_name}', pad=20, size=14)
            ax.set_xlabel('Date', size=12)
            ax.set_ylabel('Completion (0=Missed, 1=Completed)', size=12)
            
            # Set x-axis ticks
            tick_positions = list(range(0, len(date_range), max(1, len(date_range)//10)))
            ax.set_xticks(tick_positions)
            ax.set_xticklabels([date_range[i] for i in tick_positions], rotation=45)
            
            # Set y-axis ticks
            ax.set_yticks([0, 1])
            ax.set_yticklabels(['Missed', 'Completed'])
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save plot
            plots_dir = PLOTS_DIR
            os.makedirs(plots_dir, exist_ok=True)
            
            filename = f'habit_streak_{habit_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            filepath = os.path.join(plots_dir, filename)
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()  # Clean up
            
            return filepath
            
    except Exception as e:
        print(f"Error creating visualization: {str(e)}")
        return None