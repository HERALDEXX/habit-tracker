# HERALDEXX Habit Tracker v2.2.0

A modern Python application for tracking daily habits and maintaining streaks, featuring both CLI and GUI interfaces.

## What's New

**v2.1.1 → v2.2.0**

> - Added modern GUI interface with customtkinter
> - Dark/Light/System theme support
> - Interactive habit setup wizard
> - Enhanced visualization and statistics
> - Real-time streak tracking
> - Updated storage location to user configuration directory for executables and clarified source code data path
> - Added in-app daily reminders and notifications
> - Autosave functionality
> - Visualization/Chart customization for better user experience

[See All Changes](https://github.com/HERALDEXX/habit-tracker/compare/v2.1.1...v2.2.0)

## ⚡ Quick Start

> 💡 **Note:** This app is written in pure Python and the source code is cross-platform (Windows, macOS, Linux).  
> ✅ Pre-built binaries are available for **Windows, macOS & Linux**

### 🔹 For Regular Users

#### Windows

1. Download `heraldexx-habit-tracker-v2.2.0.exe` from [Release v2.2.0](https://github.com/HERALDEXX/habit-tracker/releases/tag/v2.2.0)
2. Double-click to run
3. Follow the interactive setup wizard
   > ⚠️ Data is stored in `C:\Users\<username>\.heraldexx-habit-tracker\data`. Ensure this directory is preserved for your logs, streaks, and visualizations.

#### Linux

1. Download `heraldexx-habit-tracker-v2.2.0-linux` from [Release v2.2.0](https://github.com/HERALDEXX/habit-tracker/releases/tag/v2.2.0)
2. Open terminal in download location
3. Run: `chmod +x heraldexx-habit-tracker-v2.2.0-linux`
4. Run: `./heraldexx-habit-tracker-v2.2.0-linux`
5. Follow the interactive setup wizard
   > ⚠️ Data is stored in `~/.heraldexx-habit-tracker/data`. Ensure this directory is preserved for your logs, streaks, and visualizations.

#### macOS

1. Download `heraldexx-habit-tracker-v2.2.0-macos` from [Release v2.2.0](https://github.com/HERALDEXX/habit-tracker/releases/tag/v2.2.0)
2. Open terminal in download location
3. Run: `chmod +x heraldexx-habit-tracker-v2.2.0-macos`
4. Run: `./heraldexx-habit-tracker-v2.2.0-macos`
5. Follow the interactive setup wizard
   > ⚠️ Data is stored in `~/.heraldexx-habit-tracker/data`. Ensure this directory is preserved for your logs, streaks, and visualizations.

### 👨‍💻 For Developers (Cross-Platform)

1. Download the **Cross-Platform Source Code (zip)** from [Releases Page](https://github.com/HERALDEXX/habit-tracker/releases/tag/v2.2.0) (do **not** download the **executables**)
2. Extract the zip file
3. Navigate to and open your terminal in the extracted folder
4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Run the program:

```bash
python main.py        # Starts in GUI mode
python main.py --cli  # Starts in CLI mode
```

> ⚠️ Data is stored in the `data/` directory relative to `main.py`. Ensure this directory is preserved for your logs, streaks, and visualizations.

## Features

### GUI Features

- Modern, customizable interface
- Dark/Light/System theme support
- Interactive habit setup wizard
- Real-time habit tracking
- Visual streak indicators
- Detailed log history view
- Interactive statistics and visualizations
- One-click theme switching
- Intuitive navigation
- Autosave functionality
- In-app daily reminders and notifications
- Visualization/Chart customization

### CLI Features

- Track 2-10 daily habits
- Maintain streak counts
- View habit completion logs
- Clear logs or reset data
- Command-line arguments support
- Cross-platform compatibility
- JSON-based persistent storage
- Visualization plot generation
- View MIT license

## 📁 Project Structure

```
├── main.py                     # Main entry point with both GUI and CLI modes
├── requirements.txt            # Python package dependencies
├── README.md                   # Project documentation
├── .github/                    # GitHub specific configurations
│   └── workflows/             # GitHub Actions CI/CD workflows
│       └── build.yml          # Cross-platform build configuration
├── assets/                    # Application assets
│   ├── icon.ico              # Windows application icon
│   ├── icon.png              # Main application icon (for macOS/Linux)
│   └── icons/                # Icon variants for different resolutions
│       ├── icon_16.png       # 16x16 icon
│       ├── icon_32.png       # 32x32 icon
│       ├── icon_64.png       # 64x64 icon
│       ├── icon_128.png      # 128x128 icon
│       └── icon_256.png      # 256x256 icon
├── data/                      # Data storage directory
│   ├── settings.json         # User-specific settings and preferences
│   ├── habits.json           # User's configured habits
│   ├── logs.json            # Daily habit completion records
│   ├── streaks.json        # Current streak counts for each habit
│   └── plots/              # Generated visualization plots
└── habit_engine/             # Core application package
    ├── __init__.py          # Package metadata and version info
    ├── gui.py               # Modern GUI interface using customtkinter
    ├── habit_setup.py       # Initial habit configuration logic
    ├── habit_io.py          # File I/O and data persistence
    ├── habit_logic.py       # Core habit tracking algorithms
    ├── habit_display.py     # CLI display and output formatting
    └── habit_visualization.py # Data visualization and plotting
```

## 🖥️ Command Line Usage **(For Developers)**

The source code can run in either GUI or CLI mode.

### Getting Help

View all available commands and usage information:

```bash
python main.py -h
```

or

```bash
python main.py --help
```

### Mode Selection

Start in GUI mode (default):

```bash
python main.py
```

Force CLI mode:

```bash
python main.py --cli
```

### Information Commands

View help message:

```bash
python main.py -h
```

or

```bash
python main.py --help
```

Show app info and version:

```bash
python main.py -i
```

or

```bash
python main.py --info
```

View MIT license:

```bash
python main.py -l
```

or

```bash
python main.py --license
```

### Data Management

View habit completion logs and streaks:

```bash
python main.py -v-logs
```

or

```bash
python main.py --view-logs
```

Clear tracking data while keeping habits:

```bash
python main.py -c-logs
```

or

```bash
python main.py --clear-logs
```

Reset everything (habits, logs, streaks, and plots):

```bash
python main.py -r
```

or

```bash
python main.py --reset
```

### Visualization

Create habit streak visualizations:

```bash
python main.py -p
```

or

```bash
python main.py --plot
```

### Development Options

Developer mode (make core files editable):

```bash
python main.py --dev
```

Lock core files (after development):

```bash
python main.py --lock
```

### Notes

> - For executables, data is stored in `~/.heraldexx-habit-tracker/data` (Linux/macOS) or `C:\Users\<username>\.heraldexx-habit-tracker\data` (Windows).
> - For source code, data is stored in `data/` relative to `main.py`.
> - Visualizations are saved in the `plots/` subdirectory of the data directory.
> - Use GUI mode for the best interactive experience
> - CLI mode is ideal for automation and scripting

> 📝 **Note:** For Linux and macOS users, you may need to make the file executable first:
>
> ```bash
> # For Linux
> chmod +x heraldexx-habit-tracker-v2.2.0-linux
> ```
>
> ```bash
> # For macOS
> chmod +x heraldexx-habit-tracker-v2.2.0-macos
> ```

## 🔒 Development Workflow

When making changes to the codebase:

1. Unlock files for development:

```bash
python main.py --dev
```

2. Make your changes to the code

3. Lock files before committing:

```bash
python main.py --lock
```

4. Push your changes:

```bash
git add .
git commit -m "Your commit message"
git push
```

This ensures that files are always pushed in their protected (read-only) state.

## 💾 Data Storage

> All data is stored in JSON format in the data directory:
>
> - For executables: `~/.heraldexx-habit-tracker/data` (Linux/macOS) or `C:\Users\<username>\.heraldexx-habit-tracker\data` (Windows)
> - For source code: `data/` directory relative to `main.py`
>
> The data directory contains:
>
> - `settings.json`: User-specific settings and preferences
> - `habits.json`: List of configured habits
> - `logs.json`: List of daily habit completion logs
> - `streaks.json`: Dictionary of current streaks for each habit
> - `plots/`: Folder containing auto-generated visualization plots

## 🎨 Themes

> The application supports three theme modes:
>
> - Light Mode: Optimized for bright environments
> - Dark Mode: Easy on the eyes in low-light conditions
> - System Mode: Automatically matches your system preferences
>
> Switch between themes using the dropdown menu in the sidebar.

## 📄 License

> This project is licensed under the MIT License. You can view the license text:
>
> - In GUI mode: Click 'View License' button in the Statistics view
> - In CLI mode: Use the `-l` or `--license` option
> - Or read the LICENSE file in the source code project root
