from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
import os

from rooms.views import PropertyWebDetailView
from accounts.views import sitemap_view, robots_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # APIs
    path('api/accounts/', include('accounts.urls')),
    path('api/auth/', include('accounts.urls')),
    path('api/properties/', include('rooms.urls')),
    path('api/bookings/', include('bookings.urls')),
    
    # TEMPORARY: One-time migration endpoint for Vercel deployment
    # DELETE THIS after running initial migrations
    path('__/migrate/', include('maintenance.urls')),

    # Frontend views
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('signup/', TemplateView.as_view(template_name='signup.html'), name='signup_page'),
    path('forgot-password/', TemplateView.as_view(template_name='forgot_password.html'), name='forgot_password_page'),
    path('email-config/', TemplateView.as_view(template_name='email_config.html'), name='email_config_page'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('privacy-policy/', TemplateView.as_view(template_name='privacy_policy.html'), name='privacy_policy'),
    path('terms-conditions/', TemplateView.as_view(template_name='terms_conditions.html'), name='terms_conditions'),
    path('property/<int:pk>/', PropertyWebDetailView.as_view(), name='property-detail'),
    
    # Sitemaps and Robots
    path('sitemap.xml', sitemap_view, name='sitemap'),
    path('robots.txt', robots_view, name='robots'),
]

handler404 = 'accounts.views.custom_404_view'
handler500 = 'accounts.views.custom_500_view'

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=str(settings.STATICFILES_DIRS[0]))

if settings.DEBUG or os.getenv('VERCEL'):
    urlpatterns += static(settings.MEDIA_URL, document_root=str(settings.MEDIA_ROOT))
