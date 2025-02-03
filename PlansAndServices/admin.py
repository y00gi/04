from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import ITRFilingPlan, Field, CallbackRequest, Service, PromoCode, Order

admin.site.site_header = "Fintrix Administration"
admin.site.site_title = "Fintrix Admin Portal"
admin.site.index_title = "Welcome to Fintrix Admin Panel"

class FieldInline(admin.TabularInline):
    model = Field
    extra = 1
    fields = ('name', 'is_deleted', 'is_transacted')
    readonly_fields = ()

# Import-export resources
class ITRFilingPlanResource(resources.ModelResource):
    class Meta:
        model = ITRFilingPlan

class ServiceResource(resources.ModelResource):
    class Meta:
        model = Service

class PromoCodeResource(resources.ModelResource):
    class Meta:
        model = PromoCode

class OrderResource(resources.ModelResource):
    class Meta:
        model = Order

class CallbackRequestResource(resources.ModelResource):
    class Meta:
        model = CallbackRequest

@admin.register(ITRFilingPlan)
class ITRFilingPlanAdmin(ImportExportModelAdmin):
    resource_class = ITRFilingPlanResource
    list_display = ('plan_name', 'prices', 'discount_percentage', 'total_cost', 'created_at', 'updated_at', 'is_deleted', 'is_transacted')
    readonly_fields = ('total_cost',)
    search_fields = ('plan_name',)
    list_filter = ('is_deleted', 'is_transacted')
    inlines = [FieldInline]

@admin.register(CallbackRequest)
class CallbackRequestAdmin(ImportExportModelAdmin):
    resource_class = CallbackRequestResource
    list_display = ('name', 'email', 'phone', 'message', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    actions = ['mark_as_processed']

    def mark_as_processed(self, request, queryset):
        queryset.update(is_processed=True)
        self.message_user(request, "Selected callback requests marked as processed")
    mark_as_processed.short_description = "Mark selected requests as processed"

@admin.register(Service)
class ServiceAdmin(ImportExportModelAdmin):
    resource_class = ServiceResource
    list_display = ('name', 'service_code', 'basic_cost', 'discount', 'gst', 'calculate_total_cost_display', 'is_deleted', 'is_transacted')
    search_fields = ('name', 'service_code')
    list_filter = ('gst', 'is_deleted', 'is_transacted')
    readonly_fields = ('total_cost',)

    def calculate_total_cost_display(self, obj):
        return f"{obj.get_total_cost():.2f}"
    calculate_total_cost_display.short_description = "Total Cost (Dynamic)"

@admin.register(PromoCode)
class PromoCodeAdmin(ImportExportModelAdmin):
    resource_class = PromoCodeResource
    list_display = ('name', 'discount_percentage', 'is_deleted', 'is_transacted')
    list_filter = ('is_deleted', 'is_transacted')
    search_fields = ('name',)
    actions = ['mark_as_deleted']

    def mark_as_deleted(self, request, queryset):
        queryset.update(is_deleted=True)
    mark_as_deleted.short_description = "Mark selected promo codes as deleted"

@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    resource_class = OrderResource
    list_display = ('full_name', 'email', 'payment_status', 'total_cost', 'created_at', 'updated_at', 'transaction_id')
    list_filter = ('payment_status', 'is_deleted', 'is_transacted')
    search_fields = ('full_name', 'email', 'contact_number')
    list_editable = ('payment_status',)
    raw_id_fields = ('itr_filing_plan',)
    filter_horizontal = ('services',)
    readonly_fields = ('total_cost', 'created_at', 'updated_at')

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_transacted:
            return self.readonly_fields
        return self.readonly_fields
