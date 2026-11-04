"""B2: independent HTTP scenarios; the promotion clock is fixed for reproducibility."""

import json
from datetime import date
from unittest.mock import patch

from django.test import SimpleTestCase

from orders import views


class OrderApiTests(SimpleTestCase):
    def setUp(self):
        views.ORDERS.clear()
        self.addCleanup(views.ORDERS.clear)
        clock = self.enterContext(patch("orders.pricing.date", wraps=date))
        clock.today.return_value = date(2026, 6, 1)
        self.payload = {
            "items": [{"name": "Pizza", "price": 12.5, "quantity": 2}],
            "distance": 5,
            "weight": 2,
            "hour": 15,
            "dayOfWeek": "tuesday",
        }

    def post(self, path, payload):
        return self.client.post(path, json.dumps(payload), content_type="application/json")

    def simulate(self, **changes):
        return self.post("/orders/simulate", {**self.payload, **changes})

    def test_should_simulate_normal(self):
        response = self.simulate()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 28)

    def test_should_simulate_promo(self):
        response = self.simulate(promoCode="BIENVENUE20")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["discount"], 5)

    def test_should_reject_simulation_expired_promo(self):
        response = self.simulate(promoCode="ETE2020")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_should_reject_simulation_empty_cart(self):
        response = self.simulate(items=[])
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_should_reject_simulation_out_of_zone(self):
        response = self.simulate(distance=15)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_should_reject_simulation_closed(self):
        response = self.simulate(hour=23)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_should_simulate_surge(self):
        response = self.simulate(hour=20, dayOfWeek="friday")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["deliveryFee"], 5.4)

    def test_should_not_save_simulation(self):
        self.simulate()
        self.assertEqual(views.ORDERS, {})

    def test_should_create_order(self):
        response = self.post("/orders", self.payload)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["id"])
        self.assertEqual(response.json()["total"], 28)

    def test_should_retrieve_created_order(self):
        created = self.post("/orders", self.payload).json()
        response = self.client.get("/orders/" + created["id"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), created)

    def test_should_allocate_unique_ids(self):
        first = self.post("/orders", self.payload).json()
        second = self.post("/orders", self.payload).json()
        self.assertNotEqual(first["id"], second["id"])

    def test_should_reject_invalid_creation(self):
        response = self.post("/orders", {**self.payload, "items": []})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_should_not_save_invalid_creation(self):
        self.post("/orders", {**self.payload, "distance": 15})
        self.assertEqual(views.ORDERS, {})

    def test_should_return_unknown_order(self):
        response = self.client.get("/orders/missing")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())

    def test_should_return_complete_order(self):
        created = self.post("/orders", self.payload).json()
        response = self.client.get("/orders/" + created["id"])
        self.assertEqual(set(response.json()), {"id", "subtotal", "discount", "deliveryFee", "surge", "total"})

    def test_should_preserve_saved_order(self):
        created = self.post("/orders", self.payload).json()
        self.simulate(promoCode="BIENVENUE20")
        self.assertEqual(self.client.get("/orders/" + created["id"]).json(), created)

    def test_should_validate_promo(self):
        response = self.post("/promo/validate", {"promoCode": "BIENVENUE20", "subtotal": 50})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["valid"])
        self.assertEqual(response.json()["total"], 40)
        self.assertEqual(views.ORDERS, {})

    def test_should_reject_expired_promo(self):
        response = self.post("/promo/validate", {"promoCode": "ETE2020", "subtotal": 50})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["valid"])
        self.assertIn("error", response.json())

    def test_should_reject_promo_below_minimum(self):
        response = self.post("/promo/validate", {"promoCode": "BIENVENUE20", "subtotal": 5})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["valid"])
        self.assertIn("error", response.json())

    def test_should_reject_unknown_promo(self):
        response = self.post("/promo/validate", {"promoCode": "NOPE", "subtotal": 50})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["valid"])
        self.assertIn("error", response.json())

    def test_should_reject_missing_promo(self):
        response = self.post("/promo/validate", {"subtotal": 50})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["valid"])
        self.assertIn("error", response.json())

    def test_should_reject_invalid_promo_amount(self):
        response = self.post("/promo/validate", {"promoCode": "BIENVENUE20", "subtotal": -1})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["valid"])
        self.assertIn("error", response.json())

    def test_should_reject_array_simulation(self):
        response = self.post("/orders/simulate", [])
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_should_reject_null_creation(self):
        response = self.post("/orders", None)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_should_reject_array_promo(self):
        response = self.post("/promo/validate", [])
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_should_reject_broken_json(self):
        response = self.client.post("/orders/simulate", "{", content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_should_reject_nan(self):
        response = self.simulate(distance=float("nan"))
        self.assertEqual(response.status_code, 400)

    def test_should_reject_wrong_methods(self):
        for path in ["/orders", "/orders/simulate", "/promo/validate"]:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 405)
