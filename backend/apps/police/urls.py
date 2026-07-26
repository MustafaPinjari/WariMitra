from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PoliceStationViewSet, PatrolUnitViewSet, RoadBlockViewSet

router = DefaultRouter()
router.register(r'stations', PoliceStationViewSet)
router.register(r'patrols', PatrolUnitViewSet)
router.register(r'roadblocks', RoadBlockViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
