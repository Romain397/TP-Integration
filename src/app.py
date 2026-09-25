"""Flask application for the student directory API."""

import re

from flask import Flask, jsonify, request

from src import data

FIELDS = {"informatique", "mathématiques", "physique", "chimie"}
REQUIRED_FIELDS = {"firstName", "lastName", "email", "grade", "field"}
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)

    def validate_student(payload, current_id=None):
        if not isinstance(payload, dict):
            return None, "Le corps JSON doit être un objet."
        missing = REQUIRED_FIELDS - payload.keys()
        if missing:
            return None, f"Champs obligatoires manquants : {', '.join(sorted(missing))}."

        first_name = payload["firstName"]
        last_name = payload["lastName"]
        email = payload["email"]
        grade = payload["grade"]
        field = payload["field"]
        if not isinstance(first_name, str) or len(first_name.strip()) < 2:
            return None, "firstName doit contenir au moins 2 caractères."
        if not isinstance(last_name, str) or len(last_name.strip()) < 2:
            return None, "lastName doit contenir au moins 2 caractères."
        if not isinstance(email, str) or not EMAIL_PATTERN.fullmatch(email.strip()):
            return None, "email doit être une adresse valide."
        if any(student["email"].lower() == email.strip().lower() and student["id"] != current_id for student in data.students):
            return None, ("Cet email est déjà utilisé.", 409)
        if isinstance(grade, bool) or not isinstance(grade, (int, float)) or not 0 <= grade <= 20:
            return None, "grade doit être un nombre entre 0 et 20."
        if not isinstance(field, str) or field not in FIELDS:
            return None, "field doit être informatique, mathématiques, physique ou chimie."
        return {
            "firstName": first_name.strip(),
            "lastName": last_name.strip(),
            "email": email.strip(),
            "grade": grade,
            "field": field,
        }, None

    def parse_id(raw_id):
        if not raw_id.isdigit():
            return None
        return int(raw_id)

    @app.get("/students")
    def list_students():
        return jsonify(data.students), 200

    @app.get("/students/stats")
    def student_stats():
        by_field = {field: sum(student["field"] == field for student in data.students) for field in sorted(FIELDS)}
        average = round(sum(student["grade"] for student in data.students) / len(data.students), 2) if data.students else 0
        best = max(data.students, key=lambda student: student["grade"], default=None)
        return jsonify(
            {
                "totalStudents": len(data.students),
                "averageGrade": average,
                "studentsByField": by_field,
                "bestStudent": best,
            }
        ), 200

    @app.get("/students/search")
    def search_students():
        query = request.args.get("q", "").strip()
        if not query:
            return jsonify({"error": "Le paramètre q est obligatoire."}), 400
        lowered = query.casefold()
        results = [
            student
            for student in data.students
            if lowered in student["firstName"].casefold() or lowered in student["lastName"].casefold()
        ]
        return jsonify(results), 200

    @app.get("/students/<student_id>")
    def get_student(student_id):
        parsed_id = parse_id(student_id)
        if parsed_id is None:
            return jsonify({"error": "L'identifiant doit être un entier."}), 400
        student = next((item for item in data.students if item["id"] == parsed_id), None)
        if student is None:
            return jsonify({"error": "Étudiant introuvable."}), 404
        return jsonify(student), 200

    @app.post("/students")
    def create_student():
        student, error = validate_student(request.get_json(silent=True))
        if error:
            if isinstance(error, tuple):
                return jsonify({"error": error[0]}), error[1]
            return jsonify({"error": error}), 400
        student["id"] = data.allocate_id()
        data.students.append(student)
        return jsonify(student), 201

    @app.put("/students/<student_id>")
    def update_student(student_id):
        parsed_id = parse_id(student_id)
        if parsed_id is None:
            return jsonify({"error": "L'identifiant doit être un entier."}), 400
        existing = next((item for item in data.students if item["id"] == parsed_id), None)
        if existing is None:
            return jsonify({"error": "Étudiant introuvable."}), 404
        student, error = validate_student(request.get_json(silent=True), current_id=parsed_id)
        if error:
            if isinstance(error, tuple):
                return jsonify({"error": error[0]}), error[1]
            return jsonify({"error": error}), 400
        existing.update(student)
        return jsonify(existing), 200

    @app.delete("/students/<student_id>")
    def delete_student(student_id):
        parsed_id = parse_id(student_id)
        if parsed_id is None:
            return jsonify({"error": "L'identifiant doit être un entier."}), 400
        student = next((item for item in data.students if item["id"] == parsed_id), None)
        if student is None:
            return jsonify({"error": "Étudiant introuvable."}), 404
        data.students.remove(student)
        return jsonify({"message": "Étudiant supprimé avec succès."}), 200

    return app


app = create_app()
