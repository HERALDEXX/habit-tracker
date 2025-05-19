# HERALDEXX Habit Tracker v2.0.0

A modular Python application for tracking daily habits and maintaining streaks.

## Features

- Track 2-10 daily habits
- Maintain streak counts for completed habits
- View habit completion logs
- Clear logs or reset all data
- Graceful error handling and data validation
- JSON-based persistent storage

## Project Structure

```
habit_tracker_2.0/
├── main.py               # Main entry point
├── data/                 # Data storage directory
│   ├── habits.json      # Stores habit definitions
│   ├── logs.json        # Stores daily completion logs
│   └── streaks.json     # Stores habit streaks
└── habit_engine/        # Core functionality package
    ├── __init__.py      # Package initialization
    ├── habit_setup.py   # Initial setup functionality
    ├── habit_io.py      # File I/O operations
    ├── habit_logic.py   # Core habit tracking logic
    └── habit_display.py # Display and UI functions
```

## Usage

Run the program:

```bash
python main.py
```

Command line options:

- `-i` or `--info`: Display detailed application information
- `-v-logs` or `--view-logs`: View habit logs
- `-c-logs` or `--clear-logs`: Clear all logs
- `-r` or `--reset`: Reset everything (habits, logs, and streaks)
- `--dev`: Make core files writable for development/updates
- `--lock`: Make core files read-only after development

## Development Workflow

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

## Data Storage

All data is stored in JSON format in the `data/` directory:

- `habits.json`: List of configured habits
- `logs.json`: List of daily habit completion logs
- `streaks.json`: Dictionary of current streaks for each habit
