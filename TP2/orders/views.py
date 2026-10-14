"""HTTP views; app configuration is separate from the server entry point."""

import json
from uuid import uuid4

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from orders.pricing import DEFAULT_PROMO_CODES, apply_promo_code, calculate_order_total

ORDERS = {}


def _body(request):
    try:
        return json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("JSON invalide.") from None


def _calculate(data):
    return calculate_order_total(
        data.get("items"),
        data.get("distance"),
        data.get("weight"),
        data.get("promoCode"),
        data.get("hour", 15),
        data.get("dayOfWeek", "tuesday"),
        DEFAULT_PROMO_CODES,
    )


@require_POST
def simulate_order(request):
    try:
        return JsonResponse(_calculate(_body(request)))
    except (ValueError, TypeError, KeyError) as error:
        return JsonResponse({"error": str(error)}, status=400)


@require_POST
def create_order(request):
    try:
        result = _calculate(_body(request))
    except (ValueError, TypeError, KeyError) as error:
        return JsonResponse({"error": str(error)}, status=400)
    order = {"id": str(uuid4()), **result}
    ORDERS[order["id"]] = order
    return JsonResponse(order, status=201)


@require_GET
def get_order(request, order_id):
    order = ORDERS.get(order_id)
    if order is None:
        return JsonResponse({"error": "Commande introuvable."}, status=404)
    return JsonResponse(order)


@require_POST
def validate_promo(request):
    try:
        data = _body(request)
        if not data.get("promoCode"):
            raise ValueError("Code promo requis.")
        result = apply_promo_code(data.get("subtotal"), data["promoCode"], DEFAULT_PROMO_CODES)
        return JsonResponse({"valid": True, **result})
    except ValueError as error:
        status = 404 if str(error) == "Code promo inconnu." else 400
        return JsonResponse({"valid": False, "error": str(error)}, status=status)
    except (TypeError, KeyError) as error:
        return JsonResponse({"valid": False, "error": str(error)}, status=400)
