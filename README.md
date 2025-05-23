# HERALDEXX Habit Tracker v2.1.1

A modular Python application for tracking daily habits and maintaining streaks.

## What's New

**v2.1.0 → v2.1.1**

- Minor bug fixes
- CI builds for macOS and Linux
- Single-executable distribution for all platforms

[See All Changes](https://github.com/HERALDEXX/habit-tracker/compare/v2.1.0...v2.1.1)

## ⚡ Quick Start

> 💡 **Note:** This app is written in pure Python and the source code is cross-platform (Windows, macOS, Linux).  
> ✅ Pre-built binaries are available for **Windows, macOS & Linux**

### 🔹 For Regular Users

#### Windows

1. Download `heraldexx-habit-tracker-v2.1.1.exe` from [Release v2.1.1](https://github.com/HERALDEXX/habit-tracker/releases/tag/v2.1.1)
2. Double-click to run
3. Follow the prompts to set up your habits

#### Linux

1. Download `heraldexx-habit-tracker-v2.1.1-linux` from [Release v2.1.1](https://github.com/HERALDEXX/habit-tracker/releases/tag/v2.1.1)
2. Open terminal in download location
3. Run: `chmod +x heraldexx-habit-tracker-v2.1.1-linux`
4. Run: `./heraldexx-habit-tracker-v2.1.1-linux`
5. Follow the prompts to set up your habits

#### macOS

1. Download `heraldexx-habit-tracker-v2.1.1-macos` from [Release v2.1.1](https://github.com/HERALDEXX/habit-tracker/releases/tag/v2.1.1)
2. Open terminal in download location
3. Run: `chmod +x heraldexx-habit-tracker-v2.1.1-macos`
4. Run: `./heraldexx-habit-tracker-v2.1.1-macos`
5. Follow the prompts to set up your habits

> ⚠️ Keep the generated `data/` folder next to the executable for your logs, streaks, and visualizations to be saved.

### 👨‍💻 For Developers (Cross-Platform)

1. Download the **Cross-Platform Source Code (zip)** from [Releases Page](https://github.com/HERALDEXX/habit-tracker/releases/tag/v2.1.1) (do **not** download the `.exe`)
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
├── main.py           # Main entry point
├── requirements.txt  # Python dependencies
├── .github/         # GitHub specific configurations
│   └── workflows/   # GitHub Actions CI/CD workflows
│       └── build.yml # Cross-platform build configuration
├── data/            # Data storage directory
│   ├── habits.json  # Stores habit definitions
│   ├── logs.json    # Stores daily completion logs
│   ├── streaks.json # Stores habit streaks
│   └── plots/       # Generated visualization plots
└── habit_engine/    # Core functionality package
    ├── __init__.py             # Package initialization
    ├── habit_setup.py          # Initial setup functionality
    ├── habit_io.py            # File I/O operations
    ├── habit_logic.py         # Core habit tracking logic
    ├── habit_display.py       # Display and UI functions
    └── habit_visualization.py  # Data visualization
```

## 🖥️ Command Line Usage

Besides regular interactive mode, you can use these command line options. Replace `EXECUTABLE` with:

- Windows: `heraldexx-habit-tracker-v2.1.1.exe`
- Linux: `./heraldexx-habit-tracker-v2.1.1-linux`
- macOS: `./heraldexx-habit-tracker-v2.1.1-macos`
- Source code: `python main.py`

### Show these command line options and app info

```bash
EXECUTABLE -i
```

### or

```bash
EXECUTABLE --info
```

### View your habit completion logs and streaks

```bash
EXECUTABLE -v-logs
```

### or

```bash
EXECUTABLE --view-logs
```

### Clear all tracking data (logs, streaks, and plots) while keeping habits

```bash
EXECUTABLE -c-logs
```

### or

```bash
EXECUTABLE --clear-logs
```

### Reset everything (habits, logs, streaks, and plots)

```bash
EXECUTABLE -r
```

### or

```bash
EXECUTABLE --reset
```

### Create visualization plots for your habit streaks

```bash
EXECUTABLE -p
```

### or

```bash
EXECUTABLE --plot
```

### Developer mode: Make core files editable

```bash
EXECUTABLE --dev
```

### Lock core files (after development)

```bash
EXECUTABLE --lock
```

> 📝 **Note:** For Linux and macOS users, you may need to make the file executable first:
>
> ```bash
> # For Linux
> chmod +x heraldexx-habit-tracker-v2.1.1-linux
>
> # For macOS
> chmod +x heraldexx-habit-tracker-v2.1.1-macos
> ```

## 🔒 Development Workflow

When making changes to the codebase:

1. Unlock files for development:

### Windows
```bash
python main.py --dev
```
### Linux/macOS
```bash
./main.py --dev
```

2. Make your changes to the code

3. Lock files before committing:

### Windows
```bash
python main.py --lock
```
### Linux/macOS
```bash
./main.py --lock
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
