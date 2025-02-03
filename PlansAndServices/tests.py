from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from .views import (
    HomePageView, AboutPageView, ContactPageView, PrivacyPageView,
    HelpPageView, ITRPageView, ServicePageView, request_callback
)
from .models import ITRFilingPlan, Service, CallbackRequest

class HomePageViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_template(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')

class ITRPageViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        ITRFilingPlan.objects.create(plan_name="Plan A", prices=100, discount_percentage=0, total_cost=100, is_deleted=False)
        ITRFilingPlan.objects.create(plan_name="Plan B", prices=100, discount_percentage=0, total_cost=100, is_deleted=True)

    def test_itr_page_status_code(self):
        response = self.client.get(reverse('itr'))
        self.assertEqual(response.status_code, 200)

    def test_itr_page_template(self):
        response = self.client.get(reverse('itr'))
        self.assertTemplateUsed(response, 'PlansAndServices/itr.html')

    def test_itr_page_context(self):
        response = self.client.get(reverse('itr'))
        self.assertIn('plans', response.context)
        self.assertEqual(len(response.context['plans']), 1)
        self.assertEqual(response.context['plans'][0].plan_name, "Plan A")

class ServicePageViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        Service.objects.create(
            name="Service A",
            service_code="01",
            basic_cost=200,
            discount=10,  # Assuming a 10% discount
            gst=18,
            is_deleted=False
        )
        Service.objects.create(
            name="Service B",
            service_code="02",
            basic_cost=150,
            discount=5,  # Assuming a 5% discount
            gst=18,
            is_deleted=True
        )

    def test_service_page_status_code(self):
        response = self.client.get(reverse('service'))
        self.assertEqual(response.status_code, 200)

    def test_service_page_template(self):
        response = self.client.get(reverse('service'))
        self.assertTemplateUsed(response, 'PlansAndServices/service.html')

    def test_service_page_context(self):
        response = self.client.get(reverse('service'))
        self.assertIn('services', response.context)
        # Ensure only non-deleted services are included
        services = response.context['services']
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0].name, "Service A")

    def test_service_page_search(self):
        response = self.client.get(reverse('service'), {'q': 'Service A'})
        services = response.context['services']
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0].name, "Service A")

    def test_total_cost_calculation(self):
        service = Service.objects.get(name="Service A")
        expected_discounted_price = service.basic_cost * (1 - service.discount / 100)
        expected_total_cost = expected_discounted_price * (1 + service.gst / 100)
        self.assertAlmostEqual(service.total_cost, expected_total_cost, places=2)

class RequestCallbackTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_request_callback_post_success(self):
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'message': 'Please call me back.'
        }
        response = self.client.post(reverse('request_callback'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'Request submitted successfully'})
        self.assertEqual(CallbackRequest.objects.count(), 1)
        callback_request = CallbackRequest.objects.first()
        self.assertEqual(callback_request.name, 'John Doe')
        self.assertEqual(callback_request.email, 'john@example.com')
        self.assertEqual(callback_request.phone, '1234567890')
        self.assertEqual(callback_request.message, 'Please call me back.')
        self.assertEqual(callback_request.status, 'Pending')

    def test_request_callback_get(self):
        response = self.client.get(reverse('request_callback'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        
class ServiceDetailsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.service = Service.objects.create(
            name="Service A",
            service_code="SVC001",
            description="Description of Service A",
            basic_cost=100.0,
            discount=10.0,
            gst=18.0,
            is_deleted=False
        )

    def test_service_details(self):
        response = self.client.get(reverse('service_details', args=[self.service.pk]))
        self.assertEqual(response.status_code, 200)
        expected_data = {
            "id": self.service.id,
            "name": self.service.name,
            "service_code": self.service.service_code,
            "description": self.service.description,
            "basic_cost": self.service.basic_cost,
            "discount": self.service.discount,
            "gst": self.service.gst,
            "total_cost": self.service.get_total_cost(),
        }
        self.assertEqual(response.json(), expected_data)

