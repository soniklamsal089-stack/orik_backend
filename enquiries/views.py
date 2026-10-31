from django.conf import settings
from django.core.mail import send_mail
from rest_framework import generics
from rest_framework.throttling import AnonRateThrottle

from .models import Enquiry
from .serializers import EnquirySerializer


class EnquiryRateThrottle(AnonRateThrottle):
    """Rate limited per IP; the rate itself lives in settings."""

    scope = "enquiries"


class EnquiryCreateView(generics.CreateAPIView):
    """Accepts contact-form submissions. Write-only: enquiries are read in the admin."""

    queryset = Enquiry.objects.all()
    serializer_class = EnquirySerializer
    throttle_classes = [EnquiryRateThrottle]

    def perform_create(self, serializer):
        enquiry = serializer.save(
            ip_address=client_ip(self.request),
            user_agent=self.request.META.get("HTTP_USER_AGENT", "")[:300],
        )
        
        # Send email notification
        send_enquiry_notification(enquiry)


def client_ip(request):
    """Real client IP, accounting for a single proxy in front of the API."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def send_enquiry_notification(enquiry):
    """Send email notification when a new enquiry is received."""
    try:
        subject = f"New Enquiry from {enquiry.name} - {enquiry.business}"
        
        message = f"""
New Contact Form Submission

Name: {enquiry.name}
Business: {enquiry.business}
Email: {enquiry.email}
Phone: {enquiry.phone}
Package: {enquiry.package or "Not specified"}

Message:
{enquiry.message}

---
Submitted at: {enquiry.created_at.strftime("%Y-%m-%d %H:%M:%S %Z")}
IP Address: {enquiry.ip_address or "Unknown"}
"""

        recipient = settings.ENQUIRY_NOTIFICATION_EMAIL
        if recipient:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=True,  # Don't crash if email fails
            )
    except Exception as e:
        # Log the error but don't fail the enquiry submission
        print(f"Failed to send enquiry notification: {e}")