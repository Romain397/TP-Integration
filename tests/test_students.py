"""Tests for the student directory API."""

import pytest


def test_list_students_returns_json_array(client):
    response = client.get("/students")
    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_list_students_returns_all_initial_students(client):
    assert len(client.get("/students").json) == 5


def test_get_existing_student(client):
    response = client.get("/students/1")
    assert response.status_code == 200
    assert response.json["firstName"] == "Ahmed"


def test_get_missing_student_returns_404(client):
    assert client.get("/students/999").status_code == 404


def test_get_non_numeric_id_returns_400(client):
    assert client.get("/students/abc").status_code == 400


def test_create_student_returns_201_and_generated_id(client, valid_student):
    response = client.post("/students", json=valid_student)
    assert response.status_code == 201
    assert response.json["id"] == 6
    assert response.json["email"] == valid_student["email"]


def test_create_student_without_required_field_returns_400(client, valid_student):
    del valid_student["email"]
    assert client.post("/students", json=valid_student).status_code == 400


@pytest.mark.parametrize("grade", [25, -1, True, "12"])
def test_create_student_with_invalid_grade_returns_400(client, valid_student, grade):
    valid_student["grade"] = grade
    assert client.post("/students", json=valid_student).status_code == 400


def test_create_student_with_duplicate_email_returns_409(client, valid_student):
    valid_student["email"] = "AHMED.BENALI@example.com"
    assert client.post("/students", json=valid_student).status_code == 409


@pytest.mark.parametrize("field,value", [
    ("firstName", "A"),
    ("lastName", "B"),
    ("email", "invalid"),
    ("field", "biologie"),
])
def test_create_student_with_invalid_field_value_returns_400(client, valid_student, field, value):
    valid_student[field] = value
    assert client.post("/students", json=valid_student).status_code == 400


def test_update_student_returns_updated_student(client, valid_student):
    response = client.put("/students/1", json=valid_student)
    assert response.status_code == 200
    assert response.json["firstName"] == "Nora"
    assert response.json["id"] == 1


def test_update_missing_student_returns_404(client, valid_student):
    assert client.put("/students/999", json=valid_student).status_code == 404


def test_update_with_another_students_email_returns_409(client, valid_student):
    valid_student["email"] = "sarah.martin@example.com"
    assert client.put("/students/1", json=valid_student).status_code == 409


def test_update_can_keep_its_own_email(client):
    student = client.get("/students/1").json
    student["grade"] = 17
    response = client.put("/students/1", json=student)
    assert response.status_code == 200
    assert response.json["grade"] == 17


def test_delete_existing_student_returns_confirmation(client):
    response = client.delete("/students/1")
    assert response.status_code == 200
    assert "message" in response.json
    assert client.get("/students/1").status_code == 404


def test_delete_missing_student_returns_404(client):
    assert client.delete("/students/999").status_code == 404


def test_stats_returns_expected_fields(client):
    response = client.get("/students/stats")
    assert response.status_code == 200
    assert set(response.json) == {"totalStudents", "averageGrade", "studentsByField", "bestStudent"}
    assert response.json["totalStudents"] == 5
    assert response.json["averageGrade"] == 16.1
    assert response.json["bestStudent"]["id"] == 5


def test_search_is_case_insensitive(client):
    response = client.get("/students/search?q=ahmed")
    assert response.status_code == 200
    assert [student["id"] for student in response.json] == [1]


@pytest.mark.parametrize("url", ["/students/search", "/students/search?q=", "/students/search?q=%20%20"])
def test_search_without_nonempty_query_returns_400(client, url):
    assert client.get(url).status_code == 400


def test_search_returns_empty_array_when_nothing_matches(client):
    response = client.get("/students/search?q=nonexistent")
    assert response.status_code == 200
    assert response.json == []
