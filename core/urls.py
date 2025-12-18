# core/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    # ------------------------------
    # Location Management
    # ------------------------------
    path('locations/', views.location_list, name='location_list'),
    path('locations/add/', views.location_add, name='location_add'),
    path('api/locations/create/', views.location_create_api, name='location_create_api'),

    # ------------------------------
    # User Management
    # ------------------------------
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    path('users/<int:user_id>/detail/', views.user_detail, name='user_detail'),
    path('users/permissions/', views.user_permissions, name='user_permissions'),
    path('users/<int:user_id>/edit-permissions/', views.edit_user_permissions, name='edit_user_permissions'),

    # ------------------------------
    # Profile
    # ------------------------------
    path('profile/', views.profile_view, name='profile'),

    # ------------------------------
    # Authentication
    # ------------------------------
    path('login/', views.CustomLoginView.as_view(), name='account_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='account_logout'),

    # ------------------------------
    # Session / Keepalive
    # ------------------------------
    path('session/test/', views.session_test, name='session_test'),
    path('session/keepalive/', views.session_keepalive, name='session_keepalive'),

    # ------------------------------
    # Optional Test Email / Resend API
    # ------------------------------
   
    # ------------------------------
    # Language / Translation
    # ------------------------------
    path('set-language/', views.set_language, name='set_language'),
]
