from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('accounts/', include('allauth.urls')),
    path('', include(('core.urls', 'core'), namespace='core')),
    path('organisers/', include(('organisers.urls', 'organisers'), namespace='organisers')),
    path('api/', include(('api.urls', 'api'), namespace="api")),
]
