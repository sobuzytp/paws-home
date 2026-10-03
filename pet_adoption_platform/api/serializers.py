from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from adoptions.models import AdoptionRequest
from pets.models import Pet


class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = ["id", "name", "animal_type", "breed", "age", "gender", "location",
                  "description", "image", "status", "created_at"]
        read_only_fields = ["created_at"]


class AdoptionRequestSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    pet_name = serializers.CharField(source="pet.name", read_only=True)

    class Meta:
        model = AdoptionRequest
        fields = ["id", "user", "pet", "pet_name", "phone", "address", "reason",
                  "previous_pet_experience", "message", "status", "created_at"]
        read_only_fields = ["status", "created_at"]

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request is not None:
            if request.user.is_staff:
                fields["status"].read_only = False  # only admins can approve / reject
            if request.method in ("PUT", "PATCH"):
                fields["pet"].required = False  # pet cannot be changed after creation
        return fields

    def validate(self, attrs):
        request = self.context["request"]
        if self.instance is None:
            pet = attrs["pet"]
            if not pet.is_available:
                raise serializers.ValidationError({"pet": "This pet has already been adopted."})
            if AdoptionRequest.objects.filter(
                user=request.user, pet=pet, status__in=AdoptionRequest.ACTIVE_STATUSES
            ).exists():
                raise serializers.ValidationError({"pet": "You already have an active request for this pet."})
        else:
            if not request.user.is_staff and self.instance.status != AdoptionRequest.Status.PENDING:
                raise serializers.ValidationError("Only pending requests can be edited.")
            if (
                attrs.get("status") == AdoptionRequest.Status.APPROVED
                and self.instance.status != AdoptionRequest.Status.APPROVED
                and not self.instance.pet.is_available
            ):
                raise serializers.ValidationError({"status": "This pet has already been adopted."})
        return attrs

    def update(self, instance, validated_data):
        validated_data.pop("pet", None)
        return super().update(instance, validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        extra_kwargs = {"email": {"required": True}}

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
