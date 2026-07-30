from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MissingPersonReportViewSet

router = DefaultRouter()
router.register(r'reports', MissingPersonReportViewSet, basename='missing-person-report')

urlpatterns = [
    path('', include(router.urls)),
]
