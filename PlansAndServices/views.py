from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from .models import ITRFilingPlan, CallbackRequest, Service
from django.http import JsonResponse

# Create your views here.
class ITRPageView(TemplateView):
    template_name = "PlansAndServices/itr.html"

    def get_context_data(self, **kwargs):
        # Get the default context
        context = super().get_context_data(**kwargs)

        # Query all non-deleted plans
        context['plans'] = ITRFilingPlan.objects.filter(is_deleted=False)

        # Return the updated context
        return context

class ServicePageView(TemplateView):
    template_name = "PlansAndServices/service.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q')
        if query:
            context['services'] = Service.objects.filter(name__icontains=query, is_deleted=False)
        else:
            context['services'] = Service.objects.filter(is_deleted=False)
        return context
    
    def service_details(request, pk):
        service = get_object_or_404(Service, pk=pk, is_deleted=False)
        data = {
            "id": service.id,
            "name": service.name,
            "service_code": service.service_code,  # Use correct field name
            "description": service.description,
            "basic_cost": float(service.basic_cost),
            "discount": float(service.discount),
            "gst": float(service.gst),
            "total_cost": float(service.get_total_cost()),
        }
        return JsonResponse(data)

class HomePageView(TemplateView):
    template_name = "home.html"

class AboutPageView(TemplateView):
    template_name = "PlansAndServices/aboutUs.html"

class ContactPageView(TemplateView):
    template_name = "PlansAndServices/contact.html"

class PrivacyPageView(TemplateView):
    template_name = "PlansAndServices/privacy.html"

class HelpPageView(TemplateView):
    template_name = "PlansAndServices/help.html"

def request_callback(request):
    if request.method == 'POST':
        # Get the form data from the request
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        
        # Create a new CallbackRequest instance and save it
        CallbackRequest.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )
        
        # Return a success response
        return JsonResponse({'message': 'Request submitted successfully'}, status=200)
    
    return render(request, 'home.html')