from django.urls import path

from orders import views

urlpatterns = [
    path("orders/simulate", views.simulate_order, name="simulate-order"),
    path("orders", views.create_order, name="create-order"),
    path("orders/<str:order_id>", views.get_order, name="get-order"),
    path("promo/validate", views.validate_promo, name="validate-promo"),
]
