from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from adoptions.models import AdoptionRequest

from .models import Favorite, Pet


def home(request):
    latest = Pet.objects.filter(status=Pet.Status.AVAILABLE)[:6]
    return render(request, "home.html", {"latest_pets": latest, "total_available": Pet.objects.filter(status=Pet.Status.AVAILABLE).count()})


def pet_list(request):
    pets = Pet.objects.all()
    g = request.GET

    if g.get("name"):
        pets = pets.filter(name__icontains=g["name"].strip())
    if g.get("animal_type"):
        pets = pets.filter(animal_type=g["animal_type"])
    if g.get("breed"):
        pets = pets.filter(breed__icontains=g["breed"].strip())
    if g.get("gender"):
        pets = pets.filter(gender=g["gender"])
    if g.get("location"):
        pets = pets.filter(location__icontains=g["location"].strip())
    if g.get("status"):
        pets = pets.filter(status=g["status"])

    page_obj = Paginator(pets, 9).get_page(g.get("page"))

    params = g.copy()
    params.pop("page", None)

    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(request.user.favorites.values_list("pet_id", flat=True))

    return render(request, "pets/pet_list.html", {
        "page_obj": page_obj,
        "querystring": params.urlencode(),
        "filters": g,
        "animal_types": Pet.AnimalType.choices,
        "genders": Pet.Gender.choices,
        "statuses": Pet.Status.choices,
        "favorite_ids": favorite_ids,
    })


def pet_detail(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    has_active_request = False
    is_favorite = False
    if request.user.is_authenticated:
        has_active_request = AdoptionRequest.objects.filter(
            user=request.user, pet=pet, status__in=AdoptionRequest.ACTIVE_STATUSES
        ).exists()
        is_favorite = Favorite.objects.filter(user=request.user, pet=pet).exists()
    return render(request, "pets/pet_detail.html", {
        "pet": pet,
        "has_active_request": has_active_request,
        "is_favorite": is_favorite,
    })


@login_required
@require_POST
def toggle_favorite(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, pet=pet)
    if created:
        messages.success(request, f"{pet.name} was added to your favorites.")
    else:
        favorite.delete()
        messages.info(request, f"{pet.name} was removed from your favorites.")
    next_url = request.POST.get("next")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect("pet_detail", pk=pk)


@login_required
def favorites(request):
    items = Favorite.objects.filter(user=request.user).select_related("pet")
    return render(request, "pets/favorites.html", {"pets": [f.pet for f in items]})
