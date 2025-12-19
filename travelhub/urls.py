from rest_framework.routers import DefaultRouter
from .views import TravelSpotViewSet

router = DefaultRouter()
router.register(r'travel-spots', TravelSpotViewSet, basename='travel-spots')

urlpatterns = router.urls
