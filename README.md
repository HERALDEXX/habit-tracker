# HERALDEXX Habit Tracker v2.1.0

A modular Python application for tracking daily habits and maintaining streaks.

## What's New
**v2.0.0 → v2.1.0**
- Visual streak analysis with matplotlib
[See All Changes](https://github.com/HERALDEXX/habit-tracker/compare/v2.0.0...v2.1.0)

## ⚡ Quick Start

> 💡 **Note:** This app is written in pure Python and the source code is cross-platform (Windows, macOS, Linux).  
> ✅ Pre-built binary is currently available only for **Windows** for now.


### 🔹 For Regular Users (Windows Only)

1. Download `heraldexx-habit-tracker-v2.1.0.exe` from [Release v2.1.0](https://github.com/HERALDEXX/habit-tracker/releases/tag/v2.1.0)
2. Double-click to run
3. Follow the prompts to set up your habits

> ⚠️ Keep the generated `data/` folder next to the executable for your logs, streaks, and visualizations to be saved.

### 👨‍💻 For Developers (Cross-Platform)

1. Download the **Cross-Platform Source Code (zip)** from [Releases Page](https://github.com/HERALDEXX/habit-tracker/releases/tag/v2.1.0) (do **not** download the `.exe`)
2. Extract the zip file
3. Navigate to and open your terminal in the extracted folder
4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Run the program:

```bash
python main.py
```


## Features

- Track 2-10 daily habits
- Maintain streak counts for completed habits
- View habit completion logs
- Clear logs or reset all data
- Graceful error handling and data validation
- JSON-based persistent storage
- Visual streak analysis with matplotlib

## 📁 Project Structure

```
├── main.py # Main entry point
├── data/ # Data storage directory
│   ├── habits.json # Stores habit definitions
│   ├── logs.json # Stores daily completion logs
│   ├── streaks.json # Stores habit streaks
│   └── plots/ # Generated visualization plots
└── habit_engine/ # Core functionality package
    ├── __init__.py # Package initialization
    ├── habit_setup.py # Initial setup functionality
    ├── habit_io.py # File I/O operations
    ├── habit_logic.py # Core habit tracking logic
    ├── habit_display.py # Display and UI functions
    └── habit_visualization.py # Data visualization
```


🖥️ Command line options:

- `-i` or `--info`: Show application info
- `-v-logs` or `--view-logs`: View your habit logs
- `-c-logs` or `--clear-logs`: Clear all tracking data (logs, streaks, and plots) while keeping habits
- `-r` or `--reset`: Reset everything (habits, logs, streaks, and generated plots)
- `-p` or `--plot`: Visualize streaks for a specific habit
- `--dev`: Make core files editable for development/updates
- `--lock`: Make core files non-editable for protection

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

All data is stored in JSON format in the `data/` directory:

- `habits.json`: List of configured habits
- `logs.json`: List of daily habit completion logs
- `streaks.json`: Dictionary of current streaks for each habit
- `plots/`: Folder containing auto-generated visualization plots
