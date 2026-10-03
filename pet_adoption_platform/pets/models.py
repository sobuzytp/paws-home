from django.conf import settings
from django.db import models


class Pet(models.Model):
    class AnimalType(models.TextChoices):
        DOG = "Dog"
        CAT = "Cat"
        BIRD = "Bird"
        RABBIT = "Rabbit"
        OTHER = "Other"

    class Gender(models.TextChoices):
        MALE = "Male"
        FEMALE = "Female"

    class Status(models.TextChoices):
        AVAILABLE = "Available"
        ADOPTED = "Adopted"

    name = models.CharField(max_length=100)
    animal_type = models.CharField(max_length=20, choices=AnimalType.choices, default=AnimalType.DOG)
    breed = models.CharField(max_length=100)
    age = models.PositiveSmallIntegerField(help_text="Age in years")
    gender = models.CharField(max_length=10, choices=Gender.choices)
    location = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="pets/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.AVAILABLE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.animal_type})"

    @property
    def is_available(self):
        return self.status == self.Status.AVAILABLE


class Favorite(models.Model):
    """Bonus: users can save pets to favorites."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["user", "pet"], name="unique_favorite")]

    def __str__(self):
        return f"{self.user} ♥ {self.pet}"
