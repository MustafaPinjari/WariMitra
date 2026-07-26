from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommunityReportViewSet

router = DefaultRouter()
router.register(r'reports', CommunityReportViewSet, basename='community-report')

urlpatterns = [
    path('', include(router.urls)),
]
