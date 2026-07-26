from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PilgrimProfileViewSet, FamilyGroupViewSet, EmergencyContactViewSet

router = DefaultRouter()
router.register(r'profiles', PilgrimProfileViewSet, basename='pilgrim-profile')
router.register(r'families', FamilyGroupViewSet, basename='family-group')
router.register(r'emergency-contacts', EmergencyContactViewSet, basename='emergency-contact')

urlpatterns = [
    path('', include(router.urls)),
]
