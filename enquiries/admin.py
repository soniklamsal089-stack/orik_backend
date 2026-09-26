import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import Enquiry, Subscriber


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ["name", "business", "email", "phone", "package", "status", "created_at"]
    list_filter = ["status", "package", "created_at"]
    search_fields = ["name", "business", "email", "phone", "message"]
    list_editable = ["status"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at", "ip_address", "user_agent"]
    list_per_page = 50

    fieldsets = [
        ("Enquiry", {"fields": ["name", "business", "email", "phone", "package", "message"]}),
        ("Handling", {"fields": ["status"]}),
        ("Received", {"fields": ["created_at", "ip_address", "user_agent"], "classes": ["collapse"]}),
    ]

    @admin.action(description="Mark selected enquiries as contacted")
    def mark_contacted(self, request, queryset):
        updated = queryset.update(status=Enquiry.Status.CONTACTED)
        self.message_user(request, f"{updated} enquiry(s) marked as contacted.")

    actions = ["mark_contacted"]

    def has_add_permission(self, request):
        # Enquiries only arrive through the API.
        return False


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["email"]
    list_editable = ["is_active"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at", "ip_address", "user_agent"]
    list_per_page = 100

    fieldsets = [
        ("Subscriber", {"fields": ["email", "is_active"]}),
        ("Received", {"fields": ["created_at", "ip_address", "user_agent"], "classes": ["collapse"]}),
    ]

    @admin.action(description="Export selected to CSV")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="subscribers.csv"'
        writer = csv.writer(response)
        writer.writerow(["email", "is_active", "signed up"])
        for row in queryset:
            writer.writerow([row.email, row.is_active, row.created_at.strftime("%Y-%m-%d %H:%M")])
        return response

    actions = ["export_csv"]

    def has_add_permission(self, request):
        # Sign-ups only arrive through the popup.
        return False
