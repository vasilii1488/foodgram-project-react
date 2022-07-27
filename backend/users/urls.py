from django.conf.urls import include
from django.urls import path

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('api-auth/', include('rest_framework.urls')),
]