from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/pilgrims/', include('apps.pilgrims.urls')),
    path('api/v1/sos/', include('apps.sos.urls')),
    path('api/v1/community/', include('apps.community.urls')),
    path('api/v1/medical/', include('apps.medical.urls')),
    path('api/v1/police/', include('apps.police.urls')),
    path('api/v1/temple/', include('apps.temple.urls')),
    path('api/v1/ngo/', include('apps.ngo.urls')),
    path('api/v1/ai/', include('apps.ai_predictions.urls')),
    path('api/v1/heritage/', include('apps.heritage.urls')),
    path('api/v1/lost-found/', include('apps.lost_found.urls')),
    path('api/v1/sanitation/', include('apps.sanitation.urls')),
    path('api/v1/missing-person/', include('apps.missing_person.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
