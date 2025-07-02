
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('admin/', admin.site.urls),
    path('', include('bitrive.urls')), 
    path('userprofile/', include('userprofile.urls')), 
    path('investment/', include('investment.urls')),
    path('recovery/', include('recovery.urls')),
    path('connectwallet/', include('connectwallet.urls')),  # Add this line
   
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

