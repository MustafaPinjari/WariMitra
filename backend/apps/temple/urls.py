from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TempleQueueViewSet, DarshanSlotViewSet, QueueMovementViewSet

router = DefaultRouter()
router.register(r'queues', TempleQueueViewSet)
router.register(r'slots', DarshanSlotViewSet)
router.register(r'movements', QueueMovementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
