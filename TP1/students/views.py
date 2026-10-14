"""JSON views for the student directory API."""

import json
import re

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from . import data

FIELDS = {"informatique", "mathématiques", "physique", "chimie"}
REQUIRED_FIELDS = {"firstName", "lastName", "email", "grade", "field"}
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _json_body(request):
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return payload


def _validate_student(payload, current_id=None):
    if not isinstance(payload, dict):
        return None, "Le corps JSON doit être un objet.", 400
    missing = REQUIRED_FIELDS - payload.keys()
    if missing:
        return None, f"Champs obligatoires manquants : {', '.join(sorted(missing))}.", 400

    first_name = payload["firstName"]
    last_name = payload["lastName"]
    email = payload["email"]
    grade = payload["grade"]
    field = payload["field"]
    if not isinstance(first_name, str) or len(first_name.strip()) < 2:
        return None, "firstName doit contenir au moins 2 caractères.", 400
    if not isinstance(last_name, str) or len(last_name.strip()) < 2:
        return None, "lastName doit contenir au moins 2 caractères.", 400
    if not isinstance(email, str) or not EMAIL_PATTERN.fullmatch(email.strip()):
        return None, "email doit être une adresse valide.", 400
    if any(
        student["email"].casefold() == email.strip().casefold() and student["id"] != current_id
        for student in data.students
    ):
        return None, "Cet email est déjà utilisé.", 409
    if isinstance(grade, bool) or not isinstance(grade, (int, float)) or not 0 <= grade <= 20:
        return None, "grade doit être un nombre entre 0 et 20.", 400
    if not isinstance(field, str) or field not in FIELDS:
        return None, "field doit être informatique, mathématiques, physique ou chimie.", 400
    return {
        "firstName": first_name.strip(),
        "lastName": last_name.strip(),
        "email": email.strip(),
        "grade": grade,
        "field": field,
    }, None, 200


def _parse_id(raw_id):
    return int(raw_id) if raw_id.isdigit() else None


def _find_student(student_id):
    return next((student for student in data.students if student["id"] == student_id), None)


def _error(message, status):
    return JsonResponse({"error": message}, status=status)


@csrf_exempt
def students_collection(request):
    if request.method == "GET":
        return JsonResponse(data.students, safe=False)
    if request.method == "POST":
        student, error, status = _validate_student(_json_body(request))
        if error:
            return _error(error, status)
        student["id"] = data.allocate_id()
        data.students.append(student)
        return JsonResponse(student, status=201)
    return _error("Méthode non autorisée.", 405)


@csrf_exempt
def student_detail(request, raw_id):
    student_id = _parse_id(raw_id)
    if student_id is None:
        return _error("L'identifiant doit être un entier.", 400)
    student = _find_student(student_id)
    if student is None:
        return _error("Étudiant introuvable.", 404)
    if request.method == "GET":
        return JsonResponse(student)
    if request.method == "PUT":
        updated, error, status = _validate_student(_json_body(request), current_id=student_id)
        if error:
            return _error(error, status)
        student.update(updated)
        return JsonResponse(student)
    if request.method == "DELETE":
        data.students.remove(student)
        return JsonResponse({"message": "Étudiant supprimé avec succès."})
    return _error("Méthode non autorisée.", 405)


def student_stats(request):
    by_field = {field: sum(student["field"] == field for student in data.students) for field in sorted(FIELDS)}
    average = round(sum(student["grade"] for student in data.students) / len(data.students), 2) if data.students else 0
    best = max(data.students, key=lambda student: student["grade"], default=None)
    return JsonResponse(
        {"totalStudents": len(data.students), "averageGrade": average, "studentsByField": by_field, "bestStudent": best}
    )


def search_students(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return _error("Le paramètre q est obligatoire.", 400)
    lowered = query.casefold()
    results = [
        student
        for student in data.students
        if lowered in student["firstName"].casefold() or lowered in student["lastName"].casefold()
    ]
    return JsonResponse(results, safe=False)