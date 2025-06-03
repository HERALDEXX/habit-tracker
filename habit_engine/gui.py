import tkinter as tk
from customtkinter import CTkToplevel, CTkLabel, CTkOptionMenu, CTkButton
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import os, sys, subprocess
from colorama import Fore, Style
import threading
import platform
from tkinter import PhotoImage
import matplotlib.pyplot as plt
from functools import wraps
from typing import Optional, Dict, Any
import time
from habit_engine.habit_visualization import visualize_habit_streak
from habit_engine.habit_io import DATA_DIR, load_settings, save_settings, get_asset_path, reset_app_data, clear_tracking_data, PLOTS_DIR

# Lazy imports
PIL = None  # Will be imported when needed
plt = None  # Will be imported when needed
darkdetect = None  # Will be imported when needed

# Store single customtkinter instance
_ctk_instance = None

class ResourceManager:
    """Manages resources like images and fonts to prevent memory leaks and improve performance"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self._images: Dict[str, Any] = {}
        self._fonts: Dict[str, Any] = {}
        self._callbacks: Dict[str, Any] = {}
        
    def cache_image(self, path: str) -> Any:
        """Cache and return an image, loading it only if not already cached"""
        if path not in self._images:
            global PIL
            if PIL is None:
                from PIL import Image, ImageTk
                PIL = (Image, ImageTk)
            # Use CTkImage instead of PhotoImage for better high DPI support
            image = PIL[0].open(path)
            ctk_image = init_customtkinter().CTkImage(
                light_image=image,
                dark_image=image,
                size=image.size
            )
            self._images[path] = ctk_image
        return self._images[path]
    
    def cache_font(self, name: str, size: int, weight: str = "normal") -> Any:
        """Cache and return a font, creating it only if not already cached"""
        key = f"{name}_{size}_{weight}"
        if key not in self._fonts:
            if _ctk_instance:
                self._fonts[key] = _ctk_instance.CTkFont(
                    family=name,
                    size=size,
                    weight=weight
                )
        return self._fonts[key]
    
    def debounce(self, wait_ms: int):
        """Decorator to debounce a function call"""
        def decorator(func):
            key = f"{func.__name__}_timer"
            
            @wraps(func)
            def debounced(*args, **kwargs):
                def call_func():
                    self._callbacks.pop(key, None)
                    func(*args, **kwargs)
                
                # Cancel previous timer if it exists
                if key in self._callbacks:
                    # Cancel the previous Tk‐after callback on the main window
                    args[0].window.after_cancel(self._callbacks[key])
            
                # Schedule the new callback on the main window’s event loop
                self._callbacks[key] = args[0].window.after(wait_ms, call_func)
            
            return debounced
        return decorator
    
    def clear(self):
        """Clear all cached resources"""
        self._images.clear()
        self._fonts.clear()
        self._callbacks.clear()

def init_customtkinter():
    """Lazy load customtkinter when needed"""
    global _ctk_instance, darkdetect
    if (_ctk_instance is None):
        try:
            import tkinter as tk
        except ImportError:
            import platform
            system = platform.system().lower()
            if system == 'linux':
                raise ImportError("tkinter not found! Install it with: sudo apt-get install python3-tk")
            elif system == 'darwin':  # macOS
                raise ImportError("tkinter not found! If using Homebrew Python, install it with: brew install python-tk")
            else:
                raise ImportError("tkinter not found! Please reinstall Python and make sure to select the tkinter option during installation")

        try:
            import customtkinter as ctk
            import darkdetect  # For system theme detection
        except ImportError as e:
            raise ImportError("Required packages missing. Run: pip install -r requirements.txt") from e
            
        # Force update the window to prevent widget sizing issues
        if (hasattr(tk, '_default_root') and tk._default_root):
            tk._default_root.update_idletasks()
            
        _ctk_instance = ctk
        
        # Set initial appearance mode based on system theme
        system_theme = darkdetect.theme().lower() if darkdetect.theme() else "light"
        _ctk_instance.set_appearance_mode(system_theme)
        
    return _ctk_instance

class MessageWindow:
    def __init__(self, master, title, message, duration=2000, **kwargs):
        self.ctk = init_customtkinter()
        toplevel_kwargs = {k: v for k, v in kwargs.items() if k != 'on_close'}
        self.window = self.ctk.CTkToplevel(master, **toplevel_kwargs)
        self.on_close = kwargs.get('on_close', None)
        self.window.overrideredirect(True)  # Remove title bar on all platforms
        self.window.transient(master) # Make window modal
        self.window.lift()  # Ensure window is visible, especially on macOS
        # self.window.grab_set()  # Capture user focus
        self.window.attributes('-topmost', True)  # Keep window on top
        self.window.title(title)
        
        # Add window protocol handling
        self.window.protocol("WM_DELETE_WINDOW", self.destroy)
        
        # Set size and position - centered on screen
        window_width = 300
        window_height = 100
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Calculate position to center on screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Position window and configure colors
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.configure(fg_color=("gray95", "#292929"))  # Light/Dark mode colors
        # self.window.grab_set()  # Make window modal
        try:
            if self.window.winfo_exists():
                self.window.focus_force()
        except tk.TclError as e:
            # print(f"DEBUG: Caught TclError during MessageWindow focus_force: {e}") # Optional: for debugging
            pass
        except Exception as e:
            # print(f"DEBUG: Caught unexpected error during MessageWindow focus_force: {e}") # Optional: for debugging
            pass

        # Message label with proper contrast
        label = self.ctk.CTkLabel(
            self.window, 
            text=message, 
            font=self.ctk.CTkFont(size=14),
            text_color=("gray10", "gray90"),  # Light/Dark mode text
            justify="center"
        )
        label.pack(pady=20)
        
        # Auto-close after duration
        if (duration > 0):
            self.window.after(duration, self.destroy)
    
    def destroy(self):
        """Properly destroy the message window"""
        if self.on_close:
            try:
                self.on_close()
            except:
                pass
        if (hasattr(self, 'window') and self.window and self.window.winfo_exists()):
            try:
                self.window.grab_release()
                self.window.destroy()
            except:
                pass

class ConfirmDialog:
    def __init__(self, master, title, message, **kwargs):
        self.ctk = init_customtkinter()
        self.window = self.ctk.CTkToplevel(master, **kwargs)
        
        # Remove window decorations including icon for all platforms
        platform_name = platform.system().lower()
        if platform_name == 'windows':
            try:
                self.set_window_icon(self.window)
                # Additional Windows-specific icon removal
                self.window.overrideredirect(True)  # Remove title bar completely
                self.window.attributes('-toolwindow', True)  # Use tool window style
            except: pass
        elif platform_name == 'darwin':  # macOS
            try:
                # Remove window proxy icon on macOS
                self.window.wm_iconphoto(False, tk.PhotoImage())
                self.window.createcommand('::tk::mac::ReopenApplication', lambda: None)
            except: pass
        else:  # Linux/Unix
            try:
                # Remove window icon on Linux/Unix
                self.window.wm_withdraw()
                self.window.wm_deiconify()
                self.window.attributes('-type', 'dialog')
                self.window.attributes('-toolwindow', True)
            except: pass
            
        self.window.title(title)
        self.result = None
        
        # Platform-specific window attributes
        platform_name = platform.system().lower()
        if platform_name == 'windows':
            # On Windows, we'll use toolwindow style
            try:
                self.window.attributes('-toolwindow', True)
            except:
                pass
        else:
            # On Unix-like systems (Linux/macOS)
            try:
                self.window.attributes('-type', 'dialog')
            except:
                pass
                
        self.window.attributes('-topmost', True)
        # self.window.transient(master)
        # self.window.grab_set()
        
        # Set size and position
        window_width = 300
        window_height = 150
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Message label
        label = self.ctk.CTkLabel(self.window, text=message, font=self.ctk.CTkFont(size=14))
        label.pack(pady=20)
        
        # Text input
        self.input = self.ctk.CTkEntry(self.window)
        self.input.pack(pady=10)
        
        # Buttons frame
        button_frame = self.ctk.CTkFrame(self.window)
        button_frame.pack(pady=10, fill="x")
        
        # OK and Cancel buttons
        ok_button = self.ctk.CTkButton(button_frame, text="OK", command=self.ok_click)
        ok_button.pack(side="left", padx=20, expand=True)
        
        cancel_button = self.ctk.CTkButton(button_frame, text="Cancel", command=self.cancel_click)
        cancel_button.pack(side="right", padx=20, expand=True)
        
        # Center the window
        self.window.update_idletasks()
        self.window.focus_set()
        
        # Set up event bindings
        self.window.bind("<Return>", lambda e: self.ok_click())
        self.window.bind("<Escape>", lambda e: self.cancel_click())
        self.input.focus_set()
        
        # Wait for window
        self.window.wait_window()
        
    def ok_click(self):
        self.result = self.input.get()
        self.window.destroy()
        
    def cancel_click(self):
        self.window.destroy()

class YesNoDialog:
    def __init__(self, master, title, message, yes_fg_color=None, yes_hover_color=None, no_fg_color=None, no_hover_color=None, **kwargs):
        self.ctk = init_customtkinter()
        self.window = self.ctk.CTkToplevel(master, **kwargs)
        self.window.overrideredirect(True)  # Remove title bar on all platforms
        self.window.lift()  # Ensure window is visible, especially on macOS
        self.window.focus_force()  # Ensure window is focused, especially on macOS
        self.window.transient(master)  # Make window modal
        self.window.grab_set()  # Capture user focus
        self.window.attributes('-topmost', True)  # Keep window on top
        frame = self.ctk.CTkFrame(self.window)
        frame.pack(padx=20, pady=20, fill="both", expand=True)
            
        self.window.title(title)
        self.result = False
                
        self.window.transient(master)
        self.window.grab_set()
        
        # Message label
        label = self.ctk.CTkLabel(frame, text=message, wraplength=400, justify="left", anchor="w", font=self.ctk.CTkFont(size=14))
        label.pack(fill="x", padx=20, pady=(10, 20))
        
        # Buttons frame
        button_frame = self.ctk.CTkFrame(frame)
        button_frame.pack(pady=(0, 10))
        
        # Yes and No buttons
        yes_button = self.ctk.CTkButton(button_frame, text="Yes", command=self.yes_click, width=100, height=36,
                                        fg_color=yes_fg_color or "darkgreen", hover_color=yes_hover_color or "green")
        yes_button.pack(side="left", padx=10)
        
        no_button = self.ctk.CTkButton(button_frame, text="No", command=self.no_click, width=100, height=36,
                                        fg_color=no_fg_color or "darkred", hover_color=no_hover_color or "red")
        no_button.pack(side="right", padx=10)
        
         # ————— Let CTk compute its natural size, then center the window —————
        self.window.update_idletasks()                         # 1) force layout pass
        window_width = 450
        window_height = self.window.winfo_height()             # 2) get computed height
        screen_width = self.window.winfo_screenwidth()         # 3) compute center X
        screen_height = self.window.winfo_screenheight()       # 4) compute center Y
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")  # 4) apply geometry

        # Center the window and set focus
        self.window.focus_set()
        
        # Set up event bindings
        self.window.bind("<Return>", lambda e: self.yes_click())
        self.window.bind("<Escape>", lambda e: self.no_click())
        
        # Wait for window
        self.window.wait_window()
        
    def yes_click(self):
        self.result = True
        self.window.destroy()
        
    def no_click(self):
        self.result = False
        self.window.destroy()

class HabitTrackerGUI:
    def __init__(self, load_habits_fn, save_habits_fn, load_logs_fn, save_logs_fn, 
                 update_streaks_fn, load_streaks_fn, visualize_fn):
        self.plot_windows = []
        self.clear_btn_tooltip = None
        self.clear_btn_tooltip_delay = None
        # Initialize resource manager
        self.resources = ResourceManager()
        
        # Store callback functions
        self._load_habits = load_habits_fn
        self._save_habits = save_habits_fn
        self._load_logs = load_logs_fn
        self._save_logs = save_logs_fn
        self._update_streaks = update_streaks_fn
        self._load_streaks = load_streaks_fn
        self._visualize = visualize_fn
        
        # Initialize customtkinter
        self.ctk = init_customtkinter()
        
        # Create main window
        self.window = self.ctk.CTk()
        self.set_window_icon(self.window)
        self.window.title("HERALDEXX HABIT TRACKER")

        self.settings = load_settings()

        self.daily_reminder_enabled = self.settings.get("daily_reminder_enabled", False)
        self.reminder_time = self.settings.get("reminder_time", "09:00")
        self._last_reminder_date = None # To ensure reminder only pops up once per day

        self.chart_style = self.settings.get("chart_style", "Line Plot")
        self.show_streak_annotations = self.settings.get("show_streak_annotations", True)
        self.chart_date_range = self.settings.get("chart_date_range", "Last 30 Days")

        self.autosave_interval = self.settings.get("autosave_interval", 30)
        self.autosave_map = {                                              
            "15 seconds": 15,                                              
            "30 seconds": 30,                                              
            "1 minute": 60,                                                
            "Off": 0                                                       
        }
        self.autosave_map_rev = {v: k for k, v in self.autosave_map.items()}

        # Apply appearance from settings
        self.current_appearance_mode = self.settings.get("appearance_mode", "System")
        self.ctk.set_appearance_mode(self.current_appearance_mode)

            
        # Configure main window grid
        self.window.grid_columnconfigure(1, weight=1)  # Make second column expandable
        self.window.grid_rowconfigure(0, weight=1)     # Make first row expandable
        
        # Widget recycling pools
        self._checkbox_pool = []
        self._label_pool = []
        self._button_pool = []
        self._frame_pool = []
        
        # Setup window metrics and platform specifics
        self._setup_platform_specifics()
        
        # Initialize UI state
        self.habits = []
        self.logs = []
        self.streaks = {}
        self.pending_changes = False
        self.last_save = datetime.now()
        self.settings_window = None
        
        # Create main layout frames with proper color handling
        self.sidebar = self.ctk.CTkFrame(
            self.window,
            fg_color=("gray85", "#2B2B2B"),
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.main_frame = self.ctk.CTkFrame(
            self.window,
            fg_color=("gray95", "#1E1E1E")
        )
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Setup UI components
        self.setup_sidebar()
        self.setup_main_frame()
        
        # Load initial data
        self._load_data()
        
        # Set up autosave
        self._setup_autosave()
        
        # Bind window close event
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)   

    def _create_tooltip(self, button, message):
        if hasattr(button, 'tooltip') and button.tooltip:
            button.tooltip.destroy()
        button.tooltip = self.ctk.CTkToplevel()
        # Remove window decorations including icon for all platforms
        platform_name = self.platform  # Assuming self.platform is set in __init__
        if platform_name == 'windows':
            try:
                button.tooltip.wm_iconbitmap("")
            except:
                pass
        elif platform_name == 'darwin':  # macOS
            try:
                button.tooltip.wm_iconphoto(False, tk.PhotoImage())
            except:
                pass
        else:  # Linux/Unix
            try:
                button.tooltip.wm_withdraw()
                button.tooltip.wm_deiconify()
                button.tooltip.attributes('-type', 'dialog')
            except:
                pass
        button.tooltip.overrideredirect(True)
        button.tooltip.attributes("-topmost", True)
        # Create tooltip frame
        tooltip_height = 32 if message == "No Tracking History to Clear!" else 28
        tooltip_frame = self.ctk.CTkFrame(
            button.tooltip,
            fg_color=("gray75", "gray25"),
            corner_radius=6,
            width=150,
            height=tooltip_height
        )
        tooltip_frame.pack(expand=False, fill="both")
        tooltip_frame.pack_propagate(False)
        # Create tooltip label
        label = self.ctk.CTkLabel(
            tooltip_frame,
            text=message,
            font=self.ctk.CTkFont(size=12),
            text_color=("gray10", "gray90"),
            wraplength=140
        )
        label.place(relx=0.5, rely=0.5, anchor="center")
        # Position the tooltip
        button_x = button.winfo_rootx()
        button_y = button.winfo_rooty()
        button_width = button.winfo_width()
        button_height = button.winfo_height()
        x = button_x + button_width + 2
        y = button_y + (button_height // 2) - 14
        button.tooltip.geometry(f"+{x}+{y}")

    def _show_tooltip(self, event, button, message):
        if button.cget("state") == "disabled":
            if hasattr(button, 'tooltip_timer') and button.tooltip_timer:
                self.window.after_cancel(button.tooltip_timer)
            button.tooltip_timer = self.window.after(200, lambda: self._create_tooltip(button, message))

    def _hide_tooltip(self, event, button):
        if hasattr(button, 'tooltip_timer') and button.tooltip_timer:
            self.window.after_cancel(button.tooltip_timer)
            button.tooltip_timer = None
        if hasattr(button, 'tooltip') and button.tooltip:
            button.tooltip.destroy()
            button.tooltip = None

    @ResourceManager().debounce(300)   # 300 ms, on the Tk main thread
    def debounced_validate_habit_entry(self, event, index):
        self.validate_habit_entry(event, index)

    def remove_window_icon(self, window):
        """Remove the icon from a CTkToplevel window while keeping the title bar."""
        try:
            if platform.system() == "Windows":
                window.wm_attributes('-toolwindow', True)
            elif platform.system() == "Darwin":  # macOS
                window.transient(self.window)
            elif platform.system() == "Linux":
                window.wm_attributes('-type', 'dialog')
        except Exception as e:
            print(f"Error removing window icon: {e}")

    def set_window_icon(self, window):
        """Set the window icon for the title bar and taskbar/dock."""
        try:
            if platform.system() == "Windows":
                icon_path = get_asset_path('icon.ico')
                if os.path.exists(icon_path):
                    window.update_idletasks()
                    window.iconbitmap(icon_path)
            else:
                icon_path = get_asset_path('icon.png')
                if os.path.exists(icon_path):
                    icon_img = Image.open(icon_path)
                    window.update_idletasks()
                    window._set_window_icon(icon_img)
        except Exception as e:
            print(f"Error setting window icon: {e}")     

    def _get_recycled_widget(self, pool, widget_type, parent, **kwargs):
        """Get a widget from the recycling pool or create a new one with optimized configuration"""
        try:
            if pool:
                widget = pool.pop()
                try:
                    # Batch configure widget properties
                    config_updates = {}
                    for key, value in kwargs.items():
                        config_updates[key] = value
                    if config_updates:
                        widget.configure(**config_updates)
                    return widget
                except tk.TclError:
                    # Widget invalid, create new one
                    pass
                    
            # Create new widget if none available in pool
            return widget_type(parent, **kwargs)
            
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Error getting recycled widget: {e}{Style.RESET_ALL}")
            # Fallback to creating new widget
            return widget_type(parent, **kwargs)

    def _recycle_widget(self, widget, pool):
        """Add a widget to the recycling pool with error handling"""
        try:
            widget.pack_forget()
            widget.grid_forget()
            widget.place_forget()
            pool.append(widget)
        except tk.TclError:
            # Widget already destroyed or invalid
            pass
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Error recycling widget: {e}{Style.RESET_ALL}")

    @ResourceManager().debounce(500)  # Debounce save operations
    def _autosave(self):
        """Debounced autosave function"""
        if self.pending_changes:
            self.save_progress()

    def _setup_autosave(self):
        """Set up periodic autosave check"""
        def check_autosave():
            now = datetime.now()
            if self.pending_changes and self.autosave_interval > 0 and (now - self.last_save).seconds >= self.autosave_interval:
                self._autosave()
            self.window.after(1000, check_autosave)  # Check every second
        check_autosave()

    def has_tracking_data(self):
        """Check if there are any logs, streaks, or plot files."""
        # Check for logs
        if self.logs:
            return True
        # Check for streaks
        if self.streaks:
            return True
        # Check for plot files
        plots_dir = PLOTS_DIR
        if os.path.exists(plots_dir):
            plot_files = [f for f in os.listdir(plots_dir) if f.startswith('habit_streak_') and f.endswith('.png')]
            if plot_files:
                return True
        return False

    def update_clear_buttons_state(self):
        """Update the state of the 'Clear Tracking History' button in the sidebar."""
        state = "normal" if self.has_tracking_data() else "disabled"
        if hasattr(self, 'clear_btn'):
            self.clear_btn.configure(state=state)

    def _load_data(self):
        """Load all data in a background thread"""
        def load():
            try:
                self.habits = self._load_habits()
                self.logs = self._load_logs()
                self.streaks = self._load_streaks()
                
                # Update UI in main thread
                self.window.after(0, lambda: self.show_setup_view() if not self.habits else self.show_habits_view())
                self.window.after(100, self._schedule_daily_reminder) # Schedule the reminder check shortly after UI loads

                # Update navigation buttons based on habits
                if self.habits:
                    self.habits_button.configure(state="normal")
                    self.logs_button.configure(state="normal")
                    self.stats_button.configure(state="normal")
                else:
                    self.habits_button.configure(state="disabled")
                    self.logs_button.configure(state="disabled")
                    self.stats_button.configure(state="disabled")
                    
                self.window.after(0, self.update_clear_buttons_state)

            except Exception as e:
                # Show error in main thread
                self.window.after(0, lambda: self.show_error_message(str(e)))
        
        thread = threading.Thread(target=load)
        thread.daemon = True
        thread.start()

    def clear_main_frame(self):
        """Clear main frame and recycle all widgets"""
        for widget in self.main_frame.winfo_children():
            widget_type = type(widget)
            if isinstance(widget, self.ctk.CTkCheckBox):
                self._recycle_widget(widget, self._checkbox_pool)
            elif isinstance(widget, self.ctk.CTkLabel):
                self._recycle_widget(widget, self._label_pool)
            elif isinstance(widget, self.ctk.CTkButton):
                self._recycle_widget(widget, self._button_pool)
            elif isinstance(widget, self.ctk.CTkFrame):
                self._recycle_widget(widget, self._frame_pool)
            else:
                widget.destroy()  # Destroy non-recyclable widgets

    def _setup_platform_specifics(self):
        """Platform-specific initializations"""
        try:
            self.platform = platform.system().lower()
            
            if self.platform == 'windows':
                try:
                    from ctypes import windll
                    windll.shcore.SetProcessDpiAwareness(1)
                except Exception:
                    pass  # DPI awareness not critical
                    
            # Get screen dimensions
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            
            # Set desired window size (80% of screen size)
            desired_width = min(int(screen_width * 0.8), 1200)  # Cap at 1200px
            desired_height = min(int(screen_height * 0.8), 800)  # Cap at 800px
            
            # Setup window metrics
            self._setup_window_metrics(screen_width, screen_height, desired_width, desired_height)
            
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Warning: Platform detection failed: {e}{Style.RESET_ALL}")
            # Fallback to standard size
            self.window.geometry("1000x700")
            self.window.minsize(900, 600)
            
        self.platform = platform.system().lower()
        self.is_windows = (self.platform == 'windows')

    def _setup_window_metrics(self, screen_width, screen_height, desired_width, desired_height):
        """Setup window size and position with platform-specific adjustments"""
        try:            # Platform-specific margins and minimums with better scaling
            if self.platform == 'windows':
                taskbar_margin = max(80, int(screen_height * 0.05))  # At least 80px or 5% of screen height
                min_width = min(900, int(screen_width * 0.8))
                min_height = min(600, int(screen_height * 0.8))
            elif self.platform == 'darwin':
                taskbar_margin = max(100, int(screen_height * 0.06))  # Account for menu bar and dock
                min_width = min(900, int(screen_width * 0.8))
                min_height = min(600, int(screen_height * 0.8))
            else:  # Linux and others
                taskbar_margin = max(70, int(screen_height * 0.04))
                min_width = min(800, int(screen_width * 0.8))
                min_height = min(550, int(screen_height * 0.8))
                
            # Ensure window fits on screen with margin for taskbar and decorations
            max_height = screen_height - taskbar_margin - 50  # Extra 50px safety margin
            current_height = min(desired_height, max_height)
              # Calculate position to center on screen with taskbar awareness
            x = max(0, (screen_width - desired_width) // 2)  # Never negative
            y = max(0, ((screen_height - taskbar_margin) - current_height) // 2)  # Account for taskbar
            
            # Set window geometry and minimum size with error checks
            try:
                # First set minimum size to prevent window from being too small
                self.window.minsize(min_width, min_height)
                # Then set the geometry
                geometry = f"{desired_width}x{current_height}+{x}+{y}"
                self.window.geometry(geometry)
                # Verify window size after setting
                self.window.update_idletasks()
            except Exception as e:
                print(f"{Fore.LIGHTRED_EX}Warning: Error setting window geometry: {e}{Style.RESET_ALL}")
                # Fallback to simple centered window
                self.window.geometry("900x600")
            
            # Platform-specific window attributes and DPI handling
            try:
                if self.platform == 'windows':
                    # Enable DPI awareness on Windows
                    self.window.tk.call('tk', 'scaling', 1.0)
                elif self.platform == 'darwin':
                    # Ensure proper window rendering on macOS
                    self.window.lift()
                    self.window.update_idletasks()
                else:
                    # Set window type hints for Linux/Unix
                    self.window.attributes('-type', 'normal')
                    
                # Final update to ensure proper rendering
                self.window.update_idletasks()
            except Exception as e:
                print(f"{Fore.LIGHTRED_EX}Warning: Platform-specific setup failed: {e}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Warning: Window metrics setup failed: {e}{Style.RESET_ALL}")
            # Fallback to basic window setup
            self.window.geometry("1000x700")
            self.window.minsize(900, 600)

    def __del__(self):
        """Cleanup when instance is deleted"""
        try:
            # Clean up matplotlib resources if it was imported
            if 'plt' in globals():
                try:
                    plt.close('all')
                except:
                    pass
            
            # Clean up resource manager
            if hasattr(self, 'resources'):
                self.resources.clear()
            
            # Clean up instance
            if (hasattr(HabitTrackerGUI, '_instance')):
                delattr(HabitTrackerGUI, '_instance')
                
        except Exception:
            pass
            
    def on_closing(self):
        """Enhanced window closing handler with proper cleanup"""
        try:
            if (self.pending_changes):
                dialog = YesNoDialog(
                    master=self.window,
                    title="Unsaved Changes",
                    message="You have unsaved changes. Save before closing?"
                )
                if (dialog.result):
                    self.save_pending_changes()
                    
            # Ensure any open windows are properly destroyed
            if (hasattr(self, 'message_window') and (self.message_window is not None)):
                try:
                    self.message_window.window.destroy()
                except:
                    pass
            
            # Destroy all open plot windows with logging
            for pw, fp in self.plot_windows:
                try:
                    pw.destroy()
                    print(f"{Fore.LIGHTYELLOW_EX}Destroyed plot window for {fp}{Style.RESET_ALL}")
                except:
                    pass
            self.plot_windows = []  # Clear the list
            
            # Clean up matplotlib resources if it was imported
            if 'plt' in globals():
                try:
                    plt.close('all')
                except:
                    pass
            
            # Clean up resource manager
            if hasattr(self, 'resources'):
                self.resources.clear()
                
            # Clean up instance and destroy root
            if (hasattr(HabitTrackerGUI, '_instance')):
                delattr(HabitTrackerGUI, '_instance')
            
            # Final cleanup of all widgets
            for widget in self.window.winfo_children():
                try:
                    widget.destroy()
                except:
                    pass
            
            self.window.destroy()
            
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Error during cleanup: {e}{Style.RESET_ALL}")
            try:
                self.window.destroy()
            except:
                pass

    def save_pending_changes(self):
        """Save any pending changes before closing"""
        try:
            if (hasattr(self, 'habit_vars')):
                self.save_progress()
        except Exception:
            pass  # Ignore errors during cleanup

    def setup_sidebar(self):
        # Sidebar with color customization for both modes
        self.sidebar = self.ctk.CTkFrame(
            self.window, 
            width=200, 
            corner_radius=0,
            fg_color=("gray90", "#2B2B2B")  # Light mode, Dark mode
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)  # Adjusted for new icon
        
        # Load and display app icon
        try:
            if platform.system() == 'Windows':
                icon_path = get_asset_path('icon.ico')
            else:
                icon_path = get_asset_path('icon.png')
                
            if os.path.exists(icon_path):
                # Create CTkImage for the icon
                icon_image = self.ctk.CTkImage(
                    light_image=Image.open(icon_path),
                    dark_image=Image.open(icon_path),
                    size=(48, 48)  # Reasonable size for sidebar
                )
                
                # Create label for icon
                icon_label = self.ctk.CTkLabel(
                    self.sidebar,
                    image=icon_image,
                    text=""  # No text, just the icon
                )
                icon_label.grid(row=0, column=0, padx=20, pady=(20, 5))
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Warning: Could not load sidebar icon: {e}{Style.RESET_ALL}")
        
        # Logo label with version and color customization
        self.logo_label = self.ctk.CTkLabel(
            self.sidebar, 
            text="HABIT TRACKER",
            font=self.ctk.CTkFont(size=20, weight="bold"),
            text_color=("gray10", "gray90")  # Light mode, Dark mode
        )
        self.logo_label.grid(row=1, column=0, padx=20, pady=(5, 20))
        
        # Navigation buttons with proper color scheme
        button_config = {
            "fg_color": ("gray80", "gray20"),  # Light mode, Dark mode
            "hover_color": ("gray70", "gray30"),
            "text_color": ("gray10", "gray90")
        }
        
        self.habits_button = self.ctk.CTkButton(
            self.sidebar, 
            text="Habits",
            command=self.show_habits_view,
            state="disabled" if not self.habits else "normal",
            **button_config
        )
        self.habits_button.grid(row=2, column=0, padx=20, pady=10)
        self.habits_button.tooltip = None
        self.habits_button.tooltip_timer = None
        self.habits_button.bind('<Enter>', lambda e: self._show_tooltip(e, self.habits_button, "No habits found!"))
        self.habits_button.bind('<Leave>', lambda e: self._hide_tooltip(e, self.habits_button))

        self.logs_button = self.ctk.CTkButton(
            self.sidebar, 
            text="View Logs",
            command=self.show_logs_view,
            state="disabled" if not self.habits else "normal",
            **button_config
        )
        self.logs_button.grid(row=3, column=0, padx=20, pady=10)
        self.logs_button.tooltip = None
        self.logs_button.tooltip_timer = None
        self.logs_button.bind('<Enter>', lambda e: self._show_tooltip(e, self.logs_button, "No habits found!"))
        self.logs_button.bind('<Leave>', lambda e: self._hide_tooltip(e, self.logs_button))

        self.stats_button = self.ctk.CTkButton(
            self.sidebar, 
            text="Statistics",
            command=self.show_stats_view,
            state="disabled" if not self.habits else "normal",
            **button_config
        )
        self.stats_button.grid(row=4, column=0, padx=20, pady=10)
        self.stats_button.tooltip = None
        self.stats_button.tooltip_timer = None
        self.stats_button.bind('<Enter>', lambda e: self._show_tooltip(e, self.stats_button, "No habits found!"))
        self.stats_button.bind('<Leave>', lambda e: self._hide_tooltip(e, self.stats_button))

        self.settings_button = self.ctk.CTkButton(
            self.sidebar,
            text="⚙️ Settings",
            command=self.open_settings_window,
            fg_color=("gray80", "gray20"),
            hover_color=("gray70", "gray30"),
            text_color=("gray10", "gray90")
        )
        self.settings_button.grid(row=5, column=0, padx=20, pady=10)
        
    def setup_main_frame(self):
        # Main frame with color customization
        self.main_frame = self.ctk.CTkFrame(
            self.window,
            fg_color=("gray95", "#292929")  # Light mode, Dark mode
        )
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
    def show_habits_view(self):
        """Show habits view with optimized performance"""
        self.show_view(self._show_habits_view)

    def show_logs_view(self):
        """Show logs view with optimized performance"""
        self.show_view(self._show_logs_view)

    def show_stats_view(self):
        """Show statistics view with optimized performance"""
        self.show_view(self._show_stats_view)

    def show_setup_view(self):
        """Show setup view with optimized performance"""
        self.show_view(self._show_setup_view)

    def _show_habits_view(self):
        """Internal optimized habits view implementation"""
        # Configure grid before creating widgets for better performance
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Create header frame
        header_frame = self.ctk.CTkFrame(
            self.main_frame,
            fg_color=("gray90", "#2B2B2B"),
            corner_radius=10
        )
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title = self.ctk.CTkLabel(
            header_frame, 
            text="Daily Habits Check-in",
            font=self.ctk.CTkFont(size=28, weight="bold"),
            text_color=("gray10", "gray90")
        )
        title.grid(row=0, column=0, pady=(20, 5))
        
        # Today's date prominently displayed
        today = datetime.now().strftime('%Y-%m-%d')
        date_label = self.ctk.CTkLabel(
            header_frame,
            text=f"Today's Date: {today}",
            font=self.ctk.CTkFont(size=16, weight="bold"),
            text_color=("gray20", "gray80")
        )
        date_label.grid(row=1, column=0, pady=(0, 10))

        # Instructions section
        instructions_frame = self.ctk.CTkFrame(
            self.main_frame,
            fg_color=("gray95", "#232323"),
            corner_radius=10
        )
        instructions_frame.grid(row=1, column=0, padx=(20, 10), pady=(5, 20), sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)  # Give equal weight to first column
        instructions_frame.grid_columnconfigure(0, weight=1)
        
        # Instructions with icons and better formatting
        instructions_text = [
            ("✓", "Check habits you've completed"),
            ("✗", "Leave incomplete habits unchecked"),
            ("🔥", "Watch your streak grow"),
            ("💾", "Progress saves automatically")
        ]
        
        for i, (icon, text) in enumerate(instructions_text):
            instruction_row = self.ctk.CTkFrame(instructions_frame, fg_color="transparent")
            instruction_row.grid(row=i, column=0, sticky="ew", pady=5, padx=15)
            instruction_row.grid_columnconfigure(1, weight=1)
            
            icon_label = self.ctk.CTkLabel(
                instruction_row,
                text=icon,
                font=self.ctk.CTkFont(size=20),
                width=30
            )
            icon_label.grid(row=0, column=0, padx=(5, 10))
            
            text_label = self.ctk.CTkLabel(
                instruction_row,
                text=text,
                font=self.ctk.CTkFont(size=14),
                justify="left"
            )
            text_label.grid(row=0, column=1, sticky="w")

        # Habits section with visual improvements
        habits_container = self.ctk.CTkFrame(
            self.main_frame,
            fg_color=("gray95", "#232323"),
            corner_radius=10
        )
        habits_container.grid(row=1, column=1, padx=(10, 20), pady=(5, 20), sticky="nsew")
        self.main_frame.grid_columnconfigure(1, weight=1)  # Give equal weight to second column
        habits_container.grid_columnconfigure(0, weight=1)
        habits_container.grid_rowconfigure(1, weight=1)
        
        # Header for habits section
        habits_header = self.ctk.CTkLabel(
            habits_container,
            text="Your Daily Habits",
            font=self.ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray20", "gray80")
        )
        habits_header.grid(row=0, column=0, pady=(15, 5))
        
        # Scrollable frame for habits with improved sizing
        habits_frame = self.ctk.CTkScrollableFrame(
            habits_container,
            width=400  # Minimum width
        )
        habits_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        habits_frame.grid_columnconfigure(0, weight=1)  # Make habit frame expandable
        
        # Create checkboxes for each habit with auto-save
        self.habit_vars = {}
        self.streak_labels = {}
        
        def on_checkbox_click(habit):
            """Handle checkbox click with auto-save"""
            try:
                # Get all current values
                current_values = {h: var.get() for h, var in self.habit_vars.items()}
                
                # Create new log entry
                new_logs = [[h, today, completed] for h, completed in current_values.items()]
                
                # Filter out any existing logs for today
                self.logs = [log for log in self.logs if log[1] != today]
                
                # Add new logs
                self.logs.extend(new_logs)
                
                # Update streaks
                self._update_streaks(self.logs, self.habits, self.streaks)
                
                # Save to disk
                if (self._save_logs(self.logs, self.streaks)):
                    # Update streak display
                    for h, streak_label in self.streak_labels.items():
                        streak_label.configure(text=f"🔥 {self.streaks.get(h, 0)}")
                    
                    # Show auto-save indicator briefly
                    self.show_autosave_status("Progress auto-saved")
                    self.update_clear_buttons_state()
                    
            except Exception as e:
                self.show_error_message(f"Error saving progress: {str(e)}")
        
        # Create habit checkboxes with improved visual hierarchy and sizing
        for i, habit in enumerate(self.habits):
            habit_row = self.ctk.CTkFrame(habits_frame, fg_color="transparent")
            habit_row.grid(row=i*2, column=0, sticky="ew", pady=4)
            habit_row.grid_columnconfigure(1, weight=1)  # Allow habit row to expand
            
            var = tk.BooleanVar()
            # Pre-check if already completed today
            today_log = next((log for log in self.logs if log[0] == habit and log[1] == today), None)
            if (today_log):
                var.set(today_log[2])
            
            # Create checkbox with proper text handling
            checkbox = self.ctk.CTkCheckBox(
                habit_row, 
                text=habit,
                variable=var,
                font=self.ctk.CTkFont(size=16),
                command=lambda h=habit: on_checkbox_click(h),
                border_width=2,
                checkbox_width=24,
                checkbox_height=24
            )
            checkbox.grid(row=0, column=0, sticky="w", padx=(10, 0))
            
            # Store the variable reference to prevent garbage collection
            checkbox._variable_keeper = var  # Keep reference to prevent garbage collection
            
            streak = self.streaks.get(habit, 0)
            streak_label = self.ctk.CTkLabel(
                habit_row,
                text=f"🔥 {streak}",
                font=self.ctk.CTkFont(size=16),
                text_color=("#FF6B6B", "#FFB86B") if (streak > 0) else ("gray40", "gray60")
            )
            streak_label.grid(row=0, column=2, padx=15)
            
            self.habit_vars[habit] = var
            self.streak_labels[habit] = streak_label
            
            # Add subtle separator between habits
            if (i < (len(self.habits) - 1)):
                separator = self.ctk.CTkFrame(
                    habits_frame,
                    height=1,
                    fg_color=("gray80", "gray40")
                )
                separator.grid(row=i*2+1, column=0, sticky="ew", pady=4, padx=5)
        
        # Controls frame at bottom
        controls = self.ctk.CTkFrame(habits_container, fg_color="transparent")
        controls.grid(row=2, column=0, sticky="ew", padx=15, pady=15)
        controls.grid_columnconfigure(1, weight=1)
        
        # Auto-save status with subtle styling
        self.autosave_label = self.ctk.CTkLabel(
            controls,
            text="",
            font=self.ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
            width=150  # Fixed width to accommodate the message
        )
        self.autosave_label.grid(row=0, column=0, sticky="w", padx=(10, 0))  # Added left padding
        
        # Save & Continue button with improved styling
        save_button = self.ctk.CTkButton(
            controls,
            text="Save & Continue",
            command=self.finish_habit_logging,
            font=self.ctk.CTkFont(size=14, weight="bold"),
            height=32
        )
        save_button.grid(row=0, column=2, sticky="e")
        
        # Copyright at bottom
        from habit_engine.__init__ import __copyright__
        copyright = self.ctk.CTkLabel(
            self.main_frame,
            text=__copyright__,
            font=self.ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        copyright.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="e")
            
    def show_autosave_status(self, message, duration=1500):
        """Show auto-save status briefly"""
        if (hasattr(self, 'autosave_label')):
            self.autosave_label.configure(text=message)
            self.window.after(duration, lambda: self.autosave_label.configure(text=""))
            
    def finish_habit_logging(self):
        """Complete habit logging and show next steps"""
        try:
            # Final save
            if (self._save_logs(self.logs, self.streaks)):
                self.show_success_message("Progress saved successfully!\n\nPlease Wait...")
                # Show next action dialog
                self.window.after(2100, self.ask_next_action)
            else:
                self.show_error_message("Failed to save progress")
        except Exception as e:
            self.show_error_message(f"Error saving progress: {str(e)}")
            
    def ask_next_action(self):
        """Show dialog asking user what they want to do next"""
        dialog = self.ctk.CTkToplevel(self.window)
        dialog.title("What's Next?")
        
        # Remove window decorations including icon for all platforms
        platform_name = platform.system().lower()
        if platform_name == 'windows':
            try:
                dialog.wm_iconbitmap("")
            except: pass
        elif platform_name == 'darwin':  # macOS
            try:
                dialog.wm_iconphoto(False, tk.PhotoImage())
            except: pass
        else:  # Linux/Unix
            try:
                dialog.wm_withdraw()
                dialog.wm_deiconify()
                dialog.attributes('-type', 'dialog')
            except: pass
        
        # Platform-specific window attributes
        if self.is_windows:
            dialog.attributes('-toolwindow', True)  # Windows-specific
        else:
            dialog.attributes('-type', 'dialog')  # Unix-specific
        dialog.attributes('-topmost', True)
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Increase width to accommodate buttons
        window_width = 600  # Increased from 400
        window_height = 200
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Message
        message = self.ctk.CTkLabel(dialog, 
                             text="What would you like to do next?",
                             font=self.ctk.CTkFont(size=16))
        message.pack(pady=20)
        
        # Buttons frame with more spacing
        buttons = self.ctk.CTkFrame(dialog)
        buttons.pack(fill="x", padx=40, pady=20)  # Increased padding
        
        def view_logs():
            dialog.destroy()
            self.show_logs_view()
            
        def view_stats():
            dialog.destroy()
            self.show_stats_view()
            
        def close():
            dialog.destroy()
        
        # Action buttons with increased width
        logs_btn = self.ctk.CTkButton(buttons, text="View Logs", command=view_logs, width=150)  # Increased width
        logs_btn.pack(side="left", expand=True, padx=20)  # Increased padding
        
        stats_btn = self.ctk.CTkButton(buttons, text="View Statistics", command=view_stats, width=150)
        stats_btn.pack(side="left", expand=True, padx=20)
        
        close_btn = self.ctk.CTkButton(buttons, text="Stay Here", command=close, width=150)
        close_btn.pack(side="left", expand=True, padx=20)

    def save_progress(self):
        """Enhanced save progress with next action prompt"""
        if (not hasattr(self, 'habit_vars')):
            return
            
        today = datetime.now().strftime('%Y-%m-%d')
        new_logs = []
        
        try:
            for habit, var in self.habit_vars.items():
                completed = var.get()
                new_logs.append([habit, today, completed])
                
            self.logs.extend(new_logs)
            self._update_streaks(self.logs, self.habits, self.streaks)
            
            if (self._save_logs(self.logs, self.streaks)):
                self.show_success_message("Progress saved successfully!\n\nPlease Wait...")
                # Show next action dialog after success message
                self.window.after(2100, self.ask_next_action)
            else:
                self.show_error_message("Failed to save progress")
        except Exception as e:
            self.show_error_message(f"Error saving progress: {str(e)}")
            
    def _show_logs_view(self):
        """Internal optimized logs view implementation"""
        # Configure grid with proper weights
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Prepare batch updates
        updates = []
        
        # Create header frame
        header_frame = self.ctk.CTkFrame(
            self.main_frame,
            fg_color=("gray90", "#2B2B2B")
        )
        updates.append((header_frame, {"row": 0, "column": 0, "sticky": "ew", "pady": (0, 20)}))
        
        header = self.ctk.CTkLabel(
            header_frame, 
            text="Habit Logs",
            font=self.ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=20)
        
        # Create scrollable frame with deferred rendering
        scroll_frame = self.ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color=("gray95", "#292929")
        )
        updates.append((scroll_frame, {"row": 1, "column": 0, "sticky": "nsew", "padx": 20, "pady": (0, 20)}))
        
        # Pre-process logs by date for better performance
        logs_by_date = {}
        for log in self.logs:
            date = log[1]
            if date not in logs_by_date:
                logs_by_date[date] = []
            logs_by_date[date].append(log)
        
        if logs_by_date:
            # Create log entries with deferred rendering
            def create_log_chunk(dates, start_idx, chunk_size):
                end_idx = min(start_idx + chunk_size, len(dates))
                current_dates = sorted(dates[start_idx:end_idx], reverse=True)
                
                for date in current_dates:
                    date_label = self.ctk.CTkLabel(
                        scroll_frame, 
                        text=date,
                        font=self.ctk.CTkFont(size=16, weight="bold")
                    )
                    date_label.pack(anchor="w", pady=(10, 5))
                    
                    for log in logs_by_date[date]:
                        habit, _, completed = log
                        status = "✓" if completed else "✗"
                        color = "green" if completed else "red"
                        
                        log_label = self.ctk.CTkLabel(
                            scroll_frame,
                            text=f"{status} {habit}",
                            text_color=color,
                            font=self.ctk.CTkFont(size=14)
                        )
                        log_label.pack(anchor="w", padx=20)
                    
                # Schedule next chunk if needed
                if end_idx < len(dates):
                    self.window.after(10, lambda: create_log_chunk(dates, end_idx, chunk_size))
                
            # Start deferred rendering with chunks
            dates = list(logs_by_date.keys())
            create_log_chunk(dates, 0, 5)  # Render 5 dates at a time
        else:
            # Show empty state
            no_logs_label = self.ctk.CTkLabel(
                scroll_frame,
                text="No habit logs found.\nComplete some habits to see them here!",
                font=self.ctk.CTkFont(size=14)
            )
            no_logs_label.pack(pady=20)

        clear_btn = self.ctk.CTkButton(
            self.main_frame,
            text="Clear Tracking History",
            fg_color="transparent",
            border_width=3,
            border_color=("gray40", "gray60"),
            hover_color="darkred",
            command=self.confirm_clear_logs,
            state="normal" if self.has_tracking_data() else "disabled"
        )
        clear_btn.tooltip = None
        clear_btn.tooltip_timer = None
        clear_btn.bind('<Enter>', lambda e: self._show_tooltip(e, clear_btn, "No Tracking History to Clear!"))
        clear_btn.bind('<Leave>', lambda e: self._hide_tooltip(e, clear_btn))
        updates.append((clear_btn, {"row": 2, "column": 0, "padx": 20, "pady": (0, 20)}))

        # Copyright at bottom
        from habit_engine.__init__ import __copyright__
        copyright = self.ctk.CTkLabel(
            self.main_frame,
            text=__copyright__,
            font=self.ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        updates.append((copyright, {"row": 3, "column": 0, "padx": 20, "pady": 10, "sticky": "e"}))
        
        # Apply all grid configurations at once
        for widget, grid_args in updates:
            widget.grid(**grid_args)

    def confirm_clear_logs(self):
        """Prompt user before clearing logs, streaks, and plots (habits are preserved)."""
        dialog = YesNoDialog(
            master=self.window,
            title="Confirm Clear",
            message="You are about to clear all your logs, streaks, and plots.\nHabits will NOT be affected.\n\nWould you like to continue?",
            yes_fg_color="darkred",
            yes_hover_color="red",
            no_fg_color="darkgreen",
            no_hover_color="green"
        )
        if dialog.result:
            success = clear_tracking_data()
            if success:
                self.logs = []
                self.streaks = {}
                self.show_success_message("Logs, streaks, and plots cleared successfully.")
                self.show_logs_view()
                self.update_clear_buttons_state()
            else:
                self.show_error_message("Failed to clear logs.")        
                
    def _show_stats_view(self):
        """Show statistics view with optimized performance"""
        try:
            # Configure grid layout
            self.main_frame.grid_columnconfigure(0, weight=1)
            self.main_frame.grid_rowconfigure(1, weight=1)
            
            # Prepare batch updates
            updates = []
            
            # Header section with custom styling
            header_frame = self.ctk.CTkFrame(
                self.main_frame,
                fg_color=("gray90", "#2B2B2B")
            )
            updates.append((header_frame, {"row": 0, "column": 0, "sticky": "ew", "pady": (0, 20)}))
            
            title = self.ctk.CTkLabel(
                header_frame, 
                text="Statistics & Visualization",
                font=self.ctk.CTkFont(size=24, weight="bold")
            )
            title.pack(pady=(20, 5))
            
            instructions_text = (
                "Select a habit and click 'Visualize' to see your progress over time.\n"
                f"Visualizations are saved as .png files in your plots directory"
            )
            self.instructions = self.ctk.CTkLabel(
                header_frame,
                text=instructions_text,
                font=self.ctk.CTkFont(size=14)
            )
            self.instructions.pack(pady=(0, 20))

            btn_open_plots = self.ctk.CTkButton(
                header_frame,
                text="Open Plots Folder",
                command=self._open_plots_dir,
                width=200
            )
            btn_open_plots.pack(pady=(5, 20))

            # Controls section with better layout
            controls = self.ctk.CTkFrame(self.main_frame)
            updates.append((controls, {"row": 1, "column": 0, "sticky": "new", "padx": 20, "pady": 10}))
            controls.grid_columnconfigure(1, weight=1)
            
            # Habit selection
            habit_label = self.ctk.CTkLabel(controls, text="Select habit:")
            habit_label.grid(row=0, column=0, padx=10, pady=5)
            
            # Pre-calculate habit names for dropdown
            habit_names = ["No habits yet"] if not self.habits else self.habits
            
            # Use StringVar for habit selection
            self.selected_habit = tk.StringVar()
            habit_dropdown = self.ctk.CTkOptionMenu(
                controls,
                values=habit_names,
                variable=self.selected_habit,
                state="disabled" if not self.habits else "normal",
                width=250
            )
            self.selected_habit.set(habit_names[0])
            habit_dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
            
            # Status label with better positioning
            self.viz_status = self.ctk.CTkLabel(
                controls, 
                text="",
                width=120
            )
            self.viz_status.grid(row=0, column=2, padx=20, pady=5)
            
            # Visualize button with improved styling
            self.visualize_btn = self.ctk.CTkButton(
                controls, 
                text="Visualize",
                command=self.create_visualization,
                state="normal" if self.habits else "disabled",
                width=120
            )
            self.visualize_btn.grid(row=0, column=3, padx=20, pady=5)

            # Check for existing plots
            plots_dir = PLOTS_DIR
            if os.path.exists(plots_dir):
                existing_plots = [f for f in os.listdir(plots_dir) if f.startswith('habit_streak_') and f.endswith('.png')]
                if existing_plots:
                    view_existing_btn = self.ctk.CTkButton(
                        controls,
                        text="View Existing Plots",
                        command=self.show_existing_plots,
                        width=120
                    )
                    view_existing_btn.grid(row=0, column=4, padx=20, pady=5)
            
            # Plot area with placeholder
            self.plot_frame = self.ctk.CTkFrame(self.main_frame)
            updates.append((self.plot_frame, {"row": 2, "column": 0, "sticky": "nsew", "padx": 20, "pady": 20}))
            self.plot_frame.grid_columnconfigure(0, weight=1)
            self.plot_frame.grid_rowconfigure(0, weight=1)
            
            if not self.habits:
                placeholder = self.ctk.CTkLabel(
                    self.plot_frame,
                    text="No habits available for visualization.\nPlease add some habits first.",
                    font=self.ctk.CTkFont(size=14)
                )
                placeholder.grid(row=0, column=0, padx=20, pady=20)
            
            # Bottom frame with improved layout
            bottom_frame = self.ctk.CTkFrame(self.main_frame)
            updates.append((bottom_frame, {"row": 3, "column": 0, "sticky": "ew", "padx": 20, "pady": (0, 10)}))
            bottom_frame.grid_columnconfigure(0, weight=1)
            
            # Copyright with proper styling
            from habit_engine.__init__ import __copyright__
            copyright = self.ctk.CTkLabel(
                bottom_frame,
                text=__copyright__,
                font=self.ctk.CTkFont(size=12),
                text_color=("gray40", "gray60")
            )
            copyright.grid(row=0, column=0, sticky="e", padx=20, pady=10)
            
            # Apply all grid configurations at once
            for widget, grid_args in updates:
                widget.grid(**grid_args)

        except Exception as e:
            self.show_error_message(f"Error showing statistics view: {str(e)}")
            print(f"{Fore.LIGHTRED_EX}Error in statistics view: {e}{Style.RESET_ALL}")

    def _open_data_dir(self):
        path = os.path.abspath(DATA_DIR)
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])

    def _open_plots_dir(self):
        path = os.path.abspath(PLOTS_DIR)
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])


    def show_existing_plots(self):
        """Show a dialog with existing plot files"""
        try:
            dialog = self.ctk.CTkToplevel(self.window)
            dialog.title("Existing Plots")
            self.remove_window_icon(dialog)
            
            dialog.attributes('-topmost', True)
            # dialog.grab_set()

            # Set size and position
            window_width = 600
            window_height = 400
            screen_width = dialog.winfo_screenwidth()
            screen_height = dialog.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")

            # Create scrollable frame for plots
            scroll_frame = self.ctk.CTkScrollableFrame(dialog)
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

            plots_dir = PLOTS_DIR
            plot_files = []
            if os.path.exists(plots_dir):
                plot_files = [f for f in os.listdir(plots_dir) if f.startswith('habit_streak_') and f.endswith('.png')]
                plot_files.sort(reverse=True)  # Most recent first

            if plot_files:
                for plot_file in plot_files:
                    # Extract habit name and date from filename
                    # Format: habit_streak_habitname_YYYYMMDD_HHMMSS.png
                    parts = plot_file.replace('habit_streak_', '').replace('.png', '').split('_')
                    if len(parts) >= 3:
                        habit_name = '_'.join(parts[:-2])
                        date_str = parts[-2]
                        time_str = parts[-1]
                        try:
                            date_time = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                            formatted_date = date_time.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            formatted_date = "Unknown date"

                        # Create frame for each plot entry
                        plot_frame = self.ctk.CTkFrame(scroll_frame)
                        plot_frame.pack(fill="x", padx=5, pady=5)

                        # Plot info
                        info_text = f"Habit: {habit_name}\nCreated: {formatted_date}"
                        info_label = self.ctk.CTkLabel(
                            plot_frame,
                            text=info_text,
                            justify="left"
                        )
                        info_label.pack(side="left", padx=10, pady=5)

                        # Buttons frame
                        btn_frame = self.ctk.CTkFrame(plot_frame, fg_color="transparent")
                        btn_frame.pack(side="right", padx=10)

                        # View button
                        view_btn = self.ctk.CTkButton(
                            btn_frame,
                            text="View",
                            command=lambda f=plot_file: self.open_plot_file(os.path.join(plots_dir, f), parent=dialog),
                            width=70
                        )
                        view_btn.pack(side="left", padx=5)

                        # Delete button
                        delete_btn = self.ctk.CTkButton(
                            btn_frame,
                            text="Delete",
                            command=lambda f=plot_file, frame=plot_frame: self.delete_plot(f, frame),
                            fg_color="red",
                            hover_color="darkred",
                            width=70
                        )
                        delete_btn.pack(side="left", padx=5)

            else:
                no_plots_label = self.ctk.CTkLabel(
                    scroll_frame,
                    text="No plots found",
                    font=self.ctk.CTkFont(size=14)
                )
                no_plots_label.pack(pady=20)

            # Close button at bottom
            close_btn = self.ctk.CTkButton(
                dialog,
                text="Close",
                command=dialog.destroy,
                width=100
            )
            close_btn.pack(pady=20)

        except Exception as e:
            self.show_error_message(f"Error showing plots: {str(e)}")

    def open_plot_file(self, filepath, parent=None):
        try:
            print(f"{Fore.LIGHTCYAN_EX}Attempting to open plot in GUI window: {filepath}{Style.RESET_ALL}")
            img = Image.open(filepath)
            img_width, img_height = img.size
            # Constrain image size to fit within 80% of screen
            max_width = int(self.window.winfo_screenwidth() * 0.8)
            max_height = int(self.window.winfo_screenheight() * 0.8)
            if img_width > max_width or img_height > max_height:
                # Resize image while maintaining aspect ratio
                ratio = min(max_width / img_width, max_height / img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                img = img.resize((new_width, new_height), Image.LANCZOS)
                img_width, img_height = new_width, new_height
            parent = parent or self.window  # fallback to main window
            plot_window = self.ctk.CTkToplevel(parent)
            self.remove_window_icon(plot_window)
            self.plot_windows.append((plot_window, filepath))
            plot_window.title(f"Plot: {os.path.basename(filepath)}")
            # Bring to front and focus
            plot_window.transient(parent)
            try:
                if plot_window.winfo_exists():
                    plot_window.lift()
                    plot_window.attributes("-topmost", True)
                    plot_window.focus_force()
            except tk.TclError:
                pass

            screen_width = parent.winfo_screenwidth()
            screen_height = parent.winfo_screenheight()
            x = (screen_width - img_width) // 2
            y = (screen_height - img_height) // 2
            plot_window.geometry(f"{img_width}x{img_height}+{x}+{y}")
            from customtkinter import CTkImage
            ctk_img = CTkImage(light_image=img, dark_image=img, size=(img_width, img_height))
            label = self.ctk.CTkLabel(plot_window, image=ctk_img, text="")
            label.pack()
            label.image = ctk_img
            plot_window.protocol("WM_DELETE_WINDOW", lambda pw=plot_window: self.on_plot_window_close(pw))
            print(f"{Fore.LIGHTGREEN_EX}Opened plot window for {filepath}{Style.RESET_ALL}")
        except Exception as e:
            self.show_error_message(f"Error opening file: {str(e)}")
            print(f"{Fore.LIGHTRED_EX}Error in open_plot_file: {str(e)}{Style.RESET_ALL}")    

    def on_plot_window_close(self, plot_window):
        for item in self.plot_windows:
            if item[0] == plot_window:
                fp = item[1]
                self.plot_windows.remove(item)
                print(f"{Fore.LIGHTYELLOW_EX}Closed plot window for {fp}{Style.RESET_ALL}")
                break
        plot_window.destroy()

    def delete_plot(self, filename, frame):
        """Delete a plot file and remove it from the dialog"""
        try:
            filepath = os.path.join(PLOTS_DIR, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                frame.destroy()
                self.show_success_message("Plot deleted successfully")
                self.update_clear_buttons_state()
        except Exception as e:
            self.show_error_message(f"Error deleting plot: {str(e)}")

    def create_visualization(self):
        """Create visualization with enhanced error handling"""
        try:
            habit_name = self.selected_habit.get()
            if not habit_name or habit_name == "No habits yet":
                self.show_error_message("Please select a habit first")
                return
                
            # Disable button and show status
            self.visualize_btn.configure(state="disabled")
            self.viz_status.configure(text="Generating visualization...")
            
            # Clear previous plot
            for widget in self.plot_frame.winfo_children():
                widget.destroy()

            # Check if we have data for this habit
            habit_logs = [log for log in self.logs if log[0] == habit_name]
            if not habit_logs:
                self.show_error_message(f"No data available for {habit_name}")
                self.visualize_btn.configure(state="normal")
                self.viz_status.configure(text="")
                return

            def create_viz():
                try:
                    # Generate visualization in background
                    result = self._visualize(self.logs, habit_name, chart_style=self.chart_style, show_streak_annotations=self.show_streak_annotations, date_range=self.chart_date_range)
                    
                    def update_ui():
                        if result and os.path.exists(result):
                            # Reset button and status
                            self.visualize_btn.configure(state="normal")
                            self.viz_status.configure(text="")
                            
                            # Show the view options dialog
                            self.window.after(100, lambda: self.show_view_options(result))
                            self.update_clear_buttons_state()
                        else:
                            self.show_error_message("Failed to create visualization")
                            self.visualize_btn.configure(state="normal")
                            self.viz_status.configure(text="")
                    
                    # Update UI in main thread
                    self.window.after(0, update_ui)
                    
                except Exception as e:
                    self.window.after(0, lambda: self.show_error_message(f"Error creating visualization: {str(e)}"))
                    self.window.after(0, lambda: self.visualize_btn.configure(state="normal"))
                    self.window.after(0, lambda: self.viz_status.configure(text=""))
            
            # Run visualization in background thread
            viz_thread = threading.Thread(target=create_viz)
            viz_thread.daemon = True
            viz_thread.start()
            
        except Exception as e:
            self.show_error_message(f"Error: {str(e)}")
            self.visualize_btn.configure(state="normal")
            self.viz_status.configure(text="")

    def show_view_options(self, filepath):
        """Show dialog with options to view or open visualization"""
        try:
            view_dialog = self.ctk.CTkToplevel(self.window)
            view_dialog.title("View Visualization")
            self.remove_window_icon(view_dialog)
            
            view_dialog.attributes('-topmost', True)
            view_dialog.grab_set()
            
            # Set size and position
            dialog_width = 450
            dialog_height = 200
            x = (self.window.winfo_screenwidth() - dialog_width) // 2
            y = (self.window.winfo_screenheight() - dialog_height) // 2
            view_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
            
            # Message
            msg = self.ctk.CTkLabel(
                view_dialog,
                text="Visualization created successfully!\nWould you like to view it?",
                font=self.resources.cache_font("Helvetica", 14)
            )
            msg.pack(pady=20)
            
            # Buttons frame
            btn_frame = self.ctk.CTkFrame(view_dialog)
            btn_frame.pack(pady=10)
            
            def open_folder():
                try:
                    folder = os.path.dirname(filepath)
                    if platform.system() == 'Windows':
                        os.startfile(folder)
                    elif platform.system() == 'Darwin':
                        os.system(f'open "{folder}"')
                    else:
                        os.system(f'xdg-open "{folder}"')
                except Exception as e:
                    self.show_error_message(f"Error opening folder: {str(e)}")
                finally:
                    view_dialog.destroy()
            
            # Create buttons
            view_btn = self.ctk.CTkButton(btn_frame, text="View Plot", command=lambda: [self.open_plot_file(filepath), view_dialog.destroy()])
            view_btn.pack(side="left", padx=5)
            
            folder_btn = self.ctk.CTkButton(btn_frame, text="Open Folder", command=open_folder)
            folder_btn.pack(side="left", padx=5)
            
            close_btn = self.ctk.CTkButton(btn_frame, text="Close", command=view_dialog.destroy)
            close_btn.pack(side="left", padx=5)
            
            # Handle window close button
            view_dialog.protocol("WM_DELETE_WINDOW", view_dialog.destroy)
            
        except Exception as e:
            self.show_error_message(f"Error showing dialog: {str(e)}")
            self.visualize_btn.configure(state="normal")
            self.viz_status.configure(text="")

    def show_license_dialog(self):
        """Show license text in a scrollable dialog with PyInstaller compatibility."""
        try:
            # Create dialog window
            dialog = self.ctk.CTkToplevel(self.window)
            dialog.title("MIT License")
            self.remove_window_icon(dialog)
            
            dialog.attributes('-topmost', True)
            dialog.transient(self.settings_window)
            # dialog.grab_set()
            
            # Set size and position
            window_width = 600
            window_height = 400
            screen_width = dialog.winfo_screenwidth()
            screen_height = dialog.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # Create scrollable text area
            text_frame = self.ctk.CTkScrollableFrame(dialog)
            text_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Get license text with PyInstaller compatibility
            try:
                # First try reading from file system (development mode)
                license_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'LICENSE')
                if (os.path.exists(license_path)):
                    with open(license_path, 'r', encoding='utf-8') as file:
                        license_text = file.read()
                else:
                    # Fallback to embedded license text for compiled version
                    try:
                        from habit_engine.__init__ import __license_text__
                        license_text = __license_text__
                    except ImportError:
                        license_text = "MIT License text not available in this build."
                    
                # Display license text
                license_label = self.ctk.CTkLabel(
                    text_frame,
                    text=license_text,
                    font=self.ctk.CTkFont(family="Courier", size=12),
                    justify="left",
                    wraplength=window_width-60
                )
                license_label.pack(pady=10)
                
            except Exception as e:
                error_label = self.ctk.CTkLabel(
                    text_frame, 
                    text=f"Error loading license: {str(e)}",
                    text_color=("red", "red")
                )
                error_label.pack(pady=20)
            
            # Close button
            close_btn = self.ctk.CTkButton(
                dialog,
                text="Close",
                command=dialog.destroy,
                width=100
            )
            close_btn.pack(pady=20)
            
        except Exception as e:
            self.show_error_message(f"Error showing license: {str(e)}")

    def show_success_message(self, message):
        """Show success message in a popup window"""
        try:
            # Clean up any existing message window
            if hasattr(self, 'message_window') and self.message_window:
                try:
                    self.message_window.destroy()
                except:
                    pass
                self.message_window = None
                
            parent = self.settings_window if getattr(self, "settings_window", None) and self.settings_window.winfo_exists() else self.window

            self.message_window = MessageWindow(
                master=parent,
                title="Success",
                message=message,
                duration=1500
            )
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Error showing success message: {e}{Style.RESET_ALL}")
            
    def show_error_message(self, message, on_close=None):
        """Show error message in a popup window"""
        try:
            # Clean up any existing message window
            if hasattr(self, 'message_window') and self.message_window:
                try:
                    self.message_window.destroy()
                except:
                    pass
                self.message_window = None
                
            self.message_window = MessageWindow(
                master=self.window,
                title="Error",
                message=message,
                duration=1700,
                on_close=on_close
            )
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Error showing error message: {e}{Style.RESET_ALL}")
            
    def after_success_action(self, action):
        """Execute an action after success message disappears"""
        self.window.after(1800, action)  # 1500ms for message + 300ms buffer
            
    def show_reset_confirmation(self):
        """Show reset confirmation dialog"""
        try:
            # Create dialog window
            dialog = self.ctk.CTkToplevel(self.window)
            dialog.title("Reset Confirmation")
            
            # Remove window decorations including icon for all platforms
            platform_name = platform.system().lower()
            if platform_name == 'windows':
                try:
                    # Remove icon from title bar on Windows
                    dialog.wm_iconbitmap("")
                    # Additional Windows-specific icon removal
                    dialog.overrideredirect(True)  # Remove title bar completely
                    dialog.attributes('-toolwindow', True)  # Use tool window style
                except: pass
            elif platform_name == 'darwin':  # macOS
                try:
                    # Remove window proxy icon on macOS
                    dialog.wm_iconphoto(False, tk.PhotoImage())
                    dialog.createcommand('::tk::mac::ReopenApplication', lambda: None)
                except: pass
            else:  # Linux/Unix
                try:
                    # Remove window icon on Linux/Unix
                    dialog.wm_withdraw()
                    dialog.wm_deiconify()
                    dialog.attributes('-type', 'dialog')
                    dialog.attributes('-toolwindow', True)
                except: pass
            
            # Platform-specific window attributes
            if self.is_windows:
                dialog.attributes('-toolwindow', True)  # Windows-specific
            else:
                dialog.attributes('-type', 'dialog')  # Unix-specific
            dialog.attributes('-topmost', True)
            # dialog.transient(self.window)
            # dialog.grab_set()
            
            # Set size and position
            window_width = 300
            window_height = 200
            screen_width = dialog.winfo_screenwidth()
            screen_height = dialog.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # Message label
            label = self.ctk.CTkLabel(dialog, text="Type 'RESET' to confirm clearing all data:", 
                               font=self.ctk.CTkFont(size=14))
            label.pack(pady=20)
            
            # Entry field
            entry = self.ctk.CTkEntry(dialog)
            entry.pack(pady=10)
            entry.focus_set()
            
            def confirm():
                if (entry.get() == "RESET"):
                    dialog.destroy()
                    self.reset_all_data()
                else:
                    self.show_error_message("Please type 'RESET' exactly to confirm")
                    entry.focus_set()

            def cancel():
                dialog.destroy()
            
            # Buttons frame
            button_frame = self.ctk.CTkFrame(dialog)
            button_frame.pack(pady=10)
            
            # Buttons
            confirm_btn = self.ctk.CTkButton(button_frame, fg_color="darkred", text="Confirm", hover_color="red", command=confirm)
            confirm_btn.pack(side="left", padx=10)
            
            cancel_btn = self.ctk.CTkButton(button_frame, text="Cancel", command=cancel)
            cancel_btn.pack(side="left", padx=10)
            
            # Bind enter and escape
            dialog.bind("<Return>", lambda e: confirm())
            dialog.bind("<Escape>", lambda e: cancel())
            
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Error in reset confirmation: {e}{Style.RESET_ALL}")

    def reset_all_data(self):
        """Reset all application data with proper cleanup"""
        try:
            if (reset_app_data()):
                self.habits = []
                self.logs = []
                self.streaks = {}
                
                # Re-load settings from disk (reset to DEFAULTS)
                self.settings = load_settings()

                # Close the settings window if it's open
                if hasattr(self, 'settings_window') and self.settings_window and self.settings_window.winfo_exists():
                    try:
                        self.settings_window.destroy()
                    except:
                        pass

                self.settings_window = None

                # Apply appearance or other settings again
                self.change_appearance_mode(self.settings.get("appearance_mode", "System"))

                # Disable navigation buttons since we have no habits
                self.logs_button.configure(state="disabled")
                self.stats_button.configure(state="disabled")
                
                # Clear any open message windows
                if (hasattr(self, 'message_window') and (self.message_window is not None)):
                    try:
                        self.message_window.window.destroy()
                    except:
                        pass
                    self.message_window = None
                
                # Show success message before changing view
                self.show_success_message("All data has been reset\n\nPlease Wait...")
                
                # Use after to ensure message is shown before view change
                self.window.after(2100, self.show_setup_view)

                # Ensure the main window has focus after reset
                self.window.focus_force()
            else:
                self.show_error_message("Failed to reset data")
        except Exception as e:
            self.show_error_message(f"Error resetting data: {str(e)}")

    def change_appearance_mode(self, new_mode: str):
        """
        Change the app’s theme (Light/Dark/System) and save to settings.json.
        This function intentionally closes the settings window to prevent UI instability
        during the global theme change, ensuring the settings button remains responsive.
        """
        try:
            # 1. Update settings and save them to disk immediately.
            self.current_appearance_mode = new_mode
            self.settings['appearance_mode'] = new_mode
            save_settings(self.settings)

            # 2. Check if the settings window exists and is valid. If so, destroy it.
            #    This is the crucial step to prevent a stale reference and instability.
            if hasattr(self, 'settings_window') and self.settings_window and self.settings_window.winfo_exists():
                self.settings_window.destroy()
            
            # 3. It's good practice to also clear the reference after destroying.
            self.settings_window = None

            # 4. Define the function to apply the theme change.
            def apply_theme():
                if new_mode.lower() == "system":
                    import darkdetect
                    system_theme = darkdetect.theme()
                    self.ctk.set_appearance_mode(system_theme.lower() if system_theme else "light")
                else:
                    self.ctk.set_appearance_mode(new_mode.lower())
                
                # Refresh the main window to ensure all widgets are redrawn correctly.
                self.window.update_idletasks()
        
            # 5. Schedule the theme change to happen after a short delay.
            #    This ensures the settings window has fully closed before redrawing the entire UI.
            self.window.after(50, apply_theme)

        except Exception as e:
            self.show_error_message(f"Failed to change theme: {str(e)}")

    def change_autosave_interval(self, new_interval_str: str):
        """Updates the auto-save interval based on user selection."""
        try:
            # 1. Get the integer value from the display string
            new_interval = self.autosave_map.get(new_interval_str)
            if new_interval is None:
                # Fallback if something goes wrong, though this is unlikely
                self.show_error_message(f"Unknown interval: {new_interval_str}")
                return

            # 2. Update the instance attribute used by the autosave loop
            self.autosave_interval = new_interval

            # 3. Update the settings dictionary
            self.settings['autosave_interval'] = new_interval

            # 4. Save the settings to disk for persistence
            save_settings(self.settings)

            # 5. Notify the user of the successful change
            # We add a small delay to ensure this message appears over the settings window
            # without causing instability.
            def show_msg():
                 self.show_success_message(f"Auto-save set to {new_interval_str.lower()}")

            self.window.after(100, show_msg)

        except Exception as e:
            self.show_error_message(f"Failed to set interval: {str(e)}")

    def _toggle_daily_reminders(self):
        """Toggles the daily reminder setting and saves it."""
        self.daily_reminder_enabled = self.enable_reminder_checkbox.get()
        self.settings["daily_reminder_enabled"] = self.daily_reminder_enabled
        save_settings(self.settings)
        self.show_success_message(f"Daily reminders {'enabled' if self.daily_reminder_enabled else 'disabled'}")
        if self.daily_reminder_enabled:
            # If enabling, immediately try to schedule the next reminder
            self._schedule_daily_reminder()
        else:
            # If disabling, reset the last reminder date to avoid immediate pop-up if re-enabled later today
            self._last_reminder_date = None


    def _set_reminder_time(self, new_time_str):
        """Sets the reminder time and saves it."""
        if new_time_str == "Select Time":
            # Don't set if it's the placeholder
            return

        # Basic validation for HH:MM format
        try:
            datetime.strptime(new_time_str, "%H:%M")
            self.reminder_time = new_time_str
            self.settings["reminder_time"] = self.reminder_time
            save_settings(self.settings)
            self.show_success_message(f"Reminder time set to {self.reminder_time}")
            # Reschedule reminder with new time
            self._schedule_daily_reminder()
        except ValueError:
            self.show_error_message("Invalid time format. Please use HH:MM.")
            # Reset option menu to previous valid value or placeholder
            self.reminder_time_optionmenu.set(self.reminder_time if self.reminder_time else "Select Time")

    def _set_chart_style(self, style: str):
        """Sets the chart style preference and saves it."""
        self.chart_style = style
        self.settings["chart_style"] = self.chart_style
        save_settings(self.settings)
        self.show_success_message(f"Chart style set to '{self.chart_style}'")

    def _toggle_streak_annotations(self):
        """Toggles whether streak annotations are shown on plots and saves it."""
        self.show_streak_annotations = self.show_annotations_checkbox.get()
        self.settings["show_streak_annotations"] = self.show_streak_annotations
        save_settings(self.settings)
        self.show_success_message(f"Streak annotations {'enabled' if self.show_streak_annotations else 'disabled'}")

    def _set_chart_date_range(self, date_range: str):
        """Sets the default chart date range and saves it."""
        self.chart_date_range = date_range
        self.settings["chart_date_range"] = self.chart_date_range
        save_settings(self.settings)
        self.show_success_message(f"Default chart range set to '{self.chart_date_range}'")

    def _schedule_daily_reminder(self):
        """
        Schedules the daily habit reminder.
        This function checks if a reminder needs to be shown and schedules itself
        to run periodically or for the next day.
        """
        # Cancel any previous schedules to avoid multiple reminders
        if hasattr(self, '_reminder_job_id') and self._reminder_job_id:
            try:
                self.window.after_cancel(self._reminder_job_id)
            except ValueError:
                pass # Job might have already run or been cancelled

        if not self.daily_reminder_enabled:
            print(f"{Fore.LIGHTYELLOW_EX}Daily reminders are disabled. Not scheduling.{Style.RESET_ALL}")
            return

        if not self.reminder_time or self.reminder_time == "Select Time":
            print(f"{Fore.LIGHTYELLOW_EX}Reminder time not set. Not scheduling.{Style.RESET_ALL}")
            return

        now = datetime.now()
        today_date = now.strftime('%Y-%m-%d')

        # Check if habits for today are already logged
        habits_completed_today = False
        for habit in self.habits:
            log_found = next((log for log in self.logs if log[0] == habit and log[1] == today_date and log[2]), None)
            if log_found:
                habits_completed_today = True
                break
        
        # Check if reminder already sent for today
        reminder_already_sent = (self._last_reminder_date == today_date)

        target_time_str = self.reminder_time.split(":")
        target_hour = int(target_time_str[0])
        target_minute = int(target_time_str[1])
        
        target_datetime = datetime(now.year, now.month, now.day, target_hour, target_minute, 0)

        if now >= target_datetime and not reminder_already_sent and not habits_completed_today:
            # It's reminder time, and reminder hasn't been sent, and habits not yet logged
            self._show_reminder_popup()
            self._last_reminder_date = today_date # Mark reminder as sent for today
            print(f"{Fore.LIGHTGREEN_EX}Reminder popped up for {today_date} at {self.reminder_time}{Style.RESET_ALL}")
            
            # Schedule for next day's reminder
            next_day_target = target_datetime + timedelta(days=1)
            delay_ms = (next_day_target - now).total_seconds() * 1000
            if delay_ms < 0: # Should not happen if logic is correct, but safety
                delay_ms = 60 * 1000 # Default to 1 minute to re-evaluate
            self._reminder_job_id = self.window.after(int(delay_ms), self._schedule_daily_reminder)
            print(f"{Fore.LIGHTCYAN_EX}Next reminder scheduled for {next_day_target.strftime('%Y-%m-%d %H:%M')}{Style.RESET_ALL}")

        else:
            # Calculate delay until next check or reminder time
            if now < target_datetime:
                # Target time is in the future today
                delay_seconds = (target_datetime - now).total_seconds()
                print(f"{Fore.LIGHTBLUE_EX}Scheduling reminder for later today: {target_datetime.strftime('%H:%M')}{Style.RESET_ALL}")
            elif now >= target_datetime and (reminder_already_sent or habits_completed_today):
                # Target time has passed, but reminder already sent or habits logged, schedule for next day
                next_day_target = target_datetime + timedelta(days=1)
                delay_seconds = (next_day_target - now).total_seconds()
                print(f"{Fore.LIGHTBLUE_EX}Reminder already sent/habits logged. Scheduling for next day: {next_day_target.strftime('%Y-%m-%d %H:%M')}{Style.RESET_ALL}")
            else: # Fallback to a periodic check if logic is somehow missed (e.g., small negative delay)
                delay_seconds = 60 # Check again in 1 minute

            delay_ms = max(1000, int(delay_seconds * 1000)) # Minimum 1 second delay
            self._reminder_job_id = self.window.after(delay_ms, self._schedule_daily_reminder)
            print(f"{Fore.LIGHTCYAN_EX}Reminder re-check scheduled in {int(delay_seconds / 60)} minutes ({int(delay_seconds)} seconds){Style.RESET_ALL}")


    def _show_reminder_popup(self):
        """Displays a pop-up window as a daily habit reminder."""
        # Use MessageWindow, similar to success/error messages
        message = "Time to track your habits for today!"
        
        # Check if any habits are defined before showing reminder
        if not self.habits:
            message = "You have no habits configured yet.\nSet them up to start tracking!"
            
        # Ensure the popup is not shown multiple times quickly
        if hasattr(self, '_current_reminder_popup') and self._current_reminder_popup and self._current_reminder_popup.window.winfo_exists():
            return # A reminder is already active

        # Make the reminder pop-up more noticeable and persistent
        self._current_reminder_popup = MessageWindow(
            self.window,
            title="Daily Habit Reminder!",
            message=message,
            duration=0, # Make it stay until user closes
            on_close=lambda: setattr(self, '_current_reminder_popup', None) # Clear reference when closed
        )

        # Add a "Go to Habits" button if habits exist
        if self.habits:
            go_to_habits_button = self.ctk.CTkButton(
                self._current_reminder_popup.window,
                text="Go to Habits",
                command=lambda: [self._current_reminder_popup.destroy(), self.show_habits_view()]
            )
            go_to_habits_button.pack(pady=10)

        # Set specific styling for the reminder
        self._current_reminder_popup.window.configure(fg_color=("lightblue", "#3A3A5A")) # Light blue/dark blue
        self._current_reminder_popup.window.children["!ctklabel"].configure(text_color=("black", "white"))

        # Add a close button if the duration is 0
        close_button = self.ctk.CTkButton(
            self._current_reminder_popup.window,
            text="Dismiss",
            command=self._current_reminder_popup.destroy
        )
        close_button.pack(pady=5)
        self._current_reminder_popup.window.update_idletasks() # Force update to calculate proper size

    def open_settings_window(self):
        print("Attempting to open settings window")
        # If already open, bring to front
        try:
            if self.settings_window and self.settings_window.winfo_exists():
                print("Settings window exists, bringing to front")
                self.settings_window.lift()
                self.settings_window.focus_force()
                return
        except:
            # settings_window is stale or invalid
            print("Settings window is invalid, creating new one")
            self.settings_window = None


        print("Creating new settings window")
        self.settings_window = CTkToplevel(self.window)
        
        self.remove_window_icon(self.settings_window)

        self.settings_window.title("Settings")
        self.settings_window.geometry("400x450")
        self.settings_window.resizable(False, False)

        # --- START: Insert CTkScrollableFrame here ---
        # This frame will contain all the settings options and will handle scrolling
        settings_scroll_frame = self.ctk.CTkScrollableFrame(
            self.settings_window,
            fg_color="transparent" # Makes the scrollable frame background transparent
        )
        # Pack the scrollable frame to fill the entire settings window
        settings_scroll_frame.pack(fill="both", expand=True, padx=20, pady=20) # Add some padding around the scrollable area
        settings_scroll_frame.grid_columnconfigure(0, weight=1) # Allow content to expand horizontally within the scroll frame
        # --- END: Insert CTkScrollableFrame here ---

        self.settings_window.transient(self.window)
        self.settings_window.lift()
        self.settings_window.focus_force()

        # — Appearance —
        CTkLabel(settings_scroll_frame, text="Appearance Mode").pack(pady=(15, 5))
        self.settings_appearance_option = CTkOptionMenu(
            settings_scroll_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode
        )
        self.settings_appearance_option.pack(pady=(0, 15))
        self.settings_appearance_option.set(self.current_appearance_mode)

        # --- Notification / Reminder Preferences ---
        CTkLabel(settings_scroll_frame, text="Reminder Preferences", font=self.ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        
        # Enable Daily Reminders Checkbox
        self.enable_reminder_checkbox = self.ctk.CTkCheckBox(
            settings_scroll_frame,
            text="Enable Daily Reminders",
            variable=tk.BooleanVar(value=self.daily_reminder_enabled),
            command=self._toggle_daily_reminders
        )
        self.enable_reminder_checkbox.pack(padx=20, pady=5, anchor="w")

        # Reminder Time Option Menu
        time_options = [f"{h:02d}:00" for h in range(24)] # 00:00 to 23:00
        time_options.insert(0, "Select Time") # Placeholder
        
        self.reminder_time_optionmenu = self.ctk.CTkOptionMenu(
            settings_scroll_frame,
            values=time_options,
            command=self._set_reminder_time,
            fg_color=("gray80", "gray20"),
            button_color=("gray60", "gray40"),
            button_hover_color=("gray50", "gray50"),
            text_color=("gray10", "gray90")
        )
        # Set current value or placeholder
        if self.reminder_time in time_options:
            self.reminder_time_optionmenu.set(self.reminder_time)
        else:
            self.reminder_time_optionmenu.set("Select Time") # Default placeholder
        self.reminder_time_optionmenu.pack(padx=20, pady=5, fill="x")

        # --- Chart / Visualization Settings ---
        self.ctk.CTkLabel(settings_scroll_frame, text="Visualization Settings", font=self.ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        
        # Chart Style Option Menu
        self.ctk.CTkLabel(settings_scroll_frame, text="Chart Type:").pack(padx=20, pady=(5,0), anchor="w")
        self.chart_style_optionmenu = self.ctk.CTkOptionMenu(
            settings_scroll_frame,
            values=["Line Plot", "Bar Chart"],
            command=self._set_chart_style,
            fg_color=("gray80", "gray20"),
            button_color=("gray60", "gray40"),
            button_hover_color=("gray50", "gray50"),
            text_color=("gray10", "gray90")
        )
        self.chart_style_optionmenu.set(self.chart_style)
        self.chart_style_optionmenu.pack(padx=20, pady=5, fill="x")

        # Show Streak Annotations Checkbox
        self.show_annotations_checkbox = self.ctk.CTkCheckBox(
            settings_scroll_frame,
            text="Show Streak Annotations",
            variable=tk.BooleanVar(value=self.show_streak_annotations),
            command=self._toggle_streak_annotations
        )
        self.show_annotations_checkbox.pack(padx=20, pady=5, anchor="w")

        # Chart Date Range Option Menu
        self.ctk.CTkLabel(settings_scroll_frame, text="Default Date Range:").pack(padx=20, pady=(5,0), anchor="w")
        self.chart_date_range_optionmenu = self.ctk.CTkOptionMenu(
            settings_scroll_frame,
            values=["Last 7 Days", "Last 30 Days", "All Time"],
            command=self._set_chart_date_range,
            fg_color=("gray80", "gray20"),
            button_color=("gray60", "gray40"),
            button_hover_color=("gray50", "gray50"),
            text_color=("gray10", "gray90")
        )
        self.chart_date_range_optionmenu.set(self.chart_date_range)
        self.chart_date_range_optionmenu.pack(padx=20, pady=5, fill="x")

        # — Auto-save —
        CTkLabel(settings_scroll_frame, text="Auto-save Interval").pack(pady=(15, 5))
        autosave_options = list(self.autosave_map.keys())
        self.settings_autosave_option = CTkOptionMenu(
            settings_scroll_frame,
            values=autosave_options,
            command=self.change_autosave_interval
        )
        self.settings_autosave_option.pack(pady=(0, 15))
        # Set the current value from settings
        current_interval_str = self.autosave_map_rev.get(self.autosave_interval, "30 seconds")
        self.settings_autosave_option.set(current_interval_str)
        # -----------------------------

        # — Data & Maintenance —
        CTkButton(
            settings_scroll_frame,
            text="Open Data Folder",
            command=self._open_data_dir
        ).pack(fill="x", padx=20, pady=5)

        CTkButton(
            settings_scroll_frame,
            text="Clear Tracking History",
            fg_color="gray20",
            border_width=3,
            border_color=("gray40", "gray60"),
            hover_color="darkred",
            command=self.confirm_clear_logs
        ).pack(fill="x", padx=20, pady=5)

        CTkButton(
            settings_scroll_frame,
            text="RESET ALL",
            fg_color="darkred",
            hover_color="red",
            command=self.show_reset_confirmation
        ).pack(fill="x", padx=20, pady=5)

        # — License —
        CTkButton(
            settings_scroll_frame,
            text="View License",
            hover_color="yellow4",
            command=self.show_license_dialog
        ).pack(fill="x", padx=20, pady=(15, 20))


    def run(self):
        """Enhanced run method with error handling"""
        try:
            self.window.mainloop()
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Error in GUI mainloop: {e}{Style.RESET_ALL}")
            try:
                self.window.destroy()
            except:
                pass

    def clear_main_frame(self):
        """Clear main frame and recycle all widgets"""
        for widget in self.main_frame.winfo_children():
            widget_type = type(widget)
            if isinstance(widget, self.ctk.CTkCheckBox):
                self._recycle_widget(widget, self._checkbox_pool)
            elif isinstance(widget, self.ctk.CTkLabel):
                self._recycle_widget(widget, self._label_pool)
            elif isinstance(widget, self.ctk.CTkButton):
                self._recycle_widget(widget, self._button_pool)
            elif isinstance(widget, self.ctk.CTkFrame):
                self._recycle_widget(widget, self._frame_pool)
            else:
                widget.destroy()  # Destroy non-recyclable widgets

    def show_view(self, view_method):
        """Generic optimized view switching method"""
        try:
            # Disable window updates during transition
            self.window.update_idletasks()
            
            # Hide main frame during transition to prevent flickering
            self.main_frame.grid_remove()
            
            # Clear existing widgets efficiently
            self._clear_widgets_efficiently()
            
            # Show new view
            view_method()
            
            # Show main frame and update
            self.main_frame.grid()
            
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Error switching view: {e}{Style.RESET_ALL}")
            self.show_error_message(f"Error switching view: {str(e)}")
            
    def _clear_widgets_efficiently(self):
        """Clear widgets efficiently using batched operations"""
        try:
            # Get all children once
            children = self.main_frame.winfo_children()
            
            # Sort widgets by type for efficient recycling
            for widget in children:
                try:
                    if isinstance(widget, self.ctk.CTkCheckBox):
                        self._recycle_widget(widget, self._checkbox_pool)
                    elif isinstance(widget, self.ctk.CTkLabel):
                        self._recycle_widget(widget, self._label_pool)
                    elif isinstance(widget, self.ctk.CTkButton):
                        self._recycle_widget(widget, self._button_pool)
                    elif isinstance(widget, self.ctk.CTkFrame):
                        self._recycle_widget(widget, self._frame_pool)
                    else:
                        widget.destroy()
                except tk.TclError:
                    # Widget already destroyed
                    continue
                    
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Error clearing widgets: {e}{Style.RESET_ALL}")
            
    def _recycle_widget(self, widget, pool):
        """Add a widget to the recycling pool with error handling"""
        try:
            widget.pack_forget()
            widget.grid_forget()
            widget.place_forget()
            pool.append(widget)
        except tk.TclError:
            # Widget already destroyed or invalid
            pass
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Error recycling widget: {e}{Style.RESET_ALL}")

    def _get_recycled_widget(self, pool, widget_type, parent, **kwargs):
        """Get a widget from the recycling pool or create a new one with optimized configuration"""
        try:
            if pool:
                widget = pool.pop()
                try:
                    # Batch configure widget properties
                    config_updates = {}
                    for key, value in kwargs.items():
                        config_updates[key] = value
                    if config_updates:
                        widget.configure(**config_updates)
                    return widget
                except tk.TclError:
                    # Widget invalid, create new one
                    pass
                    
            # Create new widget if none available in pool
            return widget_type(parent, **kwargs)
            
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Error getting recycled widget: {e}{Style.RESET_ALL}")
            # Fallback to creating new widget
            return widget_type(parent, **kwargs)

    def _show_setup_view(self):
        """Show the initial setup view with proper validation"""
        self.clear_main_frame()
        
        # Create main container frame that will hold everything
        main_container = self.ctk.CTkFrame(self.main_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)  # Make habits section expandable
        
        # Top section (Welcome messages)
        top_frame = self.ctk.CTkFrame(main_container, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew")
        
        welcome = self.ctk.CTkLabel(
            top_frame, 
            text="Welcome to HERALDEXX HABIT TRACKER!",
            font=self.ctk.CTkFont(size=24, weight="bold")
        )
        welcome.pack(pady=(0, 20))
        
        intro = self.ctk.CTkLabel(
            top_frame,
            text="Let's set up your daily habits to track.",
            font=self.ctk.CTkFont(size=16)
        )
        intro.pack()
        
        # Middle section (Habits setup)
        habits_section = self.ctk.CTkFrame(main_container, fg_color="transparent")
        habits_section.grid(row=1, column=0, sticky="nsew", pady=20)
        habits_section.grid_columnconfigure(0, weight=1)
        habits_section.grid_rowconfigure(1, weight=1)  # Make scrollable frame expandable
        
        # Number of habits selection
        num_frame = self.ctk.CTkFrame(habits_section, fg_color="transparent")
        num_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.ctk.CTkLabel(num_frame, text="Number of habits (2-10):").pack(side="left", padx=10)
        
        self.num_habits_var = tk.StringVar(value="2")
        num_habits = self.ctk.CTkOptionMenu(
            num_frame,
            values=[str(i) for i in range(2, 11)],
            variable=self.num_habits_var
        )
        num_habits.pack(side="left", padx=10)
        
        # Scrollable frame for habits
        scroll_container = self.ctk.CTkFrame(habits_section)
        scroll_container.grid(row=1, column=0, sticky="nsew", padx=50)
        scroll_container.grid_columnconfigure(0, weight=1)
        scroll_container.grid_rowconfigure(0, weight=1)
        
        self.habits_input_frame = self.ctk.CTkScrollableFrame(scroll_container)
        self.habits_input_frame.pack(fill="both", expand=True)
        
        self.habit_entries = []
        self.update_habit_entries()
        if self.habit_entries:
            self.habit_entries[0].focus_set()
        # Bottom section (Start button and copyright)
        bottom_frame = self.ctk.CTkFrame(main_container, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        bottom_frame.grid_columnconfigure(0, weight=1)
        
        # Save button with validation - made larger and more prominent
        save_button = self.ctk.CTkButton(
            bottom_frame,
            text="Start Tracking",
            command=self.save_initial_habits,
            font=self.ctk.CTkFont(size=16, weight="bold"),
            width=200,
            height=50
        )
        save_button.grid(row=0, column=0, pady=(0, 10))
        
        # Copyright with proper styling - now in bottom frame
        from habit_engine.__init__ import __copyright__
        copyright = self.ctk.CTkLabel(
            bottom_frame,
            text=__copyright__,
            font=self.ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        copyright.grid(row=1, column=0, pady=(0, 5))
        
        # Connect number selection to entry updates
        self.num_habits_var.trace_add("write", lambda *args: self.update_habit_entries())
        
    def update_habit_entries(self):
        """Update habit entry fields when number changes with enhanced error handling"""
        try:
            # Get current entries before clearing
            current_values = {}
            if (hasattr(self, 'habit_entries')):
                for i, entry in enumerate(self.habit_entries):
                    try:
                        if (hasattr(entry, 'get')):
                            current_values[i] = entry.get().strip()
                    except tk.TclError:
                        continue

            # Clear existing entries
            for widget in self.habits_input_frame.winfo_children():
                try:
                    widget.destroy()
                except tk.TclError:
                    continue
            self.habit_entries.clear()
            
            # Create new entries with validation
            num = int(self.num_habits_var.get())
            for i in range(num):
                try:
                    row = self.ctk.CTkFrame(self.habits_input_frame, fg_color="transparent")
                    row.pack(pady=5, fill="x")
                    
                    # Label with proper font configuration
                    label = self.ctk.CTkLabel(
                        row, 
                        text=f"Habit #{i+1}:",
                        font=self.ctk.CTkFont(size=14, weight="bold"),
                        text_color=("gray10", "gray90")
                    )
                    label.pack(side="left", padx=10)
                    
                    # Entry with robust configuration
                    entry = self.ctk.CTkEntry(
                        row,
                        width=300,
                        height=35,  # Increased height for better visibility
                        placeholder_text="Enter habit name (max 50 chars)",
                        border_width=2,
                        corner_radius=8,
                        font=self.ctk.CTkFont(size=13)
                    )
                    entry.pack(side="left", padx=10, fill="x", expand=True)

                    # Restore previous value if it exists
                    if (i in current_values):
                        entry.insert(0, current_values[i])
                    
                    entry.bind('<KeyRelease>', 
                            lambda e, idx=i: self.debounced_validate_habit_entry(e, idx))
                    entry.bind('<Return>', lambda e, idx=i: self._focus_next_entry(idx))

                    self.habit_entries.append(entry)
                except Exception as e:
                    print(f"{Fore.LIGHTRED_EX}Error creating entry {i}: {e}{Style.RESET_ALL}")
                    continue

        except Exception as e:
            self.show_error_message(f"Error updating habit entries: {str(e)}")
            print(f"{Fore.LIGHTRED_EX}Error in update_habit_entries: {e}{Style.RESET_ALL}")

    def _focus_next_entry(self, index):
        """Move focus to the next habit entry when Enter is pressed"""
        try:
            if index + 1 < len(self.habit_entries):
                next_entry = self.habit_entries[index + 1].focus_set()
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Error focusing next habit entry: {e}{Style.RESET_ALL}")


    def validate_habit_entry(self, event, index):
        """Validate habit entry as user types with robust error handling"""
        try:
            entry = event.widget
            if (not hasattr(entry, 'get')):
                return False

            value = entry.get().strip() if (entry.get()) else ""
            
            # Check length
            if (len(value) > 50):
                entry.delete(50, tk.END)
                if (hasattr(entry, 'configure')):
                    try:
                        entry.configure(border_color=("red", "darkred"))
                    except tk.TclError:
                        pass
                self.show_error_message("Habit name must be under 50 characters")
                entry.focus_set()
                return False
                
            else:
                # Reset border when empty
                if (hasattr(entry, 'configure')):
                    try:
                        entry.configure(border_color=("gray60", "gray30"))
                    except tk.TclError:
                        pass
                    
            return True
            
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Error in habit entry validation: {e}{Style.RESET_ALL}")
            return False
            
    def save_initial_habits(self):
        """Save initial habits with validation"""
        try:
            habits = [entry.get().strip().title() for entry in self.habit_entries if entry.get().strip()]
            
            # Validation
            if (not all(habits)):
                self.show_error_message("Please fill in all habit names")
                # Focus the *first* empty habit‐Entry
                for entry in self.habit_entries:
                    if not entry.get().strip():
                        entry.focus_set()
                        break
                return
            
            if (len(set(habits)) != len(habits)):
                self.show_error_message("Each habit must be unique")
                # Focus the *first* duplicate
                seen = set()
                for entry in self.habit_entries:
                    val = entry.get().strip()
                    if val in seen:
                        entry.focus_set()
                        break
                    seen.add(val)
                return
                
            if (any(len(habit) > 50 for habit in habits)):
                self.show_error_message("All habits must be under 50 characters")
                # Focus the *first* Entry whose text length > 50
                for entry in self.habit_entries:
                    if len(entry.get().strip()) > 50:
                        entry.focus_set()
                        break
                return
            
            # Save habits
            if (self._save_habits(habits)):
                self.habits = habits
                # Enable navigation buttons now that we have habits
                self.habits_button.configure(state="normal")
                self.logs_button.configure(state="normal")
                self.stats_button.configure(state="normal")
                self.show_success_message("Habits saved successfully!\n\nPlease Wait...")
                self.after_success_action(lambda: self.show_habits_view())
            else:                
                self.show_error_message("Failed to save habits")
                
        except Exception as e:
            self.show_error_message(f"Error saving habits: {str(e)}")
            entry.focus_set()

    def _visualize(self, logs, habit_name):
        """Create visualization using the habit_visualization module"""
        try:
            # Call the visualization function from habit_visualization with both required parameters
            return self._visualize_fn(logs, habit_name)
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Error in visualization: {e}{Style.RESET_ALL}")
            return None