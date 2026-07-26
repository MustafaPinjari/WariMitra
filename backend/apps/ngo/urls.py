from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResourceViewSet, InventoryViewSet, DistributionViewSet, DonationViewSet

router = DefaultRouter()
router.register(r'resources', ResourceViewSet)
router.register(r'inventory', InventoryViewSet)
router.register(r'distributions', DistributionViewSet)
router.register(r'donations', DonationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
