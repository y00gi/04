from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from PlansAndServices.models import ITRFilingPlan, Service, PromoCode


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {"plans": {}, "services": {}}
        self.cart = cart

    def add(self, item, quantity=1, override_quantity=False, item_type="service"):
        """
        Add an item to the cart, ensuring JSON serializability.
        """
        item_id = str(item.id)
        price = float(item.total_cost)

        if item_type == "plan":
            if self.cart["plans"] and item_id not in self.cart["plans"]:
                self.clear_plans()
            self.cart["plans"][item_id] = {"quantity": 1, "price": price}

        elif item_type == "service":
            if item_id not in self.cart["services"]:
                self.cart["services"][item_id] = {"quantity": 1, "price": price}
            else:
                if override_quantity:
                    self.cart["services"][item_id]["quantity"] = 1
                else:
                    self.cart["services"][item_id]["quantity"] = min(
                        self.cart["services"][item_id]["quantity"] + quantity, 1
                    )

        self.save()

    def remove(self, item_id, item_type="service"):
        """Remove an item from the cart safely."""
        item_id = str(item_id)
        
        if item_type == "plan" and item_id in self.cart["plans"]:
            del self.cart["plans"][item_id]
        elif item_type == "service" and item_id in self.cart["services"]:
            del self.cart["services"][item_id]
        
        self.save()

    def __iter__(self):
        """Iterate over cart items and retrieve actual objects."""
        plan_ids = list(self.cart["plans"].keys())
        service_ids = list(self.cart["services"].keys())
        
        plans = {str(plan.id): plan for plan in ITRFilingPlan.objects.filter(id__in=plan_ids)}
        services = {str(service.id): service for service in Service.objects.filter(id__in=service_ids)}
        
        for item_id, item_data in self.cart["plans"].items():
            yield {
                "item": plans.get(item_id),
                "item_type": "plan",
                "quantity": item_data["quantity"],
                "price": item_data["price"],
                "total_price": item_data["price"] * item_data["quantity"],
            }
        
        for item_id, item_data in self.cart["services"].items():
            yield {
                "item": services.get(item_id),
                "item_type": "service",
                "quantity": item_data["quantity"],
                "price": item_data["price"],
                "total_price": item_data["price"] * item_data["quantity"],
            }

    def __len__(self):
        """Count total items in the cart."""
        return sum(item["quantity"] for item in self.cart["plans"].values()) + \
               sum(item["quantity"] for item in self.cart["services"].values())

    def get_sub_total_price(self):
        """Calculate total price of cart items."""
        return sum(item["price"] * item["quantity"] for item in self.cart["plans"].values()) + \
               sum(item["price"] * item["quantity"] for item in self.cart["services"].values())

    def clear(self):
        """Clear the entire cart."""
        self.cart = {"plans": {}, "services": {}}
        self.save()

    def clear_plans(self):
        """Remove all plans from the cart but keep services."""
        self.cart["plans"] = {}
        self.save()

    def clear_services(self):
        """Remove all services from the cart but keep plans."""
        self.cart["services"] = {}
        self.save()

    def save(self):
        """Mark session as modified to ensure it saves."""
        self.session.modified = True

    def apply_promo_code(self, promo_code):
        """Apply a promo code to the cart."""
        try:
            promo = PromoCode.objects.get(code=promo_code, is_active=True)
        except ObjectDoesNotExist:
            return {"valid": False, "message": "Invalid or expired promo code."}
        
        subtotal = self.get_sub_total_price()
        discount = (promo.discount_percentage / 100) * subtotal
        new_total = subtotal - discount
        
        return {
            "valid": True,
            "discount": round(float(discount), 2),
            "new_total": round(float(new_total), 2),
        }

    def get_total_cost_after_discount(self, promo_code=None):
        """Get total cost after discount if a promo code is applied."""
        subtotal = self.get_sub_total_price()
        if promo_code:
            promo_response = self.apply_promo_code(promo_code)
            return promo_response["new_total"] if promo_response["valid"] else subtotal
        return subtotal
