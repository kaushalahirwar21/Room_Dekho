from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # APIs
    path('api/accounts/', include('accounts.urls')),
    path('api/properties/', include('rooms.urls')),
    path('api/bookings/', include('bookings.urls')),
    
    # TEMPORARY: One-time migration endpoint for Vercel deployment
    # DELETE THIS after running initial migrations
    path('__/migrate/', include('maintenance.urls')),

    # Frontend views
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('signup/', TemplateView.as_view(template_name='signup.html'), name='signup_page'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('property/<int:pk>/', TemplateView.as_view(template_name='property_detail.html'), name='property-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=str(settings.STATICFILES_DIRS[0]))

if settings.DEBUG or os.getenv('VERCEL'):
    urlpatterns += static(settings.MEDIA_URL, document_root=str(settings.MEDIA_ROOT))
