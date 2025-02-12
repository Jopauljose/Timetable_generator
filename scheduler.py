from models import *
import random

class TimeTableScheduler:
    def __init__(self, school):
        self.school = school
        self.classes = school.get_classes()
        self.faculties = school.get_faculties()
        self.subject_faculty_mapping = {}
        self.faculty_schedule = {}  # Track faculty schedules

    def init_faculty_schedule(self):
        """Initialize empty schedule for each faculty"""
        for faculty in self.faculties:
            self.faculty_schedule[faculty] = {
                day: [False] * hour for day in range(len(workdays))
            }

    def is_faculty_available(self, faculty, day_index, hour):
        """Check if faculty is available at given time"""
        return not self.faculty_schedule[faculty][day_index][hour]

    def mark_faculty_schedule(self, faculty, day_index, hour, is_occupied=True):
        """Mark faculty schedule as occupied/free"""
        self.faculty_schedule[faculty][day_index][hour] = is_occupied

    def get_subject_faculty(self, subject, class_obj):
        """Get available faculty for subject"""
        key = (class_obj.get_name(), subject.get_name())
        if key not in self.subject_faculty_mapping:
            # Get all faculties that can teach this subject
            available_faculties = [f for f in self.faculties 
                                 if subject in f.get_subjects()]
            if available_faculties:
                # Choose randomly from available faculties
                self.subject_faculty_mapping[key] = random.choice(available_faculties)
        return self.subject_faculty_mapping.get(key)

    def is_consecutive_hours_valid(self, class_obj, day_idx, hour_slot, subject):
        """Check if placing subject at this slot would create > 3 consecutive hours"""
        consecutive_count = 1
        
        # Check previous hours
        h = hour_slot - 1
        while h >= 0:
            curr_slot = class_obj.Timetable[day_idx].get_hour(h)
            if curr_slot.get_subject() == subject:
                consecutive_count += 1
                if consecutive_count > 3:
                    return False
            else:
                break
            h -= 1
        
        # Check next hours
        h = hour_slot + 1
        while h < hour:
            curr_slot = class_obj.Timetable[day_idx].get_hour(h)
            if curr_slot.get_subject() == subject:
                consecutive_count += 1
                if consecutive_count > 3:
                    return False
            else:
                break
            h += 1
        
        return True

    def is_lab_subject(self, subject):
        """Check if subject is a lab"""
        return isinstance(subject, Labs)

    def find_consecutive_lab_slots(self, class_obj, subject, available_slots):
        """Find consecutive slots for lab hours"""
        lab_slots_needed = subject.numebr_of_lab_slots
        faculty = self.get_subject_faculty(subject, class_obj)
        if not faculty:
            return None
        
        # Group available slots by day
        slots_by_day = {}
        for day, hour in available_slots:
            if day not in slots_by_day:
                slots_by_day[day] = []
            slots_by_day[day].append(hour)
        
        # Find consecutive slots in each day
        for day, hours in slots_by_day.items():
            hours.sort()
            for i in range(len(hours) - lab_slots_needed + 1):
                if all(h + 1 in hours for h in hours[i:i+lab_slots_needed-1]):
                    # Check faculty availability for all consecutive slots
                    if all(self.is_faculty_available(faculty, day, h) 
                          for h in hours[i:i+lab_slots_needed]):
                        return [(day, h) for h in hours[i:i+lab_slots_needed]]
        return None

    def schedule_class(self, class_obj):
        """Schedule a class with faculty availability tracking"""
        available_slots = [(d, h) for d in range(len(workdays)) for h in range(hour)]
        
        # First schedule lab subjects
        for subject in class_obj.subjects:
            if self.is_lab_subject(subject):
                faculty = self.get_subject_faculty(subject, class_obj)
                if not faculty:
                    continue
                
                # Find consecutive slots for lab
                lab_slots = self.find_consecutive_lab_slots(class_obj, subject, available_slots)
                if lab_slots:
                    # Schedule all lab slots
                    for day_idx, hour_slot in lab_slots:
                        class_obj.Timetable[day_idx].set_hour(hour_slot, subject, faculty)
                        self.mark_faculty_schedule(faculty, day_idx, hour_slot)
                        available_slots.remove((day_idx, hour_slot))
                    
                    # Reduce remaining credits for theory classes
                    credits_to_schedule = subject.credits - subject.numebr_of_lab_slots
                    
                    # Schedule remaining theory hours
                    while credits_to_schedule > 0 and available_slots:
                        for _ in range(len(available_slots)):
                            slot_idx = random.randint(0, len(available_slots) - 1)
                            day_idx, hour_slot = available_slots[slot_idx]
                            
                            if (self.is_faculty_available(faculty, day_idx, hour_slot) and 
                                self.is_consecutive_hours_valid(class_obj, day_idx, hour_slot, subject)):
                                class_obj.Timetable[day_idx].set_hour(hour_slot, subject, faculty)
                                self.mark_faculty_schedule(faculty, day_idx, hour_slot)
                                available_slots.pop(slot_idx)
                                credits_to_schedule -= 1
                                break
        
        # Then schedule regular subjects
        for subject in class_obj.subjects:
            if self.is_lab_subject(subject):
                continue
            faculty = self.get_subject_faculty(subject, class_obj)
            if not faculty:
                continue
                
            credits_to_schedule = subject.credits
            while credits_to_schedule > 0 and available_slots:
                for _ in range(len(available_slots)):
                    slot_idx = random.randint(0, len(available_slots) - 1)
                    day_idx, hour_slot = available_slots[slot_idx]
                    
                    if (self.is_faculty_available(faculty, day_idx, hour_slot) and 
                        self.is_consecutive_hours_valid(class_obj, day_idx, hour_slot, subject)):
                        # Schedule the slot and mark faculty as occupied
                        class_obj.Timetable[day_idx].set_hour(hour_slot, subject, faculty)
                        self.mark_faculty_schedule(faculty, day_idx, hour_slot)
                        available_slots.pop(slot_idx)
                        credits_to_schedule -= 1
                        break
                else:
                    break

        # Fill any remaining empty slots
        while available_slots:
            day_idx, hour_slot = available_slots.pop()
            for subject in class_obj.subjects:
                faculty = self.get_subject_faculty(subject, class_obj)
                if (faculty and 
                    self.is_faculty_available(faculty, day_idx, hour_slot) and 
                    self.is_consecutive_hours_valid(class_obj, day_idx, hour_slot, subject)):
                    class_obj.Timetable[day_idx].set_hour(hour_slot, subject, faculty)
                    self.mark_faculty_schedule(faculty, day_idx, hour_slot)
                    break
    
    def schedule_all_classes(self):
        """Schedule all classes with faculty tracking"""
        self.init_faculty_schedule()  # Initialize faculty schedules
        for class_obj in self.classes:
            self.schedule_class(class_obj)

    def print_timetable(self, class_obj):
        """Print timetable for a class"""
        print(f"\nTimetable for {class_obj.get_name()}")
        print("=" * 100)
        header = "Hour   |"
        for day in workdays:
            header += f"{day:^19}|"
        print(header)
        print("=" * 100)
        
        for h in range(hour):
            # First line: hour and subjects
            subject_row = f"{h+1:2d}:00  |"
            # Second line: empty space and faculties
            faculty_row = "       |"
            
            for day in range(len(workdays)):
                slot = class_obj.Timetable[day].get_hour(h)
                subject = slot.get_subject()
                faculty = slot.get_faculty()
                
                if subject and faculty:
                    subject_name = f"{subject.get_name()[:15]}"
                    faculty_name = f"(F{faculty.get_name()[8:]})"  # Extract faculty number
                    subject_row += f"{subject_name:^19}|"
                    faculty_row += f"{faculty_name:^19}|"
                else:
                    subject_row += f"{'---':^19}|"
                    faculty_row += f"{'---':^19}|"
            
            print(subject_row)
            print(faculty_row)
            print("-" * 100)