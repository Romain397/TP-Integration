"""B1: delivery (16), promotions (15), surge (17) and complete orders (16)."""

from datetime import date

from django.test import SimpleTestCase

from orders.pricing import apply_promo_code, calculate_delivery_fee, calculate_order_total, calculate_surge


class DeliveryTests(SimpleTestCase):
    def test_should_delivery_case_0(self):
        self.assertEqual(calculate_delivery_fee(2, 1), 2)

    def test_should_delivery_case_1(self):
        self.assertEqual(calculate_delivery_fee(7, 3), 4)

    def test_should_delivery_case_2(self):
        self.assertEqual(calculate_delivery_fee(5, 8), 4.5)

    def test_should_delivery_case_3(self):
        self.assertEqual(calculate_delivery_fee(3, 1), 2)

    def test_should_delivery_case_4(self):
        self.assertEqual(calculate_delivery_fee(10, 5), 5.5)

    def test_should_delivery_case_5(self):
        self.assertEqual(calculate_delivery_fee(2, 5), 2)

    def test_should_delivery_case_6(self):
        self.assertEqual(calculate_delivery_fee(0, 0), 2)

    def test_should_delivery_case_7(self):
        self.assertEqual(calculate_delivery_fee(6, 2), 3.5)

    def test_should_delivery_case_8(self):
        self.assertEqual(calculate_delivery_fee(10, 6), 7)

    def test_should_delivery_case_9(self):
        self.assertEqual(calculate_delivery_fee(15, 1), None)

    def test_should_reject_negative_distance(self):
        with self.assertRaises(ValueError):
            calculate_delivery_fee(-1, 1)

    def test_should_reject_negative_weight(self):
        with self.assertRaises(ValueError):
            calculate_delivery_fee(1, -1)

    def test_should_reject_string_distance(self):
        with self.assertRaises(ValueError):
            calculate_delivery_fee("a", 1)

    def test_should_reject_boolean_distance(self):
        with self.assertRaises(ValueError):
            calculate_delivery_fee(True, 1)

    def test_should_reject_nan_distance(self):
        with self.assertRaises(ValueError):
            calculate_delivery_fee(float("nan"), 1)

    def test_should_reject_infinite_weight(self):
        with self.assertRaises(ValueError):
            calculate_delivery_fee(1, float("inf"))


class PromoTests(SimpleTestCase):
    def promo(self, amount, code, codes=None):
        return apply_promo_code(amount, code, codes, today=date(2026, 6, 1))

    def test_should_promo_percentage(self):
        self.assertEqual(self.promo(50, "BIENVENUE20")["total"], 40)

    def test_should_promo_fixed(self):
        self.assertEqual(self.promo(30, "FIXE5")["total"], 25)

    def test_should_promo_minimum_equal(self):
        self.assertEqual(self.promo(15, "BIENVENUE20")["total"], 12)

    def test_should_promo_none(self):
        self.assertEqual(self.promo(0, None)["discount"], 0)

    def test_should_promo_empty(self):
        self.assertEqual(self.promo(20, "")["total"], 20)

    def test_should_promo_clamp_fixed(self):
        self.assertEqual(
            self.promo(5, "TEST", [{"code": "TEST", "type": "fixed", "value": 10, "expiresAt": "2026-06-01"}])["total"],
            0,
        )

    def test_should_promo_hundred_percent(self):
        self.assertEqual(
            self.promo(20, "TEST", [{"code": "TEST", "type": "percentage", "value": 100, "expiresAt": "2026-06-01"}])[
                "total"
            ],
            0,
        )

    def test_should_promo_expiration_today(self):
        self.assertEqual(
            self.promo(20, "TEST", [{"code": "TEST", "type": "fixed", "value": 5, "expiresAt": "2026-06-01"}])["total"],
            15,
        )

    def test_should_reject_promo_unknown(self):
        with self.assertRaises(ValueError):
            self.promo(20, "BAD", [])

    def test_should_reject_promo_below_minimum(self):
        with self.assertRaises(ValueError):
            self.promo(2, "FIXE5")

    def test_should_reject_promo_expired(self):
        with self.assertRaises(ValueError):
            self.promo(20, "ETE2020")

    def test_should_reject_promo_negative(self):
        with self.assertRaises(ValueError):
            self.promo(-1, None)

    def test_should_reject_promo_unknown_type(self):
        with self.assertRaises(ValueError):
            self.promo(20, "TEST", [{"code": "TEST", "type": "unknown", "value": 1, "expiresAt": "2026-12-31"}])

    def test_should_reject_promo_negative_value(self):
        with self.assertRaises(ValueError):
            self.promo(20, "TEST", [{"code": "TEST", "type": "percentage", "value": -20, "expiresAt": "2026-12-31"}])

    def test_should_reject_promo_non_string_code(self):
        with self.assertRaises(ValueError):
            self.promo(20, ["TEST"])


class SurgeTests(SimpleTestCase):
    def test_should_surge_case_0(self):
        self.assertEqual(calculate_surge(15, "tuesday"), 1)

    def test_should_surge_case_1(self):
        self.assertEqual(calculate_surge(12.5, "wednesday"), 1.3)

    def test_should_surge_case_2(self):
        self.assertEqual(calculate_surge(20, "thursday"), 1.5)

    def test_should_surge_case_3(self):
        self.assertEqual(calculate_surge(21, "friday"), 1.8)

    def test_should_surge_case_4(self):
        self.assertEqual(calculate_surge(20, "saturday"), 1.8)

    def test_should_surge_case_5(self):
        self.assertEqual(calculate_surge(14, "sunday"), 1.2)

    def test_should_surge_case_6(self):
        self.assertEqual(calculate_surge(11.5, "monday"), 1)

    def test_should_surge_case_7(self):
        self.assertEqual(calculate_surge(19, "monday"), 1.5)

    def test_should_surge_case_8(self):
        self.assertEqual(calculate_surge(22, "friday"), 1.8)

    def test_should_surge_case_9(self):
        self.assertEqual(calculate_surge(9.99, "monday"), 0)

    def test_should_surge_case_10(self):
        self.assertEqual(calculate_surge(10, "monday"), 1)

    def test_should_surge_case_11(self):
        self.assertEqual(calculate_surge(22.01, "monday"), 0)

    def test_should_surge_case_12(self):
        self.assertEqual(calculate_surge(13.5, "tuesday"), 1.3)

    def test_should_surge_case_13(self):
        self.assertEqual(calculate_surge(13.75, "tuesday"), 1)

    def test_should_surge_case_14(self):
        self.assertEqual(calculate_surge(9, "sunday"), 0)

    def test_should_reject_invalid_hour(self):
        with self.assertRaises(ValueError):
            calculate_surge(25, "monday")

    def test_should_reject_invalid_day(self):
        with self.assertRaises(ValueError):
            calculate_surge(12, "holiday")


class OrderTotalTests(SimpleTestCase):
    def setUp(self):
        self.items = [{"name": "Pizza", "price": 12.5, "quantity": 2}]

    def total(self, **changes):
        parameters = {
            "items": self.items,
            "distance": 5,
            "weight": 2,
            "hour": 15,
            "day_of_week": "tuesday",
            "today": date(2026, 6, 1),
        }
        parameters.update(changes)
        return calculate_order_total(**parameters)

    def test_should_compose_normal_order(self):
        self.assertEqual(self.total(), {"subtotal": 25, "discount": 0, "deliveryFee": 3, "surge": 1, "total": 28})

    def test_should_discount_only_items(self):
        self.assertEqual(self.total(promo_code="BIENVENUE20")["total"], 23)

    def test_should_surge_only_delivery(self):
        self.assertEqual(self.total(hour=20, day_of_week="friday")["total"], 30.4)

    def test_should_compose_promo_and_surge(self):
        self.assertEqual(self.total(promo_code="BIENVENUE20", hour=20, day_of_week="friday")["total"], 25.4)

    def test_should_return_required_fields(self):
        self.assertEqual(set(self.total()), {"subtotal", "discount", "deliveryFee", "surge", "total"})

    def test_should_round_order_amounts(self):
        result = self.total(items=[{"price": 0.333, "quantity": 3}])
        self.assertEqual(result["subtotal"], 1.0)
        self.assertEqual(result["total"], 4.0)

    def test_should_reject_order_empty_cart(self):
        with self.assertRaises(ValueError):
            self.total(items=[])

    def test_should_reject_order_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.total(items=[{"price": 1, "quantity": 0}])

    def test_should_reject_order_negative_price(self):
        with self.assertRaises(ValueError):
            self.total(items=[{"price": -1, "quantity": 1}])

    def test_should_reject_order_closed(self):
        with self.assertRaises(ValueError):
            self.total(hour=23)

    def test_should_reject_order_out_of_zone(self):
        with self.assertRaises(ValueError):
            self.total(distance=15)

    def test_should_reject_order_fractional_quantity(self):
        with self.assertRaises(ValueError):
            self.total(items=[{"price": 2, "quantity": 1.5}])

    def test_should_reject_order_boolean_quantity(self):
        with self.assertRaises(ValueError):
            self.total(items=[{"price": 2, "quantity": True}])

    def test_should_reject_order_boolean_price(self):
        with self.assertRaises(ValueError):
            self.total(items=[{"price": True, "quantity": 1}])

    def test_should_reject_order_nan_price(self):
        with self.assertRaises(ValueError):
            self.total(items=[{"price": float("nan"), "quantity": 1}])

    def test_should_reject_order_invalid_item(self):
        with self.assertRaises(ValueError):
            self.total(items=[None])
