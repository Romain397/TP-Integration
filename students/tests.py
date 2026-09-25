"""Tests for the student directory API."""

from django.test import TestCase

from . import data


class StudentApiTests(TestCase):
    def setUp(self):
        data.reset_students()
        self.valid_student = {
            "firstName": "Nora",
            "lastName": "Dupont",
            "email": "nora.dupont@example.com",
            "grade": 15.5,
            "field": "physique",
        }

    def tearDown(self):
        data.reset_students()

    def test_list_students_returns_json_array(self):
        response = self.client.get("/students")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_list_students_returns_all_initial_students(self):
        self.assertEqual(len(self.client.get("/students").json()), 5)

    def test_get_existing_student(self):
        response = self.client.get("/students/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["firstName"], "Ahmed")

    def test_get_missing_student_returns_404(self):
        self.assertEqual(self.client.get("/students/999").status_code, 404)

    def test_get_non_numeric_id_returns_400(self):
        self.assertEqual(self.client.get("/students/abc").status_code, 400)

    def test_create_student_returns_201_and_generated_id(self):
        response = self.client.post("/students", self.valid_student, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["id"], 6)
        self.assertEqual(response.json()["email"], self.valid_student["email"])

    def test_create_student_without_required_field_returns_400(self):
        payload = self.valid_student.copy()
        del payload["email"]
        self.assertEqual(self.client.post("/students", payload, content_type="application/json").status_code, 400)

    def test_create_student_with_invalid_grade_returns_400(self):
        for grade in [25, -1, True, "12"]:
            with self.subTest(grade=grade):
                payload = self.valid_student | {"grade": grade}
                response = self.client.post("/students", payload, content_type="application/json")
                self.assertEqual(response.status_code, 400)

    def test_create_student_with_duplicate_email_returns_409(self):
        payload = self.valid_student | {"email": "AHMED.BENALI@example.com"}
        response = self.client.post("/students", payload, content_type="application/json")
        self.assertEqual(response.status_code, 409)

    def test_create_student_with_invalid_field_value_returns_400(self):
        for field, value in [("firstName", "A"), ("lastName", "B"), ("email", "invalid"), ("field", "biologie")]:
            with self.subTest(field=field):
                payload = self.valid_student | {field: value}
                response = self.client.post("/students", payload, content_type="application/json")
                self.assertEqual(response.status_code, 400)

    def test_update_student_returns_updated_student(self):
        response = self.client.put("/students/1", self.valid_student, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["firstName"], "Nora")
        self.assertEqual(response.json()["id"], 1)

    def test_update_missing_student_returns_404(self):
        response = self.client.put("/students/999", self.valid_student, content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_update_with_another_students_email_returns_409(self):
        payload = self.valid_student | {"email": "sarah.martin@example.com"}
        response = self.client.put("/students/1", payload, content_type="application/json")
        self.assertEqual(response.status_code, 409)

    def test_update_can_keep_its_own_email(self):
        student = self.client.get("/students/1").json()
        student["grade"] = 17
        response = self.client.put("/students/1", student, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["grade"], 17)

    def test_delete_existing_student_returns_confirmation(self):
        response = self.client.delete("/students/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertEqual(self.client.get("/students/1").status_code, 404)

    def test_delete_missing_student_returns_404(self):
        self.assertEqual(self.client.delete("/students/999").status_code, 404)

    def test_stats_returns_expected_fields(self):
        response = self.client.get("/students/stats")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.json()), {"totalStudents", "averageGrade", "studentsByField", "bestStudent"}
        )
        self.assertEqual(response.json()["totalStudents"], 5)
        self.assertEqual(response.json()["averageGrade"], 16.1)
        self.assertEqual(response.json()["bestStudent"]["id"], 5)

    def test_search_is_case_insensitive(self):
        response = self.client.get("/students/search?q=ahmed")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([student["id"] for student in response.json()], [1])

    def test_search_without_nonempty_query_returns_400(self):
        for url in ["/students/search", "/students/search?q=", "/students/search?q=%20%20"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 400)

    def test_search_returns_empty_array_when_nothing_matches(self):
        response = self.client.get("/students/search?q=nonexistent")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])