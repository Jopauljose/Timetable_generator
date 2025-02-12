from models import Class, Faculty, School, Subject,Labs
from scheduler import TimeTableScheduler





#creating subjects with their credits

subjects = [
    Subject("Mathematics", 4),
    Subject("Physics", 4),
    Subject("Chemistry", 4),
    Subject("Biology", 3),
    Subject("Computer Science", 4),
    Subject("English", 3),
    Subject("History", 2),
    Subject("Geography", 2),
    Subject("Physical Education", 2),
    Subject("Art", 2),
    Subject("Music", 2),
    Subject("Economics", 3),
    Subject("Literature", 3),
    Subject("Foreign Language", 3),
    Subject("Environmental Science", 2),
    Labs(
        "Physics ",4,2
    ),
    Labs(
        "Chemistry ",4,2
    ),
    Labs(
        "Computer",4,2
    )
]
Faculties = [
    Faculty("Faculty 1", [subjects[0], subjects[1], subjects[2], subjects[3]]),               # 4 subjects
    Faculty("Faculty 2", [subjects[4], subjects[5]]),                                           # 2 subjects
    Faculty("Faculty 3", [subjects[6], subjects[7], subjects[8], subjects[9]]),                   # 4 subjects
    Faculty("Faculty 4", [subjects[10], subjects[11], subjects[12], subjects[13], subjects[14]]),   # 5 subjects
    # 3 subjects
Faculty("Faculty 6", [subjects[2], subjects[5], subjects[8], subjects[11], subjects[15]]),    # 5 subjects
Faculty("Faculty 7", [subjects[1], subjects[3], subjects[5], subjects[7], subjects[16]]),     # 5 subjects
Faculty("Faculty 8", [subjects[0], subjects[2], subjects[4], subjects[6], subjects[17]]),     # 5 subjects
Faculty("Faculty 9", [subjects[9], subjects[11], subjects[13], subjects[15]]),                # 4 subjects
Faculty("Faculty 10", [subjects[8], subjects[10], subjects[12], subjects[14], subjects[16]]), # 5 subjects
Faculty("Faculty 11", [subjects[1], subjects[4], subjects[7], subjects[10], subjects[17]]),   # 5 subjects
Faculty("Faculty 12", [subjects[2], subjects[6], subjects[9], subjects[12], subjects[15]]),   # 5 subjects
Faculty("Faculty 13", [subjects[3], subjects[8], subjects[11], subjects[14], subjects[16]]),  # 5 subjects
Faculty("Faculty 14", [subjects[0], subjects[5], subjects[10], subjects[13], subjects[17]]),  # 5 subjects
Faculty("Faculty 15", [subjects[1], subjects[6], subjects[11], subjects[14], subjects[15]]),  # 5 subjects
Faculty("Faculty 16", [subjects[2], subjects[7], subjects[12], subjects[16]]),               # 4 subjects
    Faculty("Lab Faculty 1", [subjects[15], subjects[16], subjects[17]]),     
    Faculty("Lab Faculty 2", [subjects[15], subjects[16], subjects[17]]),  
    Faculty("Lab Faculty 3", [subjects[15], subjects[16], subjects[17]]),                     # Lab subjects
]

classes = [
    Class("Class 1", [subjects[0], subjects[1], subjects[2], subjects[3], subjects[4], subjects[15], subjects[16]]),
    Class("Class 2", [subjects[0], subjects[1], subjects[2], subjects[3], subjects[4], subjects[15], subjects[16]]),
    Class("Class 3", [subjects[5], subjects[6], subjects[7], subjects[8], subjects[16], subjects[17]]),
    Class("Class 4", [subjects[5], subjects[6], subjects[7], subjects[8], subjects[16], subjects[17]]),
    Class("Class 5", [subjects[9], subjects[10], subjects[11], subjects[12], subjects[13], subjects[15], subjects[17]]),
    Class("Class 6", [subjects[9], subjects[10], subjects[11], subjects[12], subjects[14], subjects[15], subjects[17]]),
    Class("Class 7", [subjects[0], subjects[5], subjects[10], subjects[13], subjects[14], subjects[16], subjects[17]]),
    Class("Class 8", [subjects[1], subjects[6], subjects[11], subjects[12], subjects[13], subjects[15], subjects[16]]),
    Class("Class 9", [subjects[2], subjects[7], subjects[8], subjects[9], subjects[10], subjects[16], subjects[17]]),
]

classes = [
    Class("Class 1", [subjects[0], subjects[1], subjects[2], subjects[3], subjects[4]]),         # 5 subjects
    Class("Class 2", [subjects[0], subjects[1], subjects[2], subjects[3], subjects[4]]),         # identical to Class 1
    Class("Class 3", [subjects[5], subjects[6], subjects[7], subjects[8]]),                      # 4 subjects
    Class("Class 4", [subjects[5], subjects[6], subjects[7], subjects[8]]),                      # identical to Class 3
    Class("Class 5", [subjects[9], subjects[10], subjects[11], subjects[12], subjects[13]]),      # 5 subjects
    Class("Class 6", [subjects[9], subjects[10], subjects[11], subjects[12], subjects[14]]),      # 5 subjects with a common subset to Class 5
    Class("Class 7", [subjects[0], subjects[5], subjects[10], subjects[13], subjects[14]]),      # 5 subjects
    Class("Class 8", [subjects[1], subjects[6], subjects[11], subjects[12], subjects[13]]),      # 5 subjects
    Class("Class 9", [subjects[2], subjects[7], subjects[8], subjects[9], subjects[10]]),        # 5 subjects
]
school=School(classes,Faculties)

scheduler = TimeTableScheduler(school)
scheduler.schedule_all_classes()

# Print timetables
for class_obj in school.get_classes():
    scheduler.print_timetable(class_obj)
