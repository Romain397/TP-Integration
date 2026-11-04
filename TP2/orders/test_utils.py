"""A1 and A4-A7: independently discovered examples, boundaries and regressions."""

from django.test import SimpleTestCase

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


class UtilityTests(SimpleTestCase):
    def test_should_capitalize_lowercase(self):
        self.assertEqual(capitalize("hello"), "Hello")

    def test_should_capitalize_uppercase(self):
        self.assertEqual(capitalize("WORLD"), "World")

    def test_should_capitalize_empty(self):
        self.assertEqual(capitalize(""), "")

    def test_should_capitalize_null(self):
        self.assertEqual(capitalize(None), "")

    def test_should_average_many(self):
        self.assertEqual(calculate_average([10, 12, 14]), 12)

    def test_should_average_one(self):
        self.assertEqual(calculate_average([15]), 15)

    def test_should_average_empty(self):
        self.assertEqual(calculate_average([]), 0)

    def test_should_average_null(self):
        self.assertEqual(calculate_average(None), 0)

    def test_should_average_round(self):
        self.assertEqual(calculate_average([1, 2, 2]), 1.67)

    def test_should_slugify_words(self):
        self.assertEqual(slugify("Hello World"), "hello-world")

    def test_should_slugify_spaces(self):
        self.assertEqual(slugify(" Spaces Everywhere "), "spaces-everywhere")

    def test_should_slugify_accents(self):
        self.assertEqual(slugify("C'est l'été !"), "cest-lete")

    def test_should_slugify_empty(self):
        self.assertEqual(slugify(""), "")

    def test_should_clamp_middle(self):
        self.assertEqual(clamp(5, 0, 10), 5)

    def test_should_clamp_low(self):
        self.assertEqual(clamp(-5, 0, 10), 0)

    def test_should_clamp_high(self):
        self.assertEqual(clamp(15, 0, 10), 10)

    def test_should_clamp_zero(self):
        self.assertEqual(clamp(0, 0, 0), 0)

    def test_should_reject_reversed_bounds(self):
        with self.assertRaises(ValueError):
            clamp(1, 2, 0)


class SortStudentsTests(SimpleTestCase):
    def setUp(self):
        self.students = [{"name": "Zoé", "grade": 12, "age": 20}, {"name": "Adam", "grade": 18, "age": 19}]

    def test_should_sort_grade_ascending(self):
        self.assertEqual([x["grade"] for x in sort_students(self.students, "grade", "asc")], [12, 18])

    def test_should_sort_grade_descending(self):
        self.assertEqual([x["grade"] for x in sort_students(self.students, "grade", "desc")], [18, 12])

    def test_should_sort_name_ascending(self):
        self.assertEqual([x["name"] for x in sort_students(self.students, "name")], ["Adam", "Zoé"])

    def test_should_sort_age_ascending(self):
        self.assertEqual([x["age"] for x in sort_students(self.students, "age")], [19, 20])

    def test_should_sort_null(self):
        self.assertEqual(sort_students(None, "grade"), [])

    def test_should_sort_empty(self):
        self.assertEqual(sort_students([], "grade"), [])

    def test_should_sort_without_mutating(self):
        original = [student.copy() for student in self.students]
        result = sort_students(self.students, "name")
        self.assertEqual(self.students, original)
        self.assertIsNot(result, self.students)

    def test_should_sort_ascending_by_default(self):
        self.assertEqual(sort_students(self.students, "grade"), sort_students(self.students, "grade", "asc"))

    def test_should_reject_unknown_sort_key(self):
        with self.assertRaises(ValueError):
            sort_students(self.students, "height")

    def test_should_reject_unknown_sort_order(self):
        with self.assertRaises(ValueError):
            sort_students(self.students, "grade", "sideways")


class PriceGroupingDiscountTests(SimpleTestCase):
    def test_should_parse_decimal(self):
        self.assertEqual(parse_price("12.99"), 12.99)

    def test_should_parse_comma(self):
        self.assertEqual(parse_price("12,99"), 12.99)

    def test_should_parse_suffix(self):
        self.assertEqual(parse_price("12.99 €"), 12.99)

    def test_should_parse_prefix(self):
        self.assertEqual(parse_price("€12.99"), 12.99)

    def test_should_parse_number(self):
        self.assertEqual(parse_price(12.99), 12.99)

    def test_should_parse_free(self):
        self.assertEqual(parse_price("gratuit"), 0)

    def test_should_parse_invalid(self):
        self.assertEqual(parse_price("abc"), None)

    def test_should_parse_negative(self):
        self.assertEqual(parse_price("-5.00"), None)

    def test_should_parse_null(self):
        self.assertEqual(parse_price(None), None)

    def test_should_parse_boolean(self):
        self.assertEqual(parse_price(True), None)

    def test_should_parse_nan(self):
        self.assertEqual(parse_price(float("nan")), None)

    def test_should_parse_infinity(self):
        self.assertEqual(parse_price("inf"), None)

    def test_should_parse_object(self):
        self.assertEqual(parse_price({}), None)

    def test_should_group_empty(self):
        self.assertEqual(group_by([], "role"), {})

    def test_should_group_null(self):
        self.assertEqual(group_by(None, "role"), {})

    def test_should_group_one(self):
        self.assertEqual(group_by([{"role": "dev"}], "role"), {"dev": [{"role": "dev"}]})

    def test_should_group_missing_key(self):
        self.assertEqual(group_by([{"name": "Alice"}], "role"), {None: [{"name": "Alice"}]})

    def test_should_group_many(self):
        self.assertEqual(
            group_by([{"role": "dev"}, {"role": "design"}, {"role": "dev"}], "role"),
            {"dev": [{"role": "dev"}, {"role": "dev"}], "design": [{"role": "design"}]},
        )

    def test_should_discount_percent(self):
        self.assertEqual(calculate_discount(100, [{"type": "percentage", "value": 10}]), 90)

    def test_should_discount_fixed(self):
        self.assertEqual(calculate_discount(20, [{"type": "fixed", "value": 5}]), 15)

    def test_should_discount_in_order(self):
        self.assertEqual(
            calculate_discount(100, [{"type": "percentage", "value": 10}, {"type": "fixed", "value": 5}]), 85
        )

    def test_should_discount_reverse_order(self):
        self.assertEqual(
            calculate_discount(100, [{"type": "fixed", "value": 5}, {"type": "percentage", "value": 10}]), 85.5
        )

    def test_should_discount_floor_zero(self):
        self.assertEqual(calculate_discount(5, [{"type": "fixed", "value": 10}]), 0)

    def test_should_discount_free_fourth(self):
        self.assertEqual(calculate_discount(40, [{"type": "buyXgetY", "buy": 3, "free": 1, "itemPrice": 10}]), 30)

    def test_should_discount_no_free_before_four(self):
        self.assertEqual(calculate_discount(30, [{"type": "buyXgetY", "buy": 3, "free": 1, "itemPrice": 10}]), 30)

    def test_should_discount_two_free_groups(self):
        self.assertEqual(calculate_discount(80, [{"type": "buyXgetY", "buy": 3, "free": 1, "itemPrice": 10}]), 60)

    def test_should_discount_none(self):
        self.assertEqual(calculate_discount(20, None), 20)

    def test_should_reject_negative_price(self):
        with self.assertRaises(ValueError):
            calculate_discount(-1, [])

    def test_should_reject_unknown_rule(self):
        with self.assertRaises(ValueError):
            calculate_discount(10, [{"type": "unknown"}])

    def test_should_reject_bad_percentage(self):
        with self.assertRaises(ValueError):
            calculate_discount(10, [{"type": "percentage", "value": 101}])

    def test_should_reject_boolean_discount(self):
        with self.assertRaises(ValueError):
            calculate_discount(10, [{"type": "fixed", "value": True}])

    def test_should_reject_nan_discount(self):
        with self.assertRaises(ValueError):
            calculate_discount(float("nan"), [])

    def test_should_reject_bad_rule(self):
        with self.assertRaises(ValueError):
            calculate_discount(10, [None])

    def test_should_reject_zero_buy(self):
        with self.assertRaises(ValueError):
            calculate_discount(10, [{"type": "buyXgetY", "buy": 0, "free": 1, "itemPrice": 10}])
