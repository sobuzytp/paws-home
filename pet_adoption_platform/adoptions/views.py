from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from pets.models import Pet

from .forms import AdoptionRequestForm
from .models import AdoptionRequest


@login_required
def apply(request, pk):
    pet = get_object_or_404(Pet, pk=pk)

    if not pet.is_available:
        messages.error(request, "This pet has already been adopted.")
        return redirect("pet_detail", pk=pet.pk)

    if AdoptionRequest.objects.filter(user=request.user, pet=pet, status__in=AdoptionRequest.ACTIVE_STATUSES).exists():
        messages.warning(request, f"You already have an active request for {pet.name}.")
        return redirect("my_requests")

    form = AdoptionRequestForm(request.POST or None, user=request.user, pet=pet)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, f"Your application for {pet.name} was submitted.")
            return redirect("my_requests")
        messages.error(request, "Please fix the errors below.")
    return render(request, "adoptions/apply.html", {"form": form, "pet": pet})


@login_required
def my_requests(request):
    items = AdoptionRequest.objects.filter(user=request.user).select_related("pet")
    return render(request, "adoptions/my_requests.html", {"requests": items})
