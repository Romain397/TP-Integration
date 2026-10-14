"""Pricing rules for delivery orders."""

from datetime import date

from orders.utils import parse_price

DEFAULT_PROMO_CODES = [
    {"code": "BIENVENUE20", "type": "percentage", "value": 20, "minOrder": 15.0, "expiresAt": "2026-12-31"},
    {"code": "FIXE5", "type": "fixed", "value": 5, "minOrder": 10.0, "expiresAt": "2026-12-31"},
    {"code": "ETE2020", "type": "percentage", "value": 20, "minOrder": 0, "expiresAt": "2020-12-31"},
]
WEEKDAYS = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}


def calculate_delivery_fee(distance, weight):
    if not isinstance(distance, (int, float)) or not isinstance(weight, (int, float)):
        raise ValueError("distance and weight must be numbers")
    if distance < 0 or weight < 0:
        raise ValueError("distance and weight cannot be negative")
    if distance > 10:
        return None
    fee = 2 + max(0, distance - 3) * 0.5
    if weight > 5:
        fee += 1.5
    return round(fee, 2)


def apply_promo_code(subtotal, promo_code, promo_codes=None, today=None):
    subtotal = parse_price(subtotal)
    if subtotal is None:
        raise ValueError("Montant invalide.")
    if promo_code in (None, ""):
        return {"subtotal": subtotal, "discount": 0.0, "total": subtotal}
    codes = DEFAULT_PROMO_CODES if promo_codes is None else promo_codes
    promo = next((item for item in codes if item["code"] == promo_code), None)
    if promo is None:
        raise ValueError("Code promo inconnu.")
    current_date = today or date.today()
    expiration = date.fromisoformat(promo["expiresAt"])
    if current_date > expiration:
        raise ValueError("Code promo expiré.")
    if subtotal < promo.get("minOrder", 0):
        raise ValueError("Montant minimum non atteint.")
    if promo["type"] == "percentage":
        total = subtotal * (1 - promo["value"] / 100)
    elif promo["type"] == "fixed":
        total = subtotal - promo["value"]
    else:
        raise ValueError("Type de promotion invalide.")
    total = round(max(0, total), 2)
    return {"subtotal": subtotal, "discount": round(subtotal - total, 2), "total": total}


def calculate_surge(hour, day_of_week):
    if not isinstance(hour, (int, float)) or not 0 <= hour <= 24:
        raise ValueError("hour must be between 0 and 24")
    day = day_of_week.lower() if isinstance(day_of_week, str) else ""
    if day not in WEEKDAYS:
        raise ValueError("invalid day of week")
    if hour < 10 or hour > 22:
        return 0
    weekday = WEEKDAYS[day]
    if weekday == 6:
        return 1.2
    if weekday in (4, 5) and 19 <= hour <= 22:
        return 1.8
    if weekday <= 3 and 19 <= hour <= 21:
        return 1.5
    if weekday <= 3 and 12 <= hour < 14:
        return 1.3
    return 1.0


def calculate_order_total(items, distance, weight, promo_code=None, hour=15, day_of_week="tuesday", promo_codes=None):
    if not isinstance(items, list) or not items:
        raise ValueError("Le panier doit contenir au moins un article.")
    subtotal = 0.0
    for item in items:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("price"), (int, float))
            or not isinstance(item.get("quantity"), int)
        ):
            raise ValueError("Article invalide.")
        if item["price"] < 0 or item["quantity"] <= 0:
            raise ValueError("Prix et quantité doivent être positifs.")
        subtotal += item["price"] * item["quantity"]
    subtotal = round(subtotal, 2)
    promo = apply_promo_code(subtotal, promo_code, promo_codes)
    delivery = calculate_delivery_fee(distance, weight)
    if delivery is None:
        raise ValueError("Adresse hors zone de livraison.")
    surge = calculate_surge(hour, day_of_week)
    if surge == 0:
        raise ValueError("Le service est fermé.")
    surged_delivery = round(delivery * surge, 2)
    return {
        "subtotal": subtotal,
        "discount": promo["discount"],
        "deliveryFee": surged_delivery,
        "surge": surge,
        "total": round(promo["total"] + surged_delivery, 2),
    }
