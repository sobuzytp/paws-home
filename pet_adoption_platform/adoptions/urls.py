from django.urls import path

from . import views

urlpatterns = [
    path("apply/<int:pk>/", views.apply, name="apply"),
    path("my-requests/", views.my_requests, name="my_requests"),
]
