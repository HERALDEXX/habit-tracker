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
import logging

# Suppress findfont warnings from matplotlib.font_manager
# This sets the logging level for this specific component to ERROR,
# meaning only messages of level ERROR or higher will be shown.
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

# List of fonts that typically support emojis, in order of preference
# Matplotlib will try to find and use the first available font from this list.
EMOJI_FONTS = [
    'Segoe UI Emoji',    # Windows
    'Apple Color Emoji',  # macOS
    'Noto Color Emoji',   # Linux/Cross-platform (might need installation)
    'DejaVu Sans',        # Fallback (but won't show emoji)
    'sans-serif'          # Generic fallback
]

# Add thread lock for matplotlib operations
plt_lock = threading.Lock()

# Ignore matplotlib warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

# --- Date range filtering logic ---
def _filter_logs_by_date_range(logs, date_range_str):
    """Filters logs based on the specified date range string."""
    filtered = []
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) # Normalize today to start of day

    start_date_filter = None
    if date_range_str == "Last 7 Days":
        start_date_filter = today - timedelta(days=6) # Includes today and previous 6 days
    elif date_range_str == "Last 30 Days":
        start_date_filter = today - timedelta(days=29) # Includes today and previous 29 days

    for log in logs:
        # Ensure log has correct structure and date is valid
        if not (isinstance(log, list) and len(log) >= 2 and isinstance(log[1], str)):
            continue
        try:
            log_date = datetime.strptime(log[1], '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
            if start_date_filter:
                if log_date >= start_date_filter:
                    filtered.append(log)
            else: # "All Time" or no filter specified
                filtered.append(log)
        except ValueError:
            # Skip logs with malformed dates
            print(f"{Fore.YELLOW}Warning: Skipping log with invalid date format: {log}{Style.RESET_ALL}")
            continue
    return filtered
# --- End date range filtering logic ---

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

def visualize_habit_streak(logs, habit_name, chart_style="Line Plot", show_streak_annotations=True, date_range="All Time"):
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
            
            # Filter logs for the specific habit
            habit_logs_for_name = [log for log in logs if log[0] == habit_name]
            if not habit_logs_for_name:
                return None

            # Apply date range filtering from settings
            filtered_habit_logs = _filter_logs_by_date_range(habit_logs_for_name, date_range)
            
            # Sort filtered logs by date
            filtered_habit_logs = sorted(filtered_habit_logs, key=lambda x: x[1])

            if not filtered_habit_logs:
                # If no logs in the selected range, create a blank chart for the range
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                if date_range == "Last 7 Days":
                    start_date_for_display = today - timedelta(days=6)
                elif date_range == "Last 30 Days":
                    start_date_for_display = today - timedelta(days=29)
                else: # "All Time" or default, just show today if no data
                    start_date_for_display = today

                date_range_list = []
                current_display_date = start_date_for_display
                # Generate dates until today or the defined range end
                while current_display_date <= today:
                    if date_range == "Last 7 Days" and (today - current_display_date).days > 6:
                        break
                    if date_range == "Last 30 Days" and (today - current_display_date).days > 29:
                        break
                    date_range_list.append(current_display_date.strftime('%Y-%m-%d'))
                    current_display_date += timedelta(days=1)

                if not date_range_list: # Ensure at least today is shown if no data
                    date_range_list = [today.strftime('%Y-%m-%d')]

                date_range_str = date_range_list
                completion_values = [0] * len(date_range_str) # All zeros if no data
            else:
                # Determine the full date range for the x-axis based on filtered data
                all_plot_dates = sorted(set(log[1] for log in filtered_habit_logs))
                
                # Determine the start and end date for the plot's X-axis
                plot_start_date = datetime.strptime(all_plot_dates[0], '%Y-%m-%d')
                plot_end_date = datetime.strptime(all_plot_dates[-1], '%Y-%m-%d')
                
                # Ensure the plot extends to today if the range selected is for last N days
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                if date_range in ["Last 7 Days", "Last 30 Days"]:
                    plot_end_date = max(plot_end_date, today)
                
                # Generate all dates within the determined plot range
                date_range_str = [(plot_start_date + timedelta(days=x)).strftime('%Y-%m-%d')
                                 for x in range((plot_end_date - plot_start_date).days + 1)]
                
                # Create a map for quick lookup of completion status
                completion_map = {log[1]: log[2] for log in filtered_habit_logs}
                
                # Populate completion_values for the full date_range_str
                completion_values = []
                for date in date_range_str:
                    completion_values.append(1 if completion_map.get(date) else 0) # 1 for completed, 0 for missed/no entry
                
            # Create plot
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Use numerical indices for plotting, and set labels separately for both types
            x_indices = range(len(date_range_str))

            if chart_style == "Line Plot":
                ax.plot(x_indices, completion_values, color='green',
                           marker='o', linestyle='-', linewidth=2,
                           markersize=8, label='Completed')
                # Set x-axis ticks for line plot (can be sparse for long ranges)
                tick_positions = list(range(0, len(date_range_str), max(1, len(date_range_str)//10)))
                ax.set_xticks(tick_positions)
                ax.set_xticklabels([date_range_str[i] for i in tick_positions], rotation=45, ha="right")
            elif chart_style == "Bar Chart":
                ax.bar(x_indices, completion_values, color='green', width=0.6, label='Completed')
                # Set x-axis ticks for bar chart (usually one tick per bar)
                ax.set_xticks(x_indices)
                ax.set_xticklabels(date_range_str, rotation=45, ha="right")
                # Adjust x-axis limits slightly for bar charts for better visual
                ax.set_xlim(-0.5, len(date_range_str) - 0.5)

            # Customize plot
            ax.set_title(f'Habit Tracking: {habit_name}', pad=20, size=14)
            ax.set_xlabel('Date', size=12)
            ax.set_ylabel('Completion (0=Missed, 1=Completed)', size=12)
            
            # Set y-axis ticks
            ax.set_yticks([0, 1])
            ax.set_yticklabels(['Missed', 'Completed'])
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Add streak annotations if enabled
            if show_streak_annotations and filtered_habit_logs:
                # Calculate daily streaks for annotations based on the plotted data
                current_streak = 0
                for i, date_str in enumerate(date_range_str):
                    is_completed = (completion_values[i] == 1) # Directly use completion_values
                    if is_completed:
                        current_streak += 1
                    else:
                        current_streak = 0 # Streak breaks on a miss or missing entry

                    if current_streak > 0: # Only annotate non-zero streaks
                        # Get the y-position for the annotation
                        y_pos = completion_values[i]
                        
                        # Adjust y_offset based on chart type for better visual placement
                        y_offset = 0.05 if chart_style == "Bar Chart" else 0.08

                        ax.text(
                            i, # x-position (index in date_range_str)
                            y_pos + y_offset, # y-position above the point/bar
                            f"🔥{current_streak}",
                            ha='center', # Horizontal alignment: center
                            va='bottom', # Vertical alignment: bottom of text is at y_pos + y_offset
                            color='orange',
                            fontweight='bold',
                            fontsize=15,
                            fontfamily=EMOJI_FONTS
                        )

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