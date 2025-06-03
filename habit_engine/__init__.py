# Habit Tracker Engine Package
# This package contains the core functionality for the Habit Tracker application.

from datetime import datetime

__version__ = "2.2.0"
__author__ = "Herald Inyang"
__description__ = "A modern Python application for tracking daily habits and maintaining streaks, featuring both CLI and GUI interfaces."
__app_name__ = "HERALDEXX HABIT TRACKER"
__copyright__ = f"Copyright © {datetime.now().year} Herald Inyang"
__license__ = "MIT"
__website__ = "https://github.com/heraldexx"
__release_date__ = "2025-06-12"

# License text for PyInstaller compatibility
__license_text__ = """MIT License

Copyright (c) 2025 Herald Inyang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

# Separate GUI and CLI features explicitly
__gui_features__ = [
    "Modern, customizable interface with Dark/Light/System themes",
    "Interactive habit setup wizard",
    "Real-time habit tracking with auto-save",
    "Visual streak indicators",
    "Detailed log history view",
    "Interactive statistics and visualizations",
    "One-click theme switching",
    "Intuitive navigation",
    "Autosave functionality",
    "In-app daily reminders and notifications",
    "Visualization/Chart customization"
]

__cli_features__ = [
    "Track 2-10 daily habits",
    "Maintain streak counts",
    "View habit completion logs",
    "Clear logs or reset data",
    "Command-line arguments support",
    "Cross-platform compatibility",
    "JSON-based persistent storage",
    "Visualization plot generation"
]

# Combined features list for backward compatibility
__features__ = __gui_features__ + __cli_features__

__credits__ = [
    "Herald Inyang (Lead Developer)",
    "EarlyFounders Academy (Training Institution)",
    "Adesua Ayomitan (Project Supervisor)"
]