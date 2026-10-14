"""Unit and integration tests for utilities, validators, pricing, and HTTP routes."""

import json
from datetime import date

from django.test import Client, SimpleTestCase

from orders import views
from orders.pricing import apply_promo_code, calculate_delivery_fee, calculate_order_total, calculate_surge
from orders.utils import (
    calculate_average,
    calculate_discount,
    capitalize,
    clamp,
    group_by,
    parse_price,
    slugify,
    sort_students,
)
from orders.validators import is_valid_age, is_valid_email, is_valid_password


class UtilityTests(SimpleTestCase):
    def test_capitalize_examples(self):
        for value, expected in [("hello", "Hello"), ("WORLD", "World"), ("", ""), (None, "")]:
            with self.subTest(value=value):
                self.assertEqual(capitalize(value), expected)

    def test_average_examples(self):
        for values, expected in [([10, 12, 14], 12), ([15], 15), ([], 0), ([10, 11, 12], 11), (None, 0)]:
            with self.subTest(values=values):
                self.assertEqual(calculate_average(values), expected)

    def test_slugify_examples(self):
        for value, expected in [
            ("Hello World", "hello-world"),
            (" Spaces Everywhere ", "spaces-everywhere"),
            ("C'est l'été !", "cest-lete"),
            ("", ""),
        ]:
            with self.subTest(value=value):
                self.assertEqual(slugify(value), expected)

    def test_clamp_bounds_and_invalid_range(self):
        self.assertEqual([clamp(n, 0, 10) for n in (5, -5, 15)], [5, 0, 10])
        self.assertEqual(clamp(0, 0, 0), 0)
        with self.assertRaises(ValueError):
            clamp(1, 2, 0)

    def test_sort_students_all_specified_cases(self):
        students = [{"name": "Zoé", "grade": 12, "age": 20}, {"name": "Adam", "grade": 18, "age": 19}]
        self.assertEqual([x["grade"] for x in sort_students(students, "grade")], [12, 18])
        self.assertEqual([x["grade"] for x in sort_students(students, "grade", "desc")], [18, 12])
        self.assertEqual([x["name"] for x in sort_students(students, "name")], ["Adam", "Zoé"])
        self.assertEqual([x["age"] for x in sort_students(students, "age")], [19, 20])
        self.assertEqual(sort_students(None, "grade"), [])
        self.assertEqual(sort_students([], "grade"), [])
        sorted_students = sort_students(students, "grade")
        self.assertIsNot(sorted_students, students)
        self.assertEqual(sort_students(students, "grade"), sort_students(students, "grade", "asc"))
        with self.assertRaises(ValueError):
            sort_students(students, "height")
        with self.assertRaises(ValueError):
            sort_students(students, "age", "sideways")

    def test_parse_price_formats_and_errors(self):
        for raw in ("12.99", "12,99", "12.99 €", "€12.99", 12.99):
            self.assertEqual(parse_price(raw), 12.99)
        self.assertEqual(parse_price("gratuit"), 0)
        for raw in ("abc", -5, None):
            self.assertIsNone(parse_price(raw))

    def test_group_by_cases(self):
        people = [
            {"name": "Alice", "role": "dev"},
            {"name": "Bob", "role": "design"},
            {"name": "Charlie", "role": "dev"},
        ]
        self.assertEqual(group_by(people, "role"), {"dev": [people[0], people[2]], "design": [people[1]]})
        self.assertEqual(group_by([], "role"), {})
        self.assertEqual(group_by(None, "role"), {})
        self.assertEqual(group_by([people[0]], "role"), {"dev": [people[0]]})
        self.assertEqual(group_by(people, "missing"), {None: people})

    def test_calculate_discount_rules_and_errors(self):
        self.assertEqual(calculate_discount(100, [{"type": "percentage", "value": 10}]), 90)
        self.assertEqual(calculate_discount(20, [{"type": "fixed", "value": 5}]), 15)
        self.assertEqual(calculate_discount(30, [{"type": "buyXgetY", "buy": 3, "free": 1, "itemPrice": 10}]), 20)
        self.assertEqual(
            calculate_discount(100, [{"type": "percentage", "value": 10}, {"type": "fixed", "value": 5}]), 85
        )
        self.assertEqual(calculate_discount(5, [{"type": "fixed", "value": 10}]), 0)
        for price, rules in ((-1, []), (10, [{"type": "unknown"}]), (10, [{"type": "percentage", "value": 101}])):
            with self.assertRaises(ValueError):
                calculate_discount(price, rules)


class ValidatorTests(SimpleTestCase):
    def test_email_valid_and_invalid_examples(self):
        for email in ("user@example.com", "user.name+tag@domain.co"):
            self.assertTrue(is_valid_email(email))
        for email in ("invalid", "@domain.com", "user@", "", None):
            self.assertFalse(is_valid_email(email))

    def test_password_rules_individually(self):
        self.assertEqual(is_valid_password("Passw0rd!"), {"valid": True, "errors": []})
        self.assertEqual(len(is_valid_password("short")["errors"]), 4)
        cases = [
            ("alllowercase1!", "majuscule"),
            ("ALLUPPERCASE1!", "minuscule"),
            ("NoDigits!here", "chiffre"),
            ("NoSpecial1here", "spécial"),
        ]
        for password, expected in cases:
            with self.subTest(password=password):
                self.assertTrue(any(expected in error for error in is_valid_password(password)["errors"]))
        self.assertFalse(is_valid_password("")["valid"])
        self.assertFalse(is_valid_password(None)["valid"])

    def test_age_boundaries_and_invalid_types(self):
        for age in (25, 0, 150):
            self.assertTrue(is_valid_age(age))
        for age in (-1, 151, 25.5, "25", None, True):
            self.assertFalse(is_valid_age(age))


class PricingTests(SimpleTestCase):
    def test_delivery_fee_rules_and_boundaries(self):
        self.assertEqual(calculate_delivery_fee(2, 1), 2)
        self.assertEqual(calculate_delivery_fee(7, 3), 4)
        self.assertEqual(calculate_delivery_fee(5, 8), 4.5)
        self.assertEqual(calculate_delivery_fee(3, 5), 2)
        self.assertEqual(calculate_delivery_fee(10, 5), 5.5)
        self.assertIsNone(calculate_delivery_fee(15, 1))
        self.assertEqual(calculate_delivery_fee(0, 0), 2)
        for distance, weight in ((-1, 1), (1, -1), ("a", 1)):
            with self.assertRaises(ValueError):
                calculate_delivery_fee(distance, weight)

    def test_promo_percentage_fixed_limits_and_rejections(self):
        self.assertEqual(apply_promo_code(50, "BIENVENUE20", today=date(2026, 6, 1))["total"], 40)
        self.assertEqual(apply_promo_code(30, "FIXE5", today=date(2026, 6, 1))["total"], 25)
        self.assertEqual(
            apply_promo_code(
                5,
                "FIXE5",
                [{"code": "FIXE5", "type": "fixed", "value": 10, "minOrder": 0, "expiresAt": "2026-12-31"}],
                today=date(2026, 6, 1),
            )["total"],
            0,
        )
        self.assertEqual(
            apply_promo_code(
                20,
                "100",
                [{"code": "100", "type": "percentage", "value": 100, "expiresAt": "2026-12-31"}],
                today=date(2026, 6, 1),
            )["total"],
            0,
        )
        self.assertEqual(apply_promo_code(0, None)["discount"], 0)
        self.assertEqual(apply_promo_code(20, "")["total"], 20)
        self.assertEqual(
            apply_promo_code(
                20,
                "FIXE5",
                [{"code": "FIXE5", "type": "fixed", "value": 5, "expiresAt": "2026-06-01"}],
                today=date(2026, 6, 1),
            )["total"],
            15,
        )
        for code, amount, codes in (
            ("BAD", 20, []),
            ("FIXE5", 2, [{"code": "FIXE5", "type": "fixed", "value": 5, "minOrder": 10, "expiresAt": "2026-12-31"}]),
            ("OLD", 20, [{"code": "OLD", "type": "fixed", "value": 5, "expiresAt": "2025-01-01"}]),
        ):
            with self.assertRaises(ValueError):
                apply_promo_code(amount, code, codes, today=date(2026, 6, 1))
        with self.assertRaises(ValueError):
            apply_promo_code(-1, None)

    def test_surge_time_day_and_opening_boundaries(self):
        examples = [
            (15, "tuesday", 1),
            (12.5, "wednesday", 1.3),
            (20, "thursday", 1.5),
            (21, "friday", 1.8),
            (14, "sunday", 1.2),
        ]
        for hour, day, expected in examples:
            self.assertEqual(calculate_surge(hour, day), expected)
        self.assertEqual(calculate_surge(11.5, "monday"), 1)
        self.assertEqual(calculate_surge(19, "monday"), 1.5)
        self.assertEqual(calculate_surge(22, "friday"), 1.8)
        self.assertEqual(calculate_surge(9.99, "monday"), 0)
        self.assertEqual(calculate_surge(10, "monday"), 1)
        self.assertEqual(calculate_surge(22.01, "monday"), 0)
        for hour, day in ((25, "monday"), (12, "holiday")):
            with self.assertRaises(ValueError):
                calculate_surge(hour, day)

    def test_order_total_composition_and_invalid_orders(self):
        items = [{"name": "Pizza", "price": 12.5, "quantity": 2}]
        result = calculate_order_total(items, 5, 2)
        self.assertEqual(result, {"subtotal": 25, "discount": 0, "deliveryFee": 3, "surge": 1, "total": 28})
        promo = calculate_order_total(items, 5, 2, "BIENVENUE20", 20, "friday")
        self.assertEqual(promo["discount"], 5)
        self.assertEqual(promo["deliveryFee"], 5.4)
        self.assertEqual(promo["total"], 25.4)
        for bad_items, distance, hour in (
            ([], 2, 15),
            (items, 15, 15),
            (items, 2, 23),
            ([{"price": -1, "quantity": 1}], 2, 15),
            ([{"price": 2, "quantity": 0}], 2, 15),
        ):
            with self.assertRaises(ValueError):
                calculate_order_total(bad_items, distance, 1, hour=hour)


class OrderApiTests(SimpleTestCase):
    def setUp(self):
        self.client = Client()
        views.ORDERS.clear()
        self.payload = {
            "items": [{"name": "Pizza", "price": 12.5, "quantity": 2}],
            "distance": 5,
            "weight": 2,
            "hour": 15,
            "dayOfWeek": "tuesday",
        }

    def post_json(self, path, payload):
        return self.client.post(path, data=json.dumps(payload), content_type="application/json")

    def test_simulate_order_scenarios(self):
        response = self.post_json("/orders/simulate", self.payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 28)
        promo_payload = {**self.payload, "promoCode": "BIENVENUE20"}
        self.assertEqual(self.post_json("/orders/simulate", promo_payload).json()["discount"], 5)
        for changes in ({"promoCode": "OLD"}, {"items": []}, {"distance": 15}, {"hour": 23}):
            response = self.post_json("/orders/simulate", {**self.payload, **changes})
            self.assertEqual(response.status_code, 400)
        surge = self.post_json("/orders/simulate", {**self.payload, "hour": 20, "dayOfWeek": "friday"}).json()
        self.assertEqual(surge["deliveryFee"], 5.4)
        invalid_json = self.client.post("/orders/simulate", data="{", content_type="application/json")
        self.assertEqual(invalid_json.status_code, 400)

    def test_create_retrieve_unique_and_invalid_orders(self):
        first = self.post_json("/orders", self.payload)
        second = self.post_json("/orders", self.payload)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(self.client.get(f"/orders/{first.json()['id']}").status_code, 200)
        self.assertNotEqual(first.json()["id"], second.json()["id"])
        self.assertEqual(self.post_json("/orders", {**self.payload, "items": []}).status_code, 400)
        self.assertEqual(len(views.ORDERS), 2)

    def test_get_order_not_found_and_response_shape(self):
        self.assertEqual(self.client.get("/orders/missing").status_code, 404)
        created = self.post_json("/orders", self.payload).json()
        found = self.client.get(f"/orders/{created['id']}").json()
        self.assertEqual(set(found), {"id", "subtotal", "discount", "deliveryFee", "surge", "total"})

    def test_promo_validation_success_and_failures(self):
        valid = self.post_json("/promo/validate", {"promoCode": "BIENVENUE20", "subtotal": 50})
        self.assertEqual(valid.status_code, 200)
        self.assertEqual(valid.json()["total"], 40)
        expired = self.post_json("/promo/validate", {"promoCode": "ETE2020", "subtotal": 50})
        self.assertEqual(expired.status_code, 400)
        below_min = self.post_json("/promo/validate", {"promoCode": "BIENVENUE20", "subtotal": 5})
        self.assertEqual(below_min.status_code, 400)
        unknown = self.post_json("/promo/validate", {"promoCode": "NOPE", "subtotal": 50})
        self.assertEqual(unknown.status_code, 404)
        missing = self.post_json("/promo/validate", {"subtotal": 50})
        self.assertEqual(missing.status_code, 400)
        self.assertEqual(self.post_json("/promo/validate", {}).status_code, 400)
