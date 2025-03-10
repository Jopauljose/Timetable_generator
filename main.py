from models import Class, Faculty, School, Subject, Labs, Hour
import random
import tkinter as tk
from tkinter import ttk
from config import (
    HOURS_PER_DAY,
 TIME_SLOTS,
    
    WORKDAYS,
    MAX_HOURS_PER_DAY,
    BREAK_SLOTS,
    LAB_CONSTRAINTS,
    BACKTRACK_SETTINGS
)
from datetime import datetime, timedelta

def calculate_time_slots():
    """
    Calculate time slots based on school day start/end times and breaks.
    This function automatically distributes the available time evenly among periods.
    """
    from config import SCHOOL_DAY_START, SCHOOL_DAY_END, BREAKS, HOURS_PER_DAY
    
    # Parse start and end times
    start_time = datetime.strptime(SCHOOL_DAY_START, "%H:%M")
    end_time = datetime.strptime(SCHOOL_DAY_END, "%H:%M")
    
    # Calculate total minutes in school day
    total_minutes = (end_time - start_time).total_seconds() / 60
    
    # Calculate total break minutes
    total_break_minutes = sum(b["duration_minutes"] for b in BREAKS)
    
    # Calculate how many actual teaching periods we have (total periods - breaks)
    teaching_periods = HOURS_PER_DAY - len(BREAKS)
    
    # Calculate minutes per teaching period
    minutes_per_period = (total_minutes - total_break_minutes) / teaching_periods
    
    # Round to nearest 5 minutes for cleaner schedules
    minutes_per_period = int(5 * round(minutes_per_period / 5))
    
    print(f"School day: {SCHOOL_DAY_START}-{SCHOOL_DAY_END}, total {total_minutes} minutes")
    print(f"Teaching periods: {teaching_periods}, each {minutes_per_period} minutes")
    print(f"Breaks: {len(BREAKS)}, total {total_break_minutes} minutes")
    
    # Generate time slots
    time_slots = {}
    break_slots = {}
    
    # Start exactly at the school day start time
    current_time = start_time
    period = 1
    
    # Calculate optimal break positions based on total available teaching time
    # This ensures breaks are distributed evenly throughout the day
    available_teaching_minutes = total_minutes - total_break_minutes
    ideal_break_minutes = []
    
    for i in range(len(BREAKS)):
        # Position breaks evenly by minutes (not by periods)
        # For example, if we have 355 teaching minutes and 3 breaks,
        # we'd want breaks around the 89th, 178th, and 266th minute
        position_minutes = (available_teaching_minutes / (len(BREAKS) + 1)) * (i + 1)
        ideal_break_minutes.append(position_minutes)
    
    print(f"Ideal break positions (minutes into teaching time): {[int(m) for m in ideal_break_minutes]}")
    
    # Track teaching minutes elapsed so far
    elapsed_teaching_minutes = 0
    break_index = 0
    
    while period <= HOURS_PER_DAY:
        # Check if we should insert a break now
        if break_index < len(BREAKS) and elapsed_teaching_minutes >= ideal_break_minutes[break_index]:
            # This is a break period
            break_name = BREAKS[break_index]["name"]
            break_duration = BREAKS[break_index]["duration_minutes"]
            
            # Create break time slot with actual break duration
            break_end_time = current_time + timedelta(minutes=break_duration)
            time_slot = f"{current_time.strftime('%H:%M')}-{break_end_time.strftime('%H:%M')} ({break_name})"
            time_slots[period] = time_slot
            
            # Store the 1-indexed period number for BREAK_SLOTS
            break_slot_name = break_name.lower().replace(" ", "_")
            break_slots[break_slot_name] = (period, period)
            
            # Advance time by break duration
            current_time = break_end_time
            break_index += 1
        else:
            # Regular teaching period
            period_end_time = current_time + timedelta(minutes=minutes_per_period)
            time_slot = f"{current_time.strftime('%H:%M')}-{period_end_time.strftime('%H:%M')}"
            time_slots[period] = time_slot
            
            # Advance time by period duration and track teaching minutes
            current_time = period_end_time
            elapsed_teaching_minutes += minutes_per_period
        
        period += 1
    
    # Ensure the last period ends exactly at the school day end time
    # This may adjust the last period slightly if there's any rounding discrepancy
    last_period = max(time_slots.keys())
    last_time_str = time_slots[last_period]
    
    # Check if this is not a break period
    if "(" not in last_time_str:
        start_time_str = last_time_str.split("-")[0]
        time_slots[last_period] = f"{start_time_str}-{end_time.strftime('%H:%M')}"
        
    # Print the calculated time slots for verification
    print("\nCalculated time slots:")
    for p, ts in sorted(time_slots.items()):
        print(f"Period {p}: {ts}")
    
    print("\nCalculated break slots:")
    for name, (period, _) in break_slots.items():
        print(f"{name}: Period {period}")
    
    # Override globals with calculated values
    global TIME_SLOTS, BREAK_SLOTS
    TIME_SLOTS = time_slots
    BREAK_SLOTS = break_slots
    
    return time_slots, break_slots

# Call this function before scheduling to initialize TIME_SLOTS and BREAK_SLOTS
TIME_SLOTS, BREAK_SLOTS = calculate_time_slots()

# Define subjects with credits determining weekly hours
math = Subject("Mathematics", 4)     
physics = Subject("Physics", 4)
chemistry = Subject("Chemistry", 4)    
english = Subject("English", 4)
biology = Subject("Biology", 4)       
computer = Subject("Computer", 3)
history = Subject("History", 3)
geography = Subject("Geography", 3)

# Lab subjects with specific credit hours
physics_lab = Labs("Physics Lab", 2, 2)    # 2 credits = 2 consecutive hours once per week
chemistry_lab = Labs("Chemistry Lab", 2, 2) 
biology_lab = Labs("Biology Lab", 2, 2)
computer_lab = Labs("Computer Lab", 2, 2)

# List of subjects grouped by type
core_subjects = [math, physics, chemistry, english, biology]
non_core_subjects = [computer, history, geography]
lab_subjects = [physics_lab, chemistry_lab, biology_lab, computer_lab]

# Combined subject list
subjects = core_subjects + non_core_subjects + lab_subjects

# --- Define Faculties ---
faculties = [
    Faculty("Dr. Math1", [math]),
    Faculty("Dr. Math2", [math]),
    Faculty("Dr. Math3", [math]),
    Faculty("Dr. Phys1", [physics, physics_lab]),
    Faculty("Dr. Phys2", [physics, physics_lab]),
    Faculty("Dr. Chem1", [chemistry, chemistry_lab]),
    Faculty("Dr. Chem2", [chemistry, chemistry_lab]),
    Faculty("Dr. Chem3", [chemistry, chemistry_lab]),   
    Faculty("Dr. Bio1", [biology, biology_lab]),
    Faculty("Dr. Bio2", [biology, biology_lab]),
    Faculty("Dr. Comp", [computer, computer_lab]),
    Faculty("Dr. Comp2", [computer, computer_lab]),    # Added another computer teacher
    Faculty("Dr. Eng1", [english]),
    Faculty("Dr. Eng2", [english]),
    Faculty("Dr. Hist", [history, geography]),
    Faculty("Dr. Hist2", [history, geography])         # Added another history/geography teacher
]

# --- Define Classes with Lab Distribution ---
classes = [
    # Science Stream - Labs on different days
    Class("11-A Sci", [
        math, physics, chemistry, english,
        physics_lab,    # Will be scheduled once per week
        chemistry_lab   # Will be scheduled on a different day
    ]),
    Class("11-B Sci", [
        math, physics, chemistry, english,
        physics_lab,    # Once per week
        chemistry_lab   # Different day from physics lab
    ]),
    Class("11-C Bio", [
        math, biology, chemistry, english,
        biology_lab,    # Once per week
        chemistry_lab   # Different day from biology lab
    ]),
    # Computer Stream
    Class("11-D Comp", [
        math, computer, english, physics,
        computer_lab,   # Once per week
        physics_lab     # Different day from computer lab
    ]),
    # Humanities Stream
    Class("11-E Hum", [
        math, english, history, geography, computer,
        computer_lab    # Once per week only
    ])
]

def init_availability_scores(school):
    """Initialize availability scores for all faculties"""
    for faculty in school.get_faculties():
        faculty.isfree_score = {}
        for day in WORKDAYS:
            faculty.isfree_score[day] = [10] * HOURS_PER_DAY  # 10 is max freshness

def choose_faculty(subject,assigned_faculties):
    """
    Choose a faculty member who can teach the subject
    and hasn't been assigned to this class yet
    """
    eligible_faculties = []
    
    for faculty in faculties:
        # Check if faculty can teach this subject
        can_teach = any(subj.get_name() == subject.get_name() for subj in faculty.get_subjects())
        
        # Check if faculty already teaches in this class
        already_assigned = faculty in assigned_faculties
        
        if can_teach and not already_assigned:
            eligible_faculties.append(faculty)
    
    if eligible_faculties:
        return random.choice(eligible_faculties)
    return None

def assign_teachers_to_classes(school):
    """Assign teachers to each class with backtracking"""
    
    print("Starting teacher assignment...")
    
    def backtrack_assignment(class_index=0, subject_index=0):
        # Base case: all classes processed
        if class_index >= len(school.classes):
            return True
            
        current_class = school.classes[class_index]
        subjects_to_assign = current_class.subjects
        
        # Base case: all subjects for current class assigned
        if subject_index >= len(subjects_to_assign):
            # Move to next class
            return backtrack_assignment(class_index + 1, 0)
            
        current_subject = subjects_to_assign[subject_index]
        print(f"  Trying to assign {current_subject.get_name()} for {current_class.get_name()}")
        
        # Find eligible faculties
        eligible_faculties = []
        for faculty in school.faculties:
            can_teach = any(subj.get_name() == current_subject.get_name() for subj in faculty.get_subjects())
            already_assigned = faculty in [f for f in current_class.faculties.values()]
            
            if can_teach and not already_assigned:
                eligible_faculties.append(faculty)
        
        # Shuffle to try different faculties
        random.shuffle(eligible_faculties)
        
        # Try each eligible faculty
        for faculty in eligible_faculties:
            print(f"    Trying {faculty.get_name()} for {current_subject.get_name()}")
            
            # Tentatively assign faculty
            current_class.faculties[current_subject] = faculty
            
            # Move to next subject
            if backtrack_assignment(class_index, subject_index + 1):
                return True
                
            # If failed, backtrack
            del current_class.faculties[current_subject]
            
        print(f"  No valid faculty for {current_subject.get_name()} in {current_class.get_name()}")
        # No faculty worked for this subject
        return False
    
    # Clear any previous assignments
    for class_obj in school.classes:
        class_obj.faculties = {}
        
    # Start backtracking
    success = backtrack_assignment()
    
    # Print results for debugging
    if (success):
        print("Teacher assignment successful!")
        for class_obj in school.classes:
            print(f"\nClass: {class_obj.get_name()}")
            for subject, faculty in class_obj.faculties.items():
                print(f"  {subject.get_name()} -> {faculty.get_name()}")
    else:
        print("Teacher assignment failed.")
        
    return success

def check_availability_of_faculty(faculty, hour, day, school):
    """
    Check if faculty is available at the given hour and day
    """
    # Check if faculty is already teaching another class at this time
    for class_obj in school.classes:
        if day in class_obj.timetable and len(class_obj.timetable[day]) > hour:
            slot = class_obj.timetable[day][hour]
            # Check if slot is an Hour object (not a string like "BREAK")
            if slot and not isinstance(slot, str) and slot.get_faculty() == faculty:
                return False
    
    # Check faculty's freshness score
    if faculty.isfree_score.get(day, [10])[hour] < 2:  # Too tired
        return False
    
    # Count how many hours faculty has already taught today
    hours_today = 0
    for class_obj in school.classes:
        if day in class_obj.timetable:
            for h in range(len(class_obj.timetable[day])):
                slot = class_obj.timetable[day][h]
                # Again, check if slot is an Hour object
                if slot and not isinstance(slot, str) and slot.get_faculty() == faculty:
                    hours_today += 1
    
    # Faculty reached max hours for the day
    if hours_today >= MAX_HOURS_PER_DAY:
        return False
    
    return True

def update_availability_score(faculty, hour, day):
    """
    Update faculty's availability score after teaching a class
    """
    # Decrease score for the current hour (faculty gets tired)
    if day not in faculty.isfree_score:
        faculty.isfree_score[day] = [10] * HOURS_PER_DAY
    
    # Teaching makes faculty tired (-4 points)
    faculty.isfree_score[day][hour] -= 4
    
    # Teaching also affects adjacent hours (-2 points)
    if hour > 0:
        faculty.isfree_score[day][hour-1] -= 2
    if hour < HOURS_PER_DAY - 1:
        faculty.isfree_score[day][hour+1] -= 2

def make_timetable(class_obj, school):
    """Generate timetable with variable subject distribution across the week"""
    
    # Initialize empty timetable
    for day in WORKDAYS:
        class_obj.timetable[day] = [None] * HOURS_PER_DAY
        
        # Set break slots - same for each day
        for break_name, (break_slot, _) in BREAK_SLOTS.items():
            # Fix: Adjust from 1-indexed to 0-indexed for timetable array
            class_obj.timetable[day][break_slot - 1] = "BREAK"
    
    # Track which days have labs scheduled
    days_with_labs = set()
    
    # Track how many times each lab subject has been scheduled
    lab_subjects_scheduled = {
        subject.get_name(): 0 for subject in class_obj.subjects 
        if isinstance(subject, Labs)
    }
    
    # Track subject distribution across days
    subject_day_count = {}
    
    # Track subject positions (at which hour they appear) for each day
    subject_positions = {}
    
    for subject in class_obj.subjects:
        subject_name = subject.get_name()
        subject_day_count[subject_name] = {day: 0 for day in WORKDAYS}
        subject_positions[subject_name] = {hour: 0 for hour in range(HOURS_PER_DAY)}
    
    def get_subject_distribution_score(subject, day, hour):
        """Calculate score based on distribution (lower is better)"""
        subject_name = subject.get_name()
        score = 0
        
        # Factor 1: How many times this subject already appears on this day
        day_count = subject_day_count[subject_name][day] 
        score += day_count * 3  # Higher penalty for concentration on same day
        
        # Factor 2: How many times subject appears at this hour across all days
        position_count = subject_positions[subject_name][hour]
        score += position_count * 4  # Higher penalty for same time slot pattern
        
        # Add randomization factor to prevent predictable patterns
        score += random.randint(0, 1)
        
        return score
    
    def backtrack_timetable(day_idx=0, hour=0, iterations=0):
        # Check for excessive backtracking
        iterations += 1
        if iterations > BACKTRACK_SETTINGS['max_iterations']:
            print(f"Reached maximum iterations ({BACKTRACK_SETTINGS['max_iterations']}) for class {class_obj.get_name()}")
            return False
            
        # Base case: completed timetable
        if day_idx >= len(WORKDAYS):
            return True
        
        day = WORKDAYS[day_idx]
        
        # Move to next day if all hours are filled for this day
        if hour >= HOURS_PER_DAY:
            return backtrack_timetable(day_idx + 1, 0, iterations)
        
        # Skip slots that are already filled (breaks)
        if class_obj.timetable[day][hour] is not None:
            return backtrack_timetable(day_idx, hour + 1, iterations)
        
        # Try to schedule a subject for this hour
        subjects_to_try = list(class_obj.faculties.keys())
        
        # Sort subjects by distribution score (lower is better)
        subjects_to_try.sort(key=lambda s: get_subject_distribution_score(s, day, hour))
        
        for subject in subjects_to_try:
            faculty = class_obj.faculties[subject]
            
            if check_availability_of_faculty(faculty, hour, day, school):
                if isinstance(subject, Labs):
                    # Skip if this specific lab has already been scheduled this week
                    if lab_subjects_scheduled[subject.get_name()] >= LAB_CONSTRAINTS['lab_frequency']:
                        continue
                    
                    # Check if this day already has a lab scheduled
                    if day in days_with_labs:
                        continue  # Skip - no two labs on the same day
                    
                    # Check if we have enough consecutive slots
                    slots_needed = subject.get_labslots()
                    if hour + slots_needed > HOURS_PER_DAY:
                        continue  # Not enough hours left in the day
                    
                    # Check if any of the consecutive slots are already filled
                    slots_available = True
                    for h in range(hour, hour + slots_needed):
                        if h >= HOURS_PER_DAY or class_obj.timetable[day][h] is not None:
                            slots_available = False
                            break
                    
                    if not slots_available:
                        continue  # Skip - consecutive slots not available
                        
                    # Check if faculty is available for all consecutive slots
                    faculty_available = True
                    for h in range(hour, hour + slots_needed):
                        if not check_availability_of_faculty(faculty, h, day, school):
                            faculty_available = False
                            break
                            
                    if not faculty_available:
                        continue  # Skip - faculty not available for all slots
                        
                    # Assign lab to all consecutive slots
                    for h in range(hour, hour + slots_needed):
                        class_obj.timetable[day][h] = Hour(subject, faculty)
                        update_availability_score(faculty, h, day)
                    
                    # Mark this day as having a lab and count this lab subject
                    days_with_labs.add(day)
                    lab_subjects_scheduled[subject.get_name()] += 1
                    
                    # Update distribution tracking for all lab slots
                    for h in range(hour, hour + slots_needed):
                        subject_day_count[subject.get_name()][day] += 1
                        subject_positions[subject.get_name()][h] += 1
                        
                    # Move past the lab slots
                    if backtrack_timetable(day_idx, hour + slots_needed, iterations):
                        return True
                        
                    # If scheduling failed, backtrack
                    for h in range(hour, hour + slots_needed):
                        class_obj.timetable[day][h] = None
                        subject_day_count[subject.get_name()][day] -= 1
                        subject_positions[subject.get_name()][h] -= 1
                    
                    days_with_labs.remove(day)
                    lab_subjects_scheduled[subject.get_name()] -= 1
                else:
                    # Regular subject (single slot)
                    class_obj.timetable[day][hour] = Hour(subject, faculty)
                    update_availability_score(faculty, hour, day)
                    
                    # Update distribution tracking
                    subject_day_count[subject.get_name()][day] += 1
                    subject_positions[subject.get_name()][hour] += 1
                    
                    # Move to the next hour
                    if backtrack_timetable(day_idx, hour + 1, iterations):
                        return True
                    
                    # If scheduling next hours failed, backtrack
                    class_obj.timetable[day][hour] = None
                    subject_day_count[subject.get_name()][day] -= 1
                    subject_positions[subject.get_name()][hour] -= 1
                        
        # Couldn't find a valid subject-faculty, leave hour empty and try next hour
        class_obj.timetable[day][hour] = None
        return backtrack_timetable(day_idx, hour + 1, iterations)
    
    # Add randomization to initial assignment order for diversity
    if BACKTRACK_SETTINGS['randomize_order']:
        random.shuffle(WORKDAYS)
    
    return backtrack_timetable()

def schedule_backtrack(school):
    """Main scheduling function with backtracking"""
    
    # Initialize availability scores
    init_availability_scores(school)
    
    # First assign teachers to classes
    teacher_assignment_success = assign_teachers_to_classes(school)
    if not teacher_assignment_success:
        print("Failed to assign teachers to classes. Check faculty availability.")
        return False
    
    print("Teacher assignment successful!")
    
    # Then create timetables for each class
    for class_obj in school.classes:
        timetable_success = make_timetable(class_obj, school)
        if not timetable_success:
            print(f"Failed to create timetable for {class_obj.get_name()}")
            return False
            
    return True

def export_timetables(school):
    """Export timetables to text files with subject abbreviations and time slots"""
    
    # Create abbreviations for subjects
    subject_abbreviations = {
        "Mathematics": "MAT",
        "Physics": "PHY",
        "Chemistry": "CHM",
        "Biology": "BIO", 
        "English": "ENG",
        "Computer": "COM",
        "History": "HIS",
        "Geography": "GEO",
        "Physics Lab": "PLB",
        "Chemistry Lab": "CLB",
        "Biology Lab": "BLB",
        "Computer Lab": "CPL"  # Using CPL to avoid confusion with Chemistry Lab
    }
    
    # Create abbreviations for weekdays
    day_abbreviations = {
        "Monday": "MON",
        "Tuesday": "TUE",
        "Wednesday": "WED", 
        "Thursday": "THU",
        "Friday": "FRI"
    }
    
    for class_obj in school.classes:
        with open(f"{class_obj.get_name()}_timetable.txt", "w") as f:
            f.write(f"Timetable for {class_obj.get_name()}\n\n")
            
            # Header row with abbreviated day names
            f.write("Period\tTime\t" + "\t".join([day_abbreviations[day] for day in WORKDAYS]) + "\n")
            
            # Data rows
            for hour in range(HOURS_PER_DAY):
                # Get actual time slot from calculated values
                time_slot = TIME_SLOTS.get(hour+1, f"Period {hour+1}")
                row = [f"Period {hour+1}", time_slot]
                
                for day in WORKDAYS:
                    if day in class_obj.timetable and hour < len(class_obj.timetable[day]):
                        slot = class_obj.timetable[day][hour]
                        if slot == "BREAK":
                            row.append("BRK")  # Abbreviation for break
                        elif slot:
                            # Use abbreviation instead of full name
                            subject_name = slot.get_subject().get_name()
                            abbr = subject_abbreviations.get(subject_name, subject_name[:3].upper())
                            row.append(abbr)
                        else:
                            row.append("---")  # Empty slot
                    else:
                        row.append("---")
                        
                f.write("\t".join(row) + "\n")
            
            # Add subject-teacher assignments
            f.write("\n\nSubject Assignments:\n")
            f.write("-" * 40 + "\n")
            
            # Collect unique subject-teacher pairs
            subject_teachers = {}
            for day in WORKDAYS:
                if day in class_obj.timetable:
                    for hour_slot in class_obj.timetable[day]:
                        if hour_slot and hour_slot != "BREAK":
                            subject_name = hour_slot.get_subject().get_name()
                            teacher_name = hour_slot.get_faculty().get_name()
                            subject_teachers[subject_name] = teacher_name
            
            # Write the assignments
            for subject, teacher in sorted(subject_teachers.items()):
                abbr = subject_abbreviations.get(subject, subject[:3].upper())
                f.write(f"{subject} ({abbr}): {teacher}\n")
            
            # Add abbreviation legend
            f.write("\n\nAbbreviation Key:\n")
            f.write("-" * 40 + "\n")
            f.write("BRK: Break\n")
            f.write("---: Free Period\n")
            
            # Only include abbreviations for subjects in this class
            used_subjects = set()
            for day in WORKDAYS:
                if day in class_obj.timetable:
                    for hour_slot in class_obj.timetable[day]:
                        if hour_slot and hour_slot != "BREAK":
                            used_subjects.add(hour_slot.get_subject().get_name())
            
            # Write legend for used subjects
            for subject in sorted(used_subjects):
                abbr = subject_abbreviations.get(subject, subject[:3].upper())
                f.write(f"{abbr}: {subject}\n")
            
        print(f"Exported timetable for {class_obj.get_name()}")

# Also update the GUI to use abbreviations for consistency
def create_gui(school):
    """Create a simple GUI to display timetables with abbreviations"""
    # Import the TIME_SLOTS from config
    
    # Recreate function to regenerate timetable
    def recreate_timetable():
        # Hide current window
        root.withdraw()
        
        print("\nRecreating timetable...")
        
        # Reset school data
        for class_obj in school.get_classes():
            class_obj.timetable = {}
        
        # Reinitialize availability scores and generate new timetable
        success = schedule_backtrack(school)
        
        if success:
            print("Successfully recreated timetables!")
            # Run analysis on new timetable
            free_periods, shortfalls, faculty_needs = analyze_free_periods(school)
            
            # Close current window and create new one
            root.destroy()
            create_gui(school)
        else:
            print("Failed to recreate timetables. Try adjusting constraints.")
            # Show window again if recreation failed
            root.deiconify()
    
    # Create abbreviations for subjects
    subject_abbreviations = {
        "Mathematics": "MAT",
        "Physics": "PHY",
        "Chemistry": "CHM",
        "Biology": "BIO", 
        "English": "ENG",
        "Computer": "COM",
        "History": "HIS",
        "Geography": "GEO",
        "Physics Lab": "PLB",
        "Chemistry Lab": "CLB",
        "Biology Lab": "BLB",
        "Computer Lab": "CPL"
    }
    
    root = tk.Tk()
    root.title("Timetable Scheduler")
    root.geometry("1050x700")  # Made slightly wider for the time column
    
    # Create a notebook (tabbed interface)
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Create a tab for each class
    for class_obj in school.classes:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=class_obj.get_name())
        
        # Create timetable grid with time column
        ttk.Label(frame, text="Period", font=("Arial", 10, "bold")).grid(
            row=0, column=0, padx=5, pady=5)
        ttk.Label(frame, text="Time", font=("Arial", 10, "bold")).grid(
            row=0, column=1, padx=10, pady=5)
            
        for col, day in enumerate(WORKDAYS, start=2):
            ttk.Label(frame, text=day, font=("Arial", 10, "bold")).grid(
                row=0, column=col, padx=5, pady=5)
        
        # In the create_gui function, update the loop that creates time labels
        for row in range(HOURS_PER_DAY):
            # Show period number
            ttk.Label(frame, text=f"Period {row+1}", font=("Arial", 10)).grid(
                row=row+1, column=0, padx=5, pady=5)
                
            # Show time slot - use the actual calculated time slots
            time_text = TIME_SLOTS.get(row+1, f"Period {row+1}")
            
            # Create time label with special styling for breaks if this period is a break
            is_break_period = False
            for break_name, (break_period, _) in BREAK_SLOTS.items():
                if break_period == row + 1:  # +1 because row is 0-indexed but BREAK_SLOTS uses 1-indexed periods
                    is_break_period = True
                    break
            
            if is_break_period:
                time_label = tk.Label(frame, text=time_text, 
                                     font=("Arial", 9), width=20,
                                     bg="#FFD700")  # Gold for breaks
            else:
                time_label = ttk.Label(frame, text=time_text, font=("Arial", 9), width=20)
            
            time_label.grid(row=row+1, column=1, padx=2, pady=2)
            
            for col, day in enumerate(WORKDAYS, start=2):
                if day in class_obj.timetable and row < len(class_obj.timetable[day]):
                    slot = class_obj.timetable[day][row]
                    
                    if slot == "BREAK":
                        text = "BRK"
                        bg_color = "#FFD700"  # Gold for breaks
                    elif slot:
                        # Use abbreviation for the subject
                        subject_name = slot.get_subject().get_name()
                        abbr = subject_abbreviations.get(subject_name, subject_name[:3].upper())
                        text = abbr
                        
                        # Color coding based on subject type
                        if isinstance(slot.get_subject(), Labs):
                            bg_color = "#FFCCCB"  # Light red for labs
                        elif slot.get_subject() in core_subjects:
                            bg_color = "#ADD8E6"  # Light blue for core
                        else:
                            bg_color = "#90EE90"  # Light green for others
                    else:
                        text = "---"
                        bg_color = "#FFFFFF"  # White for free periods
                        
                    cell = tk.Label(frame, text=text, width=8, height=2, 
                                   relief="solid", borderwidth=1, bg=bg_color,
                                   justify="center")
                    cell.grid(row=row+1, column=col, padx=2, pady=2, sticky="nsew")
        
        # Add legend frame below the timetable
        legend_frame = ttk.LabelFrame(frame, text="Legend")
        legend_frame.grid(row=HOURS_PER_DAY+2, column=0, columnspan=len(WORKDAYS)+2, 
                          padx=10, pady=10, sticky="ew")
        
        # Rest of the legend code remains the same
        # Add subject abbreviations to legend
        row = 0
        col = 0
        
        # Only include subjects in this class's timetable
        used_subjects = set()
        for day in WORKDAYS:
            if day in class_obj.timetable:
                for hour_slot in class_obj.timetable[day]:
                    if hour_slot and hour_slot != "BREAK":
                        used_subjects.add(hour_slot.get_subject())
        
        # Add break and free period to the legend
        ttk.Label(legend_frame, text="BRK: Break", width=20).grid(row=row, column=col, padx=5, pady=2, sticky="w")
        col += 1
        if col >= 3:  # 3 columns in the legend
            col = 0
            row += 1
            
        ttk.Label(legend_frame, text="---: Free Period", width=20).grid(row=row, column=col, padx=5, pady=2, sticky="w")
        col += 1
        if col >= 3:
            col = 0
            row += 1
        
        # Add all subjects to the legend
        for subject in sorted(used_subjects, key=lambda s: s.get_name()):
            subject_name = subject.get_name()
            abbr = subject_abbreviations.get(subject_name, subject_name[:3].upper())
            
            ttk.Label(legend_frame, text=f"{abbr}: {subject_name}", width=20).grid(
                row=row, column=col, padx=5, pady=2, sticky="w")
            
            col += 1
            if col >= 3:  # 3 columns in the legend
                col = 0
                row += 1
        
        # Add faculty assignments frame
        faculty_frame = ttk.LabelFrame(frame, text="Faculty Assignments")
        faculty_frame.grid(row=HOURS_PER_DAY+3, column=0, columnspan=len(WORKDAYS)+2, 
                           padx=10, pady=10, sticky="ew")
        
        # Add faculty assignments to the frame
        row = 0
        col = 0
        
        for subject in sorted(used_subjects, key=lambda s: s.get_name()):
            faculty = class_obj.faculties.get(subject, None)
            if faculty:
                ttk.Label(faculty_frame, text=f"{subject.get_name()}: {faculty.get_name()}", width=25).grid(
                    row=row, column=col, padx=5, pady=2, sticky="w")
                
                col += 1
                if col >= 2:  # 2 columns for faculty assignments
                    col = 0
                    row += 1
                    
    # Create button frame with Export and Recreate buttons
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=10)
    
    # Export button
    export_btn = ttk.Button(button_frame, text="Export Timetables", 
               command=lambda: export_timetables(school))
    export_btn.pack(side="left", padx=10)
    
    # Recreate button - NEW
    recreate_btn = ttk.Button(button_frame, text="Recreate Timetable", 
                           command=recreate_timetable)
    recreate_btn.pack(side="left", padx=10)
    
    root.mainloop()

def analyze_free_periods(school):
    """Analyze free periods in the timetable and calculate faculty needs"""
    
    print("\n=== FREE PERIODS ANALYSIS ===\n")
    
    # Track overall stats
    total_free_periods = 0
    subject_shortfalls = {}  # Subject to hours needed
    
    # For each class
    for class_obj in school.classes:
        print(f"\nClass: {class_obj.get_name()}")
        free_periods = 0
        free_periods_by_day = {day: 0 for day in WORKDAYS}
        
        # Count free periods
        for day in WORKDAYS:
            for hour in range(HOURS_PER_DAY):
                # Skip break slots
                if day in class_obj.timetable and hour < len(class_obj.timetable[day]):
                    if class_obj.timetable[day][hour] is None:
                        free_periods += 1
                        free_periods_by_day[day] += 1
        
        print(f"  Total free periods: {free_periods}")
        print("  Free periods by day:")
        for day, count in free_periods_by_day.items():
            print(f"    {day}: {count}")
        
        total_free_periods += free_periods
        
        # Check subject allocation vs credit requirements
        print("  Subject allocation analysis:")
        
        # Count actual hours per subject
        actual_hours = {}
        for day in WORKDAYS:
            if day not in class_obj.timetable:
                continue
                
            for hour_slot in class_obj.timetable[day]:
                if hour_slot and hour_slot != "BREAK":
                    subject = hour_slot.get_subject()
                    actual_hours[subject.get_name()] = actual_hours.get(subject.get_name(), 0) + 1
        
        # Compare with required hours (credits)
        for subject in class_obj.subjects:
            required_hours = subject.get_credits()
            actual = actual_hours.get(subject.get_name(), 0)
            
            if required_hours > actual:
                shortfall = required_hours - actual
                print(f"    {subject.get_name()}: {actual}/{required_hours} hours (shortfall: {shortfall})")
                
                # Add to overall shortfall
                if subject.get_name() not in subject_shortfalls:
                    subject_shortfalls[subject.get_name()] = shortfall
                else:
                    subject_shortfalls[subject.get_name()] += shortfall
    
    # Calculate additional faculty needs
    print("\nOverall Statistics:")
    print(f"Total free periods across all classes: {total_free_periods}")
    print("Total subject hour shortfalls:")
    for subject, hours in subject_shortfalls.items():
        print(f"  {subject}: {hours} hours")
    
    # Calculate minimum faculty needs based on subject qualifications
    faculty_needs = {}
    for subject_name, hours_needed in subject_shortfalls.items():
        # Find how many faculties can teach this subject
        qualified_faculty = sum(1 for f in school.faculties if 
                               any(s.get_name() == subject_name for s in f.get_subjects()))

        # Consider existing qualified faculty when calculating additional needs
        # Check if existing faculty still have capacity for teaching more classes
        existing_capacity = qualified_faculty * MAX_HOURS_PER_DAY

        # Calculate minimum additional faculty needed, considering existing capacity
        if existing_capacity >= hours_needed:
            additional_faculty = 0  # Existing faculty can cover the needs
        else:
            remaining_need = hours_needed - existing_capacity
            additional_faculty = (remaining_need // MAX_HOURS_PER_DAY) + \
                                (1 if remaining_need % MAX_HOURS_PER_DAY > 0 else 0)
        
        # Store the result in the faculty_needs dictionary
        faculty_needs[subject_name] = additional_faculty

        # Add information about existing qualified faculty to output
        print(f"  {subject_name}: {hours_needed} hours needed, {qualified_faculty} qualified faculty available")
        if qualified_faculty > 0:
            print(f"    Existing capacity: {existing_capacity} hours")
    
    print("\nAdditional faculty needed to cover shortfalls:")
    for subject, count in faculty_needs.items():
        if count > 0:
            print(f"  {subject}: {count} additional faculty members")
    
    return total_free_periods, subject_shortfalls, faculty_needs

if __name__ == "__main__":
    print("Starting timetable generation...")
    # Calculate time slots based on config
    TIME_SLOTS, BREAK_SLOTS = calculate_time_slots()
    print("School day schedule:")
    for period, time in sorted(TIME_SLOTS.items()):
        print(f"Period {period}: {time}")
    
    school = School(classes, faculties)
    
    success = schedule_backtrack(school)
    
    if success:
        print("Successfully created timetables for all classes!")
        # Run the free period analysis before showing GUI
        free_periods, shortfalls, faculty_needs = analyze_free_periods(school)
        create_gui(school)
    else:
        print("Failed to create complete timetables. Try adjusting constraints.")
