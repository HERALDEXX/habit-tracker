# HERALDEXX Habit Tracker v1.0.0

A simple yet powerful command-line habit tracking application that helps you build and maintain daily habits.

## Features

### 1. Dynamic Habit Setup

- Choose your own number of habits to track (minimum 2, maximum 10)
- Each habit is saved and persists between sessions
- Ability to reset and create new habits
- Completely flexible - you decide how many habits fit your lifestyle

### 2. Daily Check-ins

- Log your daily habit completion status
- Full word responses accepted: "yes"/"no" or quick "y"/"n"
- Automatic date tracking
- Visual feedback with checkmarks (✓) and crosses (✗)

### 3. Streak Tracking

- Automatically tracks streaks for each habit
- Shows streak counts with fire emoji (🔥)
- Streaks reset when habits are missed or days are skipped
- Persistent streak storage
- Accurately tracks consecutive days only

### 4. Log Management

- View complete history of habit tracking
- Clear all logs when needed
- Logs are grouped by date for easy reading
- Clean reset functionality

### 5. Command Line Options

```bash
-v-logs, --view-logs    View all tracking history
-c-logs, --clear-logs   Clear all logs and reset streaks
-r, --reset            Reset everything (habits, logs, and streaks)
```

## Usage

### 1. First Time Setup

1. Run the program for the first time
2. Choose how many habits you want to track (2-10)
3. Input your chosen number of habits
4. Each habit must be unique

### 2. Daily Check-in

1. Run the program without any arguments
2. Answer with "yes"/"no" (or "y"/"n") for each habit
3. View your progress immediately after check-in

### 3. View Progress

1. Use `-v-logs` to see your complete tracking history
2. Check your current streaks for each habit
3. Monitor your consistency over time

### 4. Reset Options

- Clear just the logs with `-c-logs`
- Complete reset with `-r` to start fresh
  - Clears all habits, logs, and streaks
  - Run the program again without arguments to set up new habits

## Technical Details

- Written in Python
- Uses file-based storage within the script itself
- No external dependencies required
- Date-aware streak calculation
- Automatic data persistence
- Clean separation of concerns in code structure

## Notes

> **Important:**
>
> - The application stores all data within the script file
> - Make sure you have write permissions in the application directory
> - Recommended to keep backup copies of your tracking data
> - Reset functionality (`-r`) provides a clean slate without prompting for new data
> - Run the program without arguments after reset to set up new habits


## Potential Future Enhancements

### 1. Data Management

- Export logs to CSV/Excel
- Backup and restore functionality
- Multiple user support

### 2. Analytics

- Success rate calculations
- Weekly/monthly reports
- Habit completion trends
- Best and worst performing habits

### 3. User Experience

- GUI interface
- Mobile app version
- Web interface
- Reminder system

### 4. Social Features

- Share progress
- Compete with friends
- Community challenges

### 5. Customization

- Dynamic habit counts
- Custom categories
- Priority levels
- Different tracking frequencies (daily/weekly/monthly)
