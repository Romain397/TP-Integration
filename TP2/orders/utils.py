"""Small utility functions and sorting exercise."""

import re
import unicodedata
from math import isfinite


def is_finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


def capitalize(text):
    if text is None:
        return ""
    text = str(text)
    return text[:1].upper() + text[1:].lower()


def calculate_average(numbers):
    if not numbers:
        return 0
    return round(sum(numbers) / len(numbers), 2)


def slugify(text):
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", str(text))
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_text = ascii_text.replace("'", "")
    return re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")


def clamp(value, minimum, maximum):
    if minimum > maximum:
        raise ValueError("minimum must be less than or equal to maximum")
    return max(minimum, min(value, maximum))


def sort_students(students, sort_by, order="asc"):
    if not students:
        return []
    if sort_by not in {"name", "grade", "age"}:
        raise ValueError("sort_by must be name, grade, or age")
    if order not in {"asc", "desc"}:
        raise ValueError("order must be asc or desc")
    return sorted(students, key=lambda student: student[sort_by], reverse=order == "desc")


def group_by(items, key):
    """Group dictionaries by a key, returning an empty mapping for no input."""
    groups = {}
    for item in items or []:
        group_key = item.get(key)
        groups.setdefault(group_key, []).append(item)
    return groups


def calculate_discount(price, discount_rules):
    """Apply percentage, fixed, and buy-X-get-Y rules sequentially."""
    if not is_finite_number(price) or price < 0:
        raise ValueError("price must be a non-negative number")
    if discount_rules is not None and not isinstance(discount_rules, list):
        raise ValueError("discount_rules must be a list")
    result = float(price)
    for rule in discount_rules or []:
        if not isinstance(rule, dict):
            raise ValueError("discount rule must be an object")
        rule_type = rule.get("type")
        if rule_type == "percentage":
            value = rule.get("value")
            if not is_finite_number(value) or not 0 <= value <= 100:
                raise ValueError("invalid percentage discount")
            result *= 1 - value / 100
        elif rule_type == "fixed":
            value = rule.get("value")
            if not is_finite_number(value) or value < 0:
                raise ValueError("invalid fixed discount")
            result -= value
        elif rule_type == "buyXgetY":
            buy, free, item_price = rule.get("buy"), rule.get("free"), rule.get("itemPrice")
            if not all(isinstance(value, int) and not isinstance(value, bool) and value > 0 for value in (buy, free)):
                raise ValueError("buy and free must be positive integers")
            if not is_finite_number(item_price) or item_price <= 0:
                raise ValueError("itemPrice must be positive")
            result -= int(result // ((buy + free) * item_price)) * free * item_price
        else:
            raise ValueError("unknown discount rule")
        result = max(0, result)
    return round(result, 2)


def parse_price(value):
    """Parse a price with either decimal separator and optional euro sign."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        amount = float(value)
    elif isinstance(value, str):
        if value.strip().lower() == "gratuit":
            return 0
        cleaned = value.strip().replace("€", "").replace(" ", "").replace(",", ".")
        try:
            amount = float(cleaned)
        except ValueError:
            return None
    else:
        return None
    if not isfinite(amount) or amount < 0:
        return None
    return round(amount, 2)
