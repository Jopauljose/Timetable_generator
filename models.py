class School:
    def __init__(self, classes, faculties):
        self.classes = classes
        self.faculties = faculties
    def get_classes(self):
        return self.classes
    def get_faculties(self):
        return self.faculties
    

class Faculty:
    def __init__(self, name, subjects):
        self.name = name
        self.subjects = subjects
        self.classes = []
        self.isfree_score = {}  # Will store availability scores for each day and hour
        self.timetable = {}     # Will store the faculty's schedule
        
    def add_class(self, class_name):
        self.classes.append(class_name)
        
    def get_classes(self):
        return self.classes
        
    def get_name(self):
        return self.name
        
    def get_subjects(self):
        return self.subjects
    
class Class:
    def __init__(self, name, subjects):
        self.name = name
        self.subjects = subjects
        self.timetable = {}
        self.faculties = {}  # Map subjects to faculties

    def get_name(self):
        return self.name
        
    def get_subject(self, faculty):
        # Find the subject taught by this faculty
        for subject, assigned_faculty in self.faculties.items():
            if assigned_faculty == faculty:
                return subject
        return None


class Subject:
    def __init__(self, name, credits):
        self.name = name
        self.credits = credits
    
    def get_name(self):
        return self.name
        
    def get_credits(self):
        return self.credits

class Hour:
    def __init__(self, subject, faculty):
        self.subject = subject
        self.faculty = faculty
        
    def get_subject(self):
        return self.subject
        
    def set_subject(self, subject):
        self.subject = subject
        
    def get_faculty(self):
        return self.faculty
    
    def __str__(self):
        return f"{self.subject.get_name()} - {self.faculty.get_name()}"

class Labs(Subject):
    def __init__(self, name, credits, labslots=2):
        super().__init__(name, credits)
        self.number_of_lab_slots = labslots
        
    def get_labslots(self):
        return self.number_of_lab_slots


