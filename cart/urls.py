from django.urls import path
from .views import cart_add, cart_detail, cart_remove, validate_promo_code, cart_checkout, order_confirmation

urlpatterns = [
    path('add/<int:item_id>/<str:item_type>/', cart_add, name='cart_add'),
    path('remove/<int:item_id>/<str:item_type>/', cart_remove, name='cart_remove'),
    path('', cart_detail, name='cart_detail'),
    path('validate_promo_code/', validate_promo_code, name='validate_promo_code'),
    path('cart_checkout/', cart_checkout, name='cart_checkout'),
    path("checkout/", cart_checkout, name="cart_checkout"),
    path("order-confirmation/<int:order_id>/", order_confirmation, name="order_confirmation"),
]
