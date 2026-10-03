from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("pets/", views.pet_list, name="pet_list"),
    path("pets/<int:pk>/", views.pet_detail, name="pet_detail"),
    path("pets/<int:pk>/favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("favorites/", views.favorites, name="favorites"),
]
