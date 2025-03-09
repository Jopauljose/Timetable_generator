from models import Class, Faculty, School, Subject, Labs, Hour
import random
import tkinter as tk
from tkinter import ttk
import copy
from config import (
    HOURS_PER_DAY,
    DAYS_PER_WEEK,
    WORKDAYS,
    MAX_HOURS_PER_DAY,
    MIN_FRESHNESS_SCORE,
    BREAK_SLOTS,
    LAB_CONSTRAINTS,
    GUI_SETTINGS,
    BACKTRACK_SETTINGS
)

# Define subjects with credits determining weekly hours
math = Subject("Mathematics", 5)     
physics = Subject("Physics", 5)
chemistry = Subject("Chemistry", 5)    
english = Subject("English", 4)
biology = Subject("Biology", 5)       
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
    """Generate timetable for a class with backtracking"""
    
    # Initialize empty timetable
    for day in WORKDAYS:
        class_obj.timetable[day] = [None] * HOURS_PER_DAY
        
        # Set break slots - same for each day
        class_obj.timetable[day][BREAK_SLOTS['morning_break'][0]] = "BREAK"
        class_obj.timetable[day][BREAK_SLOTS['lunch_break'][0]] = "BREAK"
    
    # Track which days have labs scheduled
    days_with_labs = set()
    
    # Track how many times each lab subject has been scheduled
    lab_subjects_scheduled = {
        subject.get_name(): 0 for subject in class_obj.subjects 
        if isinstance(subject, Labs)
    }
    
    def backtrack_timetable(day_idx=0, hour=0):
        # Base case: completed timetable
        if day_idx >= len(WORKDAYS):
            return True
        
        day = WORKDAYS[day_idx]
        
        # Move to next day if all hours are filled for this day
        if hour >= HOURS_PER_DAY:
            return backtrack_timetable(day_idx + 1, 0)
        
        # Skip slots that are already filled (breaks)
        if class_obj.timetable[day][hour] is not None:
            return backtrack_timetable(day_idx, hour + 1)
        
        # Try to schedule a subject for this hour
        subjects_to_try = list(class_obj.faculties.keys())
        random.shuffle(subjects_to_try)  # Try different orders
        
        for subject in subjects_to_try:
            faculty = class_obj.faculties[subject]
            
            # Check if faculty is available at this hour
            if check_availability_of_faculty(faculty, hour, day, school):
                # Check if subject is a lab
                if isinstance(subject, Labs):
                    # Skip if this specific lab has already been scheduled this week
                    if lab_subjects_scheduled[subject.get_name()] >= LAB_CONSTRAINTS['lab_frequency']:
                        continue
                    
                    # Other lab constraints remain the same...
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
                        if class_obj.timetable[day][h] is not None:
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
                        
                    # Move past the lab slots
                    if backtrack_timetable(day_idx, hour + slots_needed):
                        return True
                        
                    # If scheduling failed, backtrack
                    for h in range(hour, hour + slots_needed):
                        class_obj.timetable[day][h] = None
                    days_with_labs.remove(day)
                    lab_subjects_scheduled[subject.get_name()] -= 1  # Revert the lab count
                else:
                    # Regular subject (single slot)
                    class_obj.timetable[day][hour] = Hour(subject, faculty)
                    update_availability_score(faculty, hour, day)
                    
                    # Move to the next hour
                    if backtrack_timetable(day_idx, hour + 1):
                        return True
                    
                    # If scheduling next hours failed, backtrack
                    class_obj.timetable[day][hour] = None
                        
        # Couldn't find a valid subject-faculty, leave hour empty and try next hour
        class_obj.timetable[day][hour] = None  # Ensure the slot is empty
        return backtrack_timetable(day_idx, hour + 1)
    
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
    """Export timetables to text files with subject abbreviations"""
    
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
            f.write("Hour\t" + "\t".join([day_abbreviations[day] for day in WORKDAYS]) + "\n")
            
            # Data rows
            for hour in range(HOURS_PER_DAY):
                row = [f"Hour {hour+1}"]
                
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
    root.geometry("1000x700")  # Made taller to accommodate legend
    
    # Create a notebook (tabbed interface)
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Create a tab for each class
    for class_obj in school.classes:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=class_obj.get_name())
        
        # Create timetable grid
        for col, day in enumerate(WORKDAYS, start=1):
            ttk.Label(frame, text=day, font=("Arial", 10, "bold")).grid(
                row=0, column=col, padx=5, pady=5)
        
        for row in range(HOURS_PER_DAY):
            ttk.Label(frame, text=f"Hour {row+1}", font=("Arial", 10, "bold")).grid(
                row=row+1, column=0, padx=5, pady=5)
            
            for col, day in enumerate(WORKDAYS, start=1):
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
                        
                    cell = tk.Label(frame, text=text, width=10, height=2, 
                                   relief="solid", borderwidth=1, bg=bg_color,
                                   justify="center")
                    cell.grid(row=row+1, column=col, padx=2, pady=2, sticky="nsew")
        
        # Add legend frame below the timetable
        legend_frame = ttk.LabelFrame(frame, text="Legend")
        legend_frame.grid(row=HOURS_PER_DAY+2, column=0, columnspan=len(WORKDAYS)+1, 
                          padx=10, pady=10, sticky="ew")
        
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
        faculty_frame.grid(row=HOURS_PER_DAY+3, column=0, columnspan=len(WORKDAYS)+1, 
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
                    
    # Create Export Button
    ttk.Button(root, text="Export Timetables", 
               command=lambda: export_timetables(school)).pack(pady=10)
    
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
    school = School(classes, faculties)
    
    success = schedule_backtrack(school)
    
    if success:
        print("Successfully created timetables for all classes!")
        # Run the free period analysis before showing GUI
        free_periods, shortfalls, faculty_needs = analyze_free_periods(school)
        create_gui(school)
    else:
        print("Failed to create complete timetables. Try adjusting constraints.")
