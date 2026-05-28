# teba/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from django.shortcuts import redirect

from core.views import CustomLoginView


urlpatterns = [
    # Root redirect - goes to login page
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False), name='home'),
    
    path('admin/', admin.site.urls),

    # Language switch endpoint (MUST be near the top)
    path('i18n/', include('django.conf.urls.i18n')),

    # Apps
    path('transactions/', include('transactions.urls', namespace='transactions')),
    path('core/', include('core.urls', namespace='core')),
    path('inventory/', include('inventory.urls', namespace='inventory')),

    # Override Allauth login
    path('accounts/login/', CustomLoginView.as_view(), name='account_login'),

    # Allauth
    path('accounts/', include('allauth.urls')),

    # Home page
    path('home/', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # Rosetta (translations - optional)
    path('rosetta/', include('rosetta.urls')),
]
