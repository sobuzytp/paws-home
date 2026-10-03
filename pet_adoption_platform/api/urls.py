from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .views import AdoptionRequestViewSet, PetViewSet, RegisterView

router = DefaultRouter()
router.register("pets", PetViewSet, basename="pet")
router.register("adoptions", AdoptionRequestViewSet, basename="adoption")

urlpatterns = [
    path("token/", obtain_auth_token, name="api_token"),
    path("register/", RegisterView.as_view(), name="api_register"),
    path("", include(router.urls)),
]
