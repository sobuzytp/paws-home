from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.db.models import Q

from pets.models import Pet

phone_validator = RegexValidator(r"^\+?[0-9\- ]{7,20}$", "Enter a valid phone number (digits, spaces, - and optional leading +).")


class AdoptionRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending"
        APPROVED = "Approved"
        REJECTED = "Rejected"

    # A request counts as "active" while it is pending or approved.
    ACTIVE_STATUSES = ("Pending", "Approved")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="adoption_requests")
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="adoption_requests")
    phone = models.CharField(max_length=20, validators=[phone_validator])
    address = models.TextField()
    reason = models.TextField(verbose_name="Why do you want this pet?")
    previous_pet_experience = models.BooleanField(default=False, verbose_name="Have you owned a pet before?")
    message = models.TextField(blank=True, verbose_name="Additional message")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # Rule 2: one user cannot have more than one active request for the same pet.
            models.UniqueConstraint(
                fields=["user", "pet"],
                condition=Q(status__in=["Pending", "Approved"]),
                name="unique_active_request_per_user_pet",
            )
        ]

    def __str__(self):
        return f"{self.user} -> {self.pet} ({self.status})"

    def clean(self):
        if not (self.user_id and self.pet_id):
            return
        if self._state.adding:
            # Rule 1: only available pets can be adopted.
            if self.pet.status != Pet.Status.AVAILABLE:
                raise ValidationError("This pet has already been adopted.")
            # Rule 2: no duplicate active request.
            duplicate = AdoptionRequest.objects.filter(
                user_id=self.user_id, pet_id=self.pet_id, status__in=self.ACTIVE_STATUSES
            ).exists()
            if duplicate:
                raise ValidationError("You already have an active request for this pet.")
        elif self.status == self.Status.APPROVED and self.pet.status == Pet.Status.ADOPTED:
            # Cannot approve a second request for a pet that is already adopted.
            already_approved_here = AdoptionRequest.objects.filter(pk=self.pk, status=self.Status.APPROVED).exists()
            if not already_approved_here:
                raise ValidationError("This pet has already been adopted, so this request cannot be approved.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            # Rule 3: approving a request marks the pet as adopted and
            # rejects the other pending requests for the same pet.
            if self.status == self.Status.APPROVED:
                Pet.objects.filter(pk=self.pet_id).update(status=Pet.Status.ADOPTED)
                AdoptionRequest.objects.filter(pet_id=self.pet_id, status=self.Status.PENDING).exclude(
                    pk=self.pk
                ).update(status=self.Status.REJECTED)
