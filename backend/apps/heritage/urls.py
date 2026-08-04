from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaintViewSet, AbhangViewSet, PilgrimageMilestoneViewSet, HeritageAudioUploadView

router = DefaultRouter()
router.register(r'saints', SaintViewSet, basename='saint')
router.register(r'abhangs', AbhangViewSet, basename='abhang')
router.register(r'milestones', PilgrimageMilestoneViewSet, basename='milestone')

urlpatterns = [
    path('upload/', HeritageAudioUploadView.as_view(), name='heritage-upload'),
    path('', include(router.urls)),
]
