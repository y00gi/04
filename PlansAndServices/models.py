from django.db import models
from django.core.exceptions import ValidationError

class ITRFilingPlan(models.Model):
    plan_name = models.CharField(max_length=255)  # Name of the plan
    prices = models.DecimalField(max_digits=10, decimal_places=2)  # Price for the plan
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Discount in percentage
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)  # Total cost after discount
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_transacted = models.BooleanField(default=False)

    def clean(self):
        # Validate discount_percentage
        if self.discount_percentage < 0:
            raise ValidationError("Discount percentage cannot be negative.")
        if self.discount_percentage > 100:
            raise ValidationError("Discount percentage cannot exceed 100%.")
        
    def save(self, *args, **kwargs):
        # Automatically calculate the total cost based on the price and discount
        self.clean()  # Validate before saving
        if self.discount_percentage > 0:
            self.total_cost = self.prices - (self.prices * self.discount_percentage / 100)
        else:
            self.total_cost = self.prices
        
        # Floor the total cost to remove decimal part
        self.total_cost = int(self.total_cost)  # Remove decimal part
        
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_transacted:
            self.is_deleted = True  # Mark as deleted instead of permanent deletion
            self.save()
        else:
            super().delete(*args, **kwargs)

    def __str__(self):
        return self.plan_name  # Return the name of the plan for readability


class Field(models.Model):
    name = models.CharField(max_length=255)
    plan = models.ForeignKey('ITRFilingPlan', related_name='fields', on_delete=models.CASCADE, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_transacted = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        if self.is_transacted:
            self.is_deleted = True
            self.save()
        else:
            super().delete(*args, **kwargs)  # Perform a permanent delete

    def __str__(self):
        return self.name
    
class Service(models.Model):
    name = models.CharField(max_length=255, unique=True)
    service_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    basic_cost = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    gst = models.DecimalField(max_digits=5, decimal_places=2, default=18.00, help_text="Enter GST percentage (adjustable by admin).")  # Percentage
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)  # New field
    is_deleted = models.BooleanField(default=False)
    is_transacted = models.BooleanField(default=False)

    def get_discounted_price(self):
        """Calculate the price after discount."""
        discount_amount = (self.basic_cost * self.discount) / 100
        return self.basic_cost - discount_amount

    def get_total_cost(self):
        """Calculate the final price after applying GST."""
        discounted_price = self.get_discounted_price()
        gst_amount = (discounted_price * self.gst) / 100
        return discounted_price + gst_amount
    
    def save(self, *args, **kwargs):
        """Override save to update total_cost before saving."""
        self.total_cost = self.get_total_cost()
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if self.is_transacted:
            self.is_deleted = True  # Mark as deleted instead of permanent deletion
            self.save()
        else:
            super().delete(*args, **kwargs)  # Perform a permanent delete

    def __str__(self):
        return f"{self.name} - {self.service_code}"

class CallbackRequest(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()
    status = models.CharField(max_length=150, default='Pending')

    # Timestamp for when the request was made
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Callback Request from {self.name}"

class PromoCode(models.Model):
    name = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Enter discount percentage (e.g., 10.00 for 10%). Cannot exceed 100%."
    )
    is_deleted = models.BooleanField(default=False)
    is_transacted = models.BooleanField(default=False)

    def clean(self):
        if self.discount_percentage > 100:
            raise ValidationError("Discount percentage cannot exceed 100%.")

    def delete(self, *args, **kwargs):
        if self.is_transacted:
            self.is_deleted = True
            self.save()
        else:
            super().delete(*args, **kwargs)  # Perform a permanent delete

    def __str__(self):
        return f"{self.name} ({self.discount_percentage}%)"

class Order(models.Model):
    full_name = models.CharField(max_length=255)
    firm_name = models.CharField(max_length=255, blank=True, null=True)
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    is_deleted = models.BooleanField(default=False)
    is_transacted = models.BooleanField(default=False)
    
    # Relationships with ITRFilingPlan, Service, and PromoCode models
    itr_filing_plan = models.ForeignKey('ITRFilingPlan', on_delete=models.SET_NULL, null=True, blank=True)
    services = models.ManyToManyField('Service', related_name='orders')

     # Payment and Order status
    order_status = models.CharField(max_length=50, default='Pending', choices=[
        ('Pending', 'Pending'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')
    ])
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    # Timestamp for order creation
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Save without recalculating total cost (taken from form input)"""
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_transacted:
            self.is_deleted = True
            self.save()
        else:
            super().delete(*args, **kwargs)  # Perform a permanent delete

    def __str__(self):
        return f"Order for {self.full_name} ({self.email})"
