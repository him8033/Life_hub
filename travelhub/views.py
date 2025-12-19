from rest_framework import viewsets, permissions
from django.utils import timezone
from .models import TravelSpot
from .serializers import TravelSpotSerializer

# Optional: Public GET, Private POST/PUT/DELETE
class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Allow GET requests for anyone.
    POST, PUT, DELETE require authentication.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class TravelSpotViewSet(viewsets.ModelViewSet):
    serializer_class = TravelSpotSerializer
    permission_classes = [permissions.IsAuthenticated]  # Change to IsAuthenticatedOrReadOnly if you want public GET
    queryset = TravelSpot.objects.filter(deleted_at__isnull=True).order_by("name")

    def perform_destroy(self, instance):
        """
        Soft delete: mark as inactive + set deleted_at
        """
        instance.is_active = False
        instance.deleted_at = timezone.now()
        instance.save()
