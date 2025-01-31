from django.shortcuts import render, redirect, get_object_or_404
from PlansAndServices.models import ITRFilingPlan, Service, PromoCode, Order
from .cart import Cart
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib import messages
from decimal import Decimal

def cart_add(request, item_id, item_type="service"):
    """
    View to add an item (ITRFilingPlan or Service) to the cart.
    - If adding a plan, ensures only one plan exists.
    - If adding a service, allows multiple services with quantity.
    """
    cart = Cart(request)

    if item_type == "plan":
        item = get_object_or_404(ITRFilingPlan, id=item_id)
    elif item_type == "service":
        item = get_object_or_404(Service, id=item_id)
    else:
        return JsonResponse({"error": "Invalid item type"}, status=400)

    cart.add(item=item, item_type=item_type)

    # Return JSON response for AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"cart_count": len(cart)})

    return redirect('cart_detail')

def cart_remove(request, item_id, item_type="service"):
    """
    View to remove an item (ITRFilingPlan or Service) from the cart.
    """
    cart = Cart(request)

    if item_type == "plan":
        item = get_object_or_404(ITRFilingPlan, id=item_id)
    elif item_type == "service":
        item = get_object_or_404(Service, id=item_id)
    else:
        return JsonResponse({"error": "Invalid item type"}, status=400)

    cart.remove(item, item_type=item_type)
    return redirect('cart_detail')

def cart_detail(request):
    """
    View to display cart details.
    """
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart})

def validate_promo_code(request):
    promo_code = request.GET.get("promo_code", "").strip()
    subtotal = Decimal(request.GET.get("subtotal", "0"))  # Convert subtotal to Decimal

    try:
        promo = PromoCode.objects.get(name=promo_code, is_deleted=False, is_transacted=False)
    except PromoCode.DoesNotExist:
        return JsonResponse({"valid": False})

    discount_amount = (promo.discount_percentage / Decimal("100")) * subtotal
    new_total = subtotal - discount_amount

    return JsonResponse({
        "valid": True,
        "discount": round(discount_amount, 2),
        "new_total": round(new_total, 2),
    })
    
def cart_checkout(request):
    cart = Cart(request)

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        firm_name = request.POST.get("firm_name", "").strip()
        gst_number = request.POST.get("gst_number", "").strip()
        contact_number = request.POST.get("contact_number", "").strip()
        email = request.POST.get("email", "").strip()
        address = request.POST.get("address", "").strip()

        # ✅ Convert to Decimal for precision, then to float
        try:
            total_cost = Decimal(request.POST.get("total_cost", "0").strip())
            total_cost = float(total_cost)  # Convert safely before saving
        except ValueError:
            messages.error(request, "Invalid total cost format.")
            return redirect("cart_checkout")

        # Validate required fields
        if not full_name or not contact_number or not email:
            messages.error(request, "Full name, contact number, and email are required.")
            return redirect("cart_checkout")

        if len(cart) == 0:
            messages.error(request, "Your cart is empty. Please add items before checking out.")
            return redirect("cart_detail")

        # ✅ Create and save order
        order = Order.objects.create(
            full_name=full_name,
            firm_name=firm_name,
            gst_number=gst_number,
            contact_number=contact_number,
            email=email,
            address=address,
            total_cost=total_cost
        )

        # ✅ Assign the ITR filing plan (store only ID in the cart)
        itr_plan_id = next((item["item"].id for item in cart if item["item_type"] == "plan"), None)
        if itr_plan_id:
            order.itr_filing_plan = ITRFilingPlan.objects.get(id=itr_plan_id)
            order.save()  # ✅ Save after assigning ITR plan

        # ✅ Assign services properly (store only IDs in cart)
        service_ids = [item["item"].id for item in cart if item["item_type"] == "service"]
        services = Service.objects.filter(id__in=service_ids)
        order.services.set(services)

        # ✅ Clear cart after successful checkout
        cart.clear()

        messages.success(request, "Your order has been placed successfully!")
        return redirect("order_confirmation", order_id=order.id)

    return render(request, "cart/detail.html")

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "cart/order_confirmation.html", {"order": order})