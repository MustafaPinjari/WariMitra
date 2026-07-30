from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PilgrimProfileViewSet, FamilyGroupViewSet,
    EmergencyContactViewSet, update_location, family_locations
)

router = DefaultRouter()
router.register(r'profiles', PilgrimProfileViewSet, basename='pilgrim-profile')
router.register(r'families', FamilyGroupViewSet, basename='family-group')
router.register(r'emergency-contacts', EmergencyContactViewSet, basename='emergency-contact')

urlpatterns = [
    path('', include(router.urls)),
    path('update-location/', update_location, name='update-location'),
    path('family-locations/', family_locations, name='family-locations'),
]
