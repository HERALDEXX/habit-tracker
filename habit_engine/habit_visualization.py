# Handles advanced data visualization features using matplotlib.
# This module is separate from habit_display.py to:
# 1. Keep matplotlib dependency isolated
# 2. Maintain separation of concerns
# 3. Allow for future expansion of visualization features

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for better compatibility
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from datetime import datetime, timedelta
import os
import time
import sys
import warnings
from colorama import Fore, Style
from matplotlib.dates import DateFormatter, DayLocator
import threading
from collections import OrderedDict
from matplotlib.patches import Rectangle

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
    """Create a visualization of habit completion over time."""
    try:
        # Start loading animation
        loading_thread = threading.Thread(target=lambda: loading_animation())
        loading_thread.daemon = True
        loading_thread.start()
        warnings.filterwarnings('ignore')

        # Filter and prepare data
        habit_logs = [(log[1], log[2]) for log in logs if log[0] == habit_name]
        
        if not habit_logs:
            print(f"\n{Fore.LIGHTRED_EX}No data found for habit: {Fore.LIGHTBLUE_EX}{habit_name}{Style.RESET_ALL}")
            return None
            
        # Group logs by date
        habit_logs_dict = OrderedDict()
        for date, completed in sorted(habit_logs, key=lambda x: datetime.strptime(x[0], '%Y-%m-%d')):
            habit_logs_dict[date] = completed
        
        # Extract dates and completion status
        all_dates = [datetime.strptime(date, '%Y-%m-%d') for date in habit_logs_dict.keys()]
        all_completions = [1.0 if completed else 0.0 for completed in habit_logs_dict.values()]
        
        if not all_dates:
            return None

        # Create figure with adjusted size
        plt.style.use('default')
        fig = plt.figure(figsize=(10, 7), facecolor='white')
        plot_ax = plt.axes([0.12, 0.2, 0.76, 0.7])

        # Set window parameters
        window_size = timedelta(days=14)
        current_start = all_dates[0]
        visualization_done = False

        def update_plot(start_date, force_draw=False):
            """Update the plot with the specified date range."""
            plot_ax.clear()
            
            # Calculate end date
            end_date = start_date + window_size
            
            # Filter visible data
            visible_indices = [i for i, date in enumerate(all_dates) 
                             if start_date <= date <= end_date]
            visible_dates = [all_dates[i] for i in visible_indices]
            visible_completions = [all_completions[i] for i in visible_indices]
            
            if visible_dates:
                # Plot data points
                plot_ax.plot(visible_dates, visible_completions, 'bo-', 
                           label='Status', markerfacecolor='white',
                           markersize=12, linewidth=2)
                
                # Y-axis configuration
                plot_ax.set_yticks([0.0, 1.0])
                plot_ax.set_yticklabels(['✗ Not Done', '✓ Done'])
                plot_ax.set_ylim(-0.1, 1.1)
                
                # X-axis configuration
                plot_ax.xaxis.set_major_locator(DayLocator(interval=1))
                plot_ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
                plot_ax.set_xlim(start_date - timedelta(hours=12), 
                               end_date + timedelta(hours=12))
                
                # Grid styling
                plot_ax.grid(True, linestyle='--', alpha=0.3)
                plot_ax.set_axisbelow(True)
                
                # Rotate date labels
                plt.setp(plot_ax.xaxis.get_majorticklabels(), 
                        rotation=45, ha='right')
                
                # Title with date range
                plot_ax.set_title(f'Daily Habit Tracking: {habit_name}\n'
                                f'({start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")})',
                                pad=20, fontsize=12, fontweight='bold')
                
                # Update button states
                can_go_back = start_date > all_dates[0]
                can_go_forward = end_date < all_dates[-1]
                prev_button['state'] = 'normal' if can_go_back else 'disabled'
                next_button['state'] = 'normal' if can_go_forward else 'disabled'
                
                # Update button colors based on state
                prev_button['bg'] = '#2196F3' if can_go_back else '#CCCCCC'
                next_button['bg'] = '#2196F3' if can_go_forward else '#CCCCCC'
                
                # Adjust layout and draw if needed
                plt.tight_layout()
                if force_draw:
                    canvas.draw()

        def on_prev():
            nonlocal current_start
            if current_start > all_dates[0]:
                current_start = max(current_start - window_size, all_dates[0])
                update_plot(current_start, force_draw=True)

        def on_next():
            nonlocal current_start
            potential_end = current_start + window_size
            if potential_end < all_dates[-1]:
                current_start = current_start + window_size
                update_plot(current_start, force_draw=True)
                
        def on_window_close():
            """Handle window closing."""
            nonlocal visualization_done
            visualization_done = True
            root.quit()
            root.destroy()

        # Create Tkinter window and embed plot
        root = tk.Tk()
        root.title(f"Habit Tracking: {habit_name}")
        root.protocol("WM_DELETE_WINDOW", on_window_close)  # Handle window close button
        
        # Center window on screen
        window_width = 800
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        
        # Create navigation frame
        nav_frame = tk.Frame(root)
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        # Create custom navigation buttons with enhanced styling
        button_style = {
            'width': 15,
            'height': 1,
            'font': ('Arial', 10, 'bold'),
            'fg': 'white',
            'activebackground': '#1976D2',
            'activeforeground': 'white',
            'relief': tk.RAISED,
            'padx': 10
        }
        
        prev_button = tk.Button(nav_frame, text="◀ Previous", command=on_prev, **button_style)
        next_button = tk.Button(nav_frame, text="Next ▶", command=on_next, **button_style)
        
        # Pack buttons with spacing
        prev_button.pack(side=tk.LEFT, padx=5)
        next_button.pack(side=tk.RIGHT, padx=5)
        
        # Pack canvas
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        # Save plot before showing
        from habit_engine.habit_io import PLOTS_DIR
        os.makedirs(PLOTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = habit_name.lower().replace(" ", "_")
        plot_filename = f'{base_filename}_{timestamp}.png'
        plot_path = os.path.join(PLOTS_DIR, plot_filename)
        plt.savefig(plot_path, facecolor='white', bbox_inches='tight', dpi=300)

        # Initial plot update
        update_plot(current_start, force_draw=True)
        
        # Start Tkinter event loop
        root.mainloop()
        
        # Clear loading message and return filename
        sys.stdout.write('\r' + ' ' * 50 + '\r')
        sys.stdout.flush()
        
        if visualization_done:
            print(f"\n{Fore.LIGHTGREEN_EX}Visualization saved as: {plot_filename}{Style.RESET_ALL}")
            return plot_filename
        return None
            
    except Exception as e:
        print(f"\n{Fore.LIGHTRED_EX}Error creating visualization: {e}{Style.RESET_ALL}")
        return None
    finally:
        # Ensure we always clean up
        sys.stdout.write('\r' + ' ' * 50 + '\r')
        sys.stdout.flush()
        warnings.resetwarnings()