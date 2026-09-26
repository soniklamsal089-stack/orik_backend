from rest_framework import serializers

from .models import Enquiry, Subscriber


class EnquirySerializer(serializers.ModelSerializer):
    # Honeypot: the form renders this hidden and off-screen, so a human never
    # fills it. Bots that fill every input give themselves away.
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Enquiry
        fields = ["id", "name", "business", "email", "phone", "package", "message", "website", "created_at"]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            "name": {"trim_whitespace": True},
            "business": {"trim_whitespace": True},
            "phone": {"trim_whitespace": True},
        }

    def validate_website(self, value):
        if value.strip():
            # Deliberately vague: don't tell a bot which field caught it.
            raise serializers.ValidationError("This enquiry could not be accepted.")
        return value

    def validate_message(self, value):
        # A form this small has no reason to carry an essay; caps DB abuse.
        if len(value) > 4000:
            raise serializers.ValidationError("Please keep the project details under 4000 characters.")
        return value

    def create(self, validated_data):
        validated_data.pop("website", None)
        return super().create(validated_data)


class SubscriberSerializer(serializers.ModelSerializer):
    # Same honeypot as the enquiry form.
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Subscriber
        fields = ["id", "email", "website", "created_at"]
        read_only_fields = ["id", "created_at"]
        # Signing up twice is not an error worth showing a visitor.
        extra_kwargs = {"email": {"validators": []}}

    def validate_website(self, value):
        if value.strip():
            raise serializers.ValidationError("This sign-up could not be accepted.")
        return value

    def validate_email(self, value):
        return value.strip().lower()

    def create(self, validated_data):
        validated_data.pop("website", None)
        email = validated_data.pop("email")
        # An address that is already on the list just gets reactivated, so a
        # second sign-up reads as success rather than "email already exists".
        subscriber, _ = Subscriber.objects.update_or_create(
            email=email, defaults={**validated_data, "is_active": True}
        )
        return subscriber
