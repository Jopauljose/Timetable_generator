hour=7
workdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']



class School:
    def __init__(self,classes, faculties):
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
        self.classes=[]
        self.isfree=[True for _ in range(hour)]
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
        self.workdays = workdays
        self.name = name
        self.subjects = subjects
        self.Timetable = [Timetable_of_Day(day) for day in self.workdays]
    def set_wordays(self,workdays):
        self.workdays = workdays
    def get_name(self):
        return self.name
    def get_subject(self):
        return self.subject
    def get_faculty(self):
        return self.faculty

class Subject:
    def __init__(self, name,credits):
        self.name = name
        self.credits = credits
    def get_name(self):
        return self.name
class Hour:
    def __init__(self,subject,faculty):
        self.subject = subject
        self.faculty = faculty
    def get_subject(self):
        return self.subject
    def set_subject(self,subject):
        self.subject = subject
    def get_faculty(self):
        return self.faculty
class Timetable_of_Day:
    def __init__(self, day):
        self.day = day
        self.hours = [Hour(None,None) for _ in range(7)]
    def get_day(self):
        return self.day
    def get_hours(self):
        return self.hours
    def set_hour(self, hour, subject, faculty):
        self.hours[hour]=Hour(subject,faculty)
        
    def get_hour(self, hour):
        return self.hours[hour]
class Labs(Subject):
    def __init__(self,name,credits,labslots=2):
        super().__init__(name,credits)
        self.numebr_of_lab_slots = labslots
