"""In-memory student store and reset helpers."""

INITIAL_STUDENTS = [
    {"id": 1, "firstName": "Ahmed", "lastName": "Benali", "email": "ahmed.benali@example.com", "grade": 16.5,
     "field": "informatique"},
    {"id": 2, "firstName": "Sarah", "lastName": "Martin", "email": "sarah.martin@example.com", "grade": 18.0,
     "field": "mathématiques"},
    {"id": 3, "firstName": "Lucas", "lastName": "Bernard", "email": "lucas.bernard@example.com", "grade": 12.75,
     "field": "physique"},
    {"id": 4, "firstName": "Inès", "lastName": "Diallo", "email": "ines.diallo@example.com", "grade": 14.0,
     "field": "chimie"},
    {"id": 5, "firstName": "Emma", "lastName": "Petit", "email": "emma.petit@example.com", "grade": 19.25,
     "field": "informatique"},
]
students = []
next_id = 1


def reset_students():
    """Restore the initial dataset and return the live list."""
    global next_id
    students.clear()
    students.extend(student.copy() for student in INITIAL_STUDENTS)
    next_id = max(student["id"] for student in students) + 1
    return students


def allocate_id():
    """Return the next unique student ID."""
    global next_id
    allocated = next_id
    next_id += 1
    return allocated


reset_students()