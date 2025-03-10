# Timetable Generator Configuration

# Time settings
HOURS_PER_DAY = 9  # Total number of periods including breaks
DAYS_PER_WEEK = 5
WORKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

# School day timing
SCHOOL_DAY_START = "8:45"  
SCHOOL_DAY_END = "15:45"   

# Break configurations - breaks will be automatically positioned
BREAKS = [
    {"name": "Morning Break", "duration_minutes": 10},
    {"name": "Lunch Break", "duration_minutes": 45},
    {"name": "Evening Break", "duration_minutes": 10},
]

# Define actual time slots for each hour
TIME_SLOTS = {
    1: "8:00-8:50",
    2: "8:55-9:45",
    3: "9:50-10:40",
    4: "10:45-11:35",  # Morning break
    5: "11:40-12:30",
    6: "12:35-13:25",  # Lunch break 
    7: "13:30-14:20",
    8: "14:25-15:15",
    9: "15:20-16:10"
}

# Faculty constraints
MAX_HOURS_PER_DAY = 5  # Maximum teaching hours per day for a faculty
MIN_FRESHNESS_SCORE = 2  # Minimum faculty freshness score to teach

# Break slots (these will be dynamically calculated but we keep the structure)
BREAK_SLOTS = {
    'morning_break': (3, 3),  # Will be overridden by calculated values
    'lunch_break': (5, 5)     # Will be overridden by calculated values
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
    'max_iterations': 10000000, # Maximum number of iterations before giving up
    'randomize_order': True   # Randomize subject/faculty order during assignment
}