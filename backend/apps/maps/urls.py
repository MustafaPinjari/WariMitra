from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServicePointViewSet

router = DefaultRouter()
router.register(r'services', ServicePointViewSet, basename='servicepoint')

urlpatterns = [
    path('', include(router.urls)),
]
