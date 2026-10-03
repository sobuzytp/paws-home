from django.contrib import admin

from .models import Favorite, Pet


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ("name", "animal_type", "breed", "age", "gender", "location", "status", "created_at")
    list_editable = ("status",)
    list_filter = ("animal_type", "gender", "status", "location")
    search_fields = ("name", "breed", "location")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "pet", "created_at")
