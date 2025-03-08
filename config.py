# Timetable Generator Configuration

# Time settings
HOURS_PER_DAY = 7
DAYS_PER_WEEK = 5
WORKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

# Faculty constraints
MAX_HOURS_PER_DAY = 3  # Maximum teaching hours per day for a faculty
MIN_FRESHNESS_SCORE = 2  # Minimum faculty freshness score to teach

# Break slots (period number, duration)
BREAK_SLOTS = {
    'morning_break': (3, 1),  # 4th period, 1 hour duration
    'lunch_break': (5, 1)     # 6th period, 1 hour duration
}

# Lab constraints
LAB_CONSTRAINTS = {
    'max_labs_per_day': 1,    # Maximum labs per day per class
    'lab_frequency': 1,       # Each lab subject occurs once per week
    'consecutive_slots': 2     # Lab sessions require consecutive slots
}

# GUI settings
GUI_SETTINGS = {
    'window_width': 1000,
    'window_height': 600,
    'core_subject_color': "#ADD8E6",  # Light blue
    'lab_subject_color': "#FFCCCB",   # Light red
    'other_subject_color': "#90EE90", # Light green
    'break_color': "#FFD700",         # Gold
    'free_period_color': "#FFFFFF"    # White
}

# Backtracking settings
BACKTRACK_SETTINGS = {
    'max_iterations': 1000,   # Maximum number of iterations before giving up
    'randomize_order': True   # Randomize subject/faculty order during assignment
}