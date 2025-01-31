from django.urls import path
from .views import HomePageView, AboutPageView, ContactPageView, PrivacyPageView, HelpPageView, ITRPageView, request_callback, ServicePageView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("contact/", ContactPageView.as_view(), name="contact"),
    path("privacy/", PrivacyPageView.as_view(), name="privacy"),
    path("help/", HelpPageView.as_view(), name="help"),
    path("itr/", ITRPageView.as_view(), name="itr"),
    path("service/", ServicePageView.as_view(), name="service"),
    path('services/details/<int:pk>/', ServicePageView.service_details, name='service_details'),

    path("request-callback/", request_callback, name="request_callback"),
    ]