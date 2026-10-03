import django_filters
from rest_framework import filters, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from adoptions.models import AdoptionRequest
from pets.models import Pet

from .serializers import AdoptionRequestSerializer, PetSerializer, RegisterSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """Anyone can read pets; only staff can create / update / delete."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class PetFilter(django_filters.FilterSet):
    animal_type = django_filters.CharFilter(lookup_expr="iexact")
    gender = django_filters.CharFilter(lookup_expr="iexact")
    status = django_filters.CharFilter(lookup_expr="iexact")
    breed = django_filters.CharFilter(lookup_expr="icontains")
    location = django_filters.CharFilter(lookup_expr="icontains")
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Pet
        fields = ["name", "animal_type", "breed", "gender", "location", "status"]


class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all().order_by("-created_at")
    serializer_class = PetSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PetFilter
    search_fields = ["name", "animal_type", "breed", "location", "description"]
    ordering_fields = ["created_at", "age", "name"]


class AdoptionRequestViewSet(viewsets.ModelViewSet):
    """Users see and edit only their own requests. Staff can see all and change status."""

    serializer_class = AdoptionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "put", "patch", "head", "options"]

    def get_queryset(self):
        qs = AdoptionRequest.objects.select_related("user", "pet")
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"username": user.username, "token": token.key}, status=status.HTTP_201_CREATED)
