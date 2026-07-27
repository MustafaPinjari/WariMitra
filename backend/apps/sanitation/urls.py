from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PublicToiletViewSet, WasteReportViewSet

router = DefaultRouter()
router.register(r'toilets', PublicToiletViewSet, basename='publictoilet')
router.register(r'waste-reports', WasteReportViewSet, basename='wastereport')

urlpatterns = [
    path('', include(router.urls)),
]
