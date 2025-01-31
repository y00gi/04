from django.contrib import admin
from .models import ITRFilingPlan, Field, CallbackRequest, Service, PromoCode, Order

admin.site.site_header = "Fintrix Administration"
admin.site.site_title = "Fintrix Admin Portal"
admin.site.index_title = "Welcome to Fintrix Admin Panel"

class FieldInline(admin.TabularInline):
    model = Field
    extra = 1  # Number of empty forms to display
    fields = ('name', 'is_deleted', 'is_transacted')  # Show specific fields
    readonly_fields = ()  # Make is_transacted read-only

@admin.register(ITRFilingPlan)
class ITRFilingPlanAdmin(admin.ModelAdmin):
    list_display = ('plan_name', 'prices', 'discount_percentage', 'total_cost', 'created_at', 'updated_at', 'is_deleted', 'is_transacted')
    readonly_fields = ('total_cost',)  # Make total_cost read-only, since it's auto-calculated
    search_fields = ('plan_name',)  # Allow searching by plan_name
    list_filter = ('is_deleted', 'is_transacted')  # Add filters for is_deleted and is_transacted
    inlines = [FieldInline]  # Inline the Field model to appear in the ITRFilingPlan admin

# Register CallbackRequest with a custom admin interface
@admin.register(CallbackRequest)
class CallbackRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'message', 'created_at')  # Display important fields in the list view
    search_fields = ('name', 'email')  # Enable searching by name and email
    list_filter = ('created_at',)  # Allow filtering by created_at date
    ordering = ('-created_at',)  # Display most recent requests first

    # Optional: Add actions for the admin interface
    actions = ['mark_as_processed']

    def mark_as_processed(self, request, queryset):
        # Custom action to mark callback requests as processed
        queryset.update(is_processed=True)  # Assuming you add an `is_processed` field to CallbackRequest
        self.message_user(request, "Selected callback requests marked as processed")
    mark_as_processed.short_description = "Mark selected requests as processed"

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_code', 'basic_cost', 'discount', 'gst', 'calculate_total_cost_display', 'is_deleted', 'is_transacted')
    search_fields = ('name', 'service_code')
    list_filter = ('gst', 'is_deleted', 'is_transacted')
    readonly_fields = ('total_cost',)

    def calculate_total_cost_display(self, obj):
        """Dynamically display the total cost in the admin panel."""
        return f"{obj.get_total_cost():.2f}"
    calculate_total_cost_display.short_description = "Total Cost (Dynamic)"

# Customizing PromoCode admin interface
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_percentage', 'is_deleted', 'is_transacted')
    list_filter = ('is_deleted', 'is_transacted')
    search_fields = ('name',)
    actions = ['mark_as_deleted']

    # Custom action to mark promo codes as deleted
    def mark_as_deleted(self, request, queryset):
        queryset.update(is_deleted=True)
    mark_as_deleted.short_description = "Mark selected promo codes as deleted"

# Customizing Order admin interface
class OrderAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'order_status', 'total_cost', 'created_at', 'updated_at')
    list_filter = ('order_status', 'is_deleted', 'is_transacted')
    search_fields = ('full_name', 'email', 'contact_number')
    list_editable = ('order_status',)
    raw_id_fields = ('itr_filing_plan',)  # Optimize performance for ForeignKey selection
    filter_horizontal = ('services',)  # Display services in a filterable horizontal box
    readonly_fields = ('total_cost', 'created_at', 'updated_at')  # Make these fields readonly

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_transacted:
            # If the order is already transacted, make these fields readonly
            return self.readonly_fields
        return self.readonly_fields

# Register models in the admin
admin.site.register(PromoCode, PromoCodeAdmin)
admin.site.register(Order, OrderAdmin)