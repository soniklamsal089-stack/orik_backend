from django.urls import path

from .views import EnquiryCreateView, SubscriberCreateView

urlpatterns = [
    path("enquiries/", EnquiryCreateView.as_view(), name="enquiry-create"),
    path("subscribers/", SubscriberCreateView.as_view(), name="subscriber-create"),
]
