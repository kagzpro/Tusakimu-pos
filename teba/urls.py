# teba/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.shortcuts import redirect

from core.views import CustomLoginView


urlpatterns = [
    path('admin/', admin.site.urls),

    # Language switch endpoint (MUST be near the top)
    path('i18n/', include('django.conf.urls.i18n')),

    # Apps
    path('', include('transactions.urls', namespace='transactions')),
    path('core/', include('core.urls', namespace='core')),
    path('inventory/', include('inventory.urls', namespace='inventory')),

    # Override Allauth login
    path('accounts/login/', CustomLoginView.as_view(), name='account_login'),

    # Allauth
    path('accounts/', include('allauth.urls')),

    # Home page
    path('home/', TemplateView.as_view(template_name='home.html'), name='home'),

    # Root redirect
    path('', lambda request: redirect('transactions:home')),
     path('rosetta/', include('rosetta.urls')),
]
