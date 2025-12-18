# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse, HttpResponse
from django import forms
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
import threading

from .models import Location, UserProfile
from .forms import CustomUserCreationForm, CustomUserChangeForm, UserProfileForm

from allauth.account.views import LoginView as AllauthLoginView
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
import logging

logger = logging.getLogger(__name__)

# ------------------------------
# Location Management
# ------------------------------
class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'address']

def location_list(request):
    return render(request, 'core/location_list.html', {'locations': Location.objects.all()})

def location_add(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:location_list')
    else:
        form = LocationForm()
    return render(request, 'core/location_form.html', {'form': form})

@require_POST
def location_create_api(request):
    name = request.POST.get('name')
    address = request.POST.get('address', '')
    if not name:
        return JsonResponse({'ok': False, 'error': 'name required'}, status=400)
    loc = Location.objects.create(name=name, address=address)
    return JsonResponse({'ok': True, 'id': loc.id, 'name': loc.name})


# ------------------------------
# User Management
# ------------------------------
def is_admin_user(user):
    return hasattr(user, 'profile') and user.profile.role == 'admin'

@login_required
@user_passes_test(is_admin_user)
def user_list(request):
    users = User.objects.all().select_related('profile').order_by('username')
    role_filter = request.GET.get('role', '')
    location_filter = request.GET.get('location', '')

    if role_filter:
        users = users.filter(profile__role=role_filter)
    if location_filter:
        users = users.filter(profile__assigned_location_id=location_filter)

    context = {
        'users': users,
        'roles': UserProfile.USER_ROLES,
        'locations': Location.objects.filter(is_active=True),
        'role_filter': role_filter,
        'location_filter': location_filter,
    }
    return render(request, 'core/user_list.html', context)

@login_required
@user_passes_test(is_admin_user)
def user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('core:user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'core/user_form.html', {'form': form, 'title': 'Create New User'})

@login_required
@user_passes_test(is_admin_user)
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('core:user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'core/user_form.html', {'form': form, 'title': f'Edit User: {user.username}', 'user': user})

@login_required
@user_passes_test(is_admin_user)
def user_toggle_active(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, 'You cannot deactivate your own account!')
    else:
        user.is_active = not user.is_active
        user.save()
        messages.success(request, f'User {user.username} {"activated" if user.is_active else "deactivated"} successfully!')
    return redirect('core:user_list')

@login_required
@user_passes_test(is_admin_user)
def user_detail(request, user_id):
    user = get_object_or_404(User.objects.select_related('profile'), id=user_id)
    return render(request, 'core/user_detail.html', {'user_obj': user, 'title': f'User Details: {user.username}'})

@login_required
def user_permissions(request):
    if not request.user.profile.role == 'admin':
        messages.error(request, "You don't have permission to manage user permissions.")
        return redirect('core:profile')
    users = User.objects.select_related('profile').all().order_by('username')
    return render(request, 'core/user_permissions.html', {'users': users})

@login_required
def edit_user_permissions(request, user_id):
    if not request.user.profile.role == 'admin':
        messages.error(request, "You don't have permission to edit user permissions.")
        return redirect('core:profile')
    
    user = get_object_or_404(User, id=user_id)
    profile = user.profile

    if request.method == 'POST':
        profile.role = request.POST.get('role', 'staff')
        profile.assigned_location_id = request.POST.get('assigned_location') or None
        profile.can_manage_inventory = 'can_manage_inventory' in request.POST
        profile.can_manage_sales = 'can_manage_sales' in request.POST
        profile.can_manage_purchases = 'can_manage_purchases' in request.POST
        profile.can_manage_customers = 'can_manage_customers' in request.POST
        profile.can_view_reports = 'can_view_reports' in request.POST
        profile.can_manage_users = 'can_manage_users' in request.POST
        profile.save()
        messages.success(request, f"Permissions updated for {user.username}")
        return redirect('core:user_permissions')

    locations = Location.objects.all()
    return render(request, 'core/edit_user_permissions.html', {'edit_user': user, 'profile': profile, 'locations': locations})


# ------------------------------
# Profile (Auto-verified)
# ------------------------------
@login_required
def profile_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    # Auto-verify email
    profile.email_verified = True
    profile.save()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('core:profile')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'core/profile.html', {'form': form, 'user': user, 'profile': profile, 'title': 'My Profile'})


# ------------------------------
# Authentication (Username only)
# ------------------------------
class CustomLoginView(AllauthLoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user

        # Auto-verify profile
        if hasattr(user, 'profile'):
            user.profile.email_verified = True
            user.profile.save()

        messages.success(self.request, f"Welcome back, {user.username}!")
        return response


# ------------------------------
# Session & Keepalive
# ------------------------------
@require_http_methods(["GET"])
def session_test(request):
    return JsonResponse({
        'status': 'success',
        'user': request.user.username if request.user.is_authenticated else 'anonymous',
        'session_active': True
    })

@require_http_methods(["POST"])
@csrf_exempt
def session_keepalive(request):
    return JsonResponse({
        'status': 'success',
        'message': 'Session kept alive',
        'timestamp': timezone.now().isoformat()
    })


# ------------------------------
# Email / Resend API Testing (optional)
# ------------------------------
def test_email_setup(request):
    try:
        email = EmailMessage(
            subject='🧪 Teba System - Email Test',
            body='Test email. If received, email setup works.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ADMIN_EMAIL],
        )
        email.send(fail_silently=False)
        return JsonResponse({'status': 'success', 'message': '✅ Test email sent successfully!'})
    except Exception as e:
        logger.error(f"Test email failed: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)})

# Resend API test (still works if needed)
def test_resend_api(request):
    from .views import send_verification_email
    try:
        success = send_verification_email(settings.ADMIN_EMAIL, '123456', 'test')
        return HttpResponse("✅ Resend API test successful!" if success else "❌ Resend API test failed")
    except Exception as e:
        return HttpResponse(f"❌ Resend API test error: {e}")


# ------------------------------
# Language Switching
# ------------------------------
from django.utils import translation

def set_language(request):
    lang = request.GET.get('lang') or request.POST.get('language')
    if lang in ['en', 'fr']:
        request.session['django_language'] = lang
        response = redirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie('preferred_language', lang, max_age=365*24*60*60)
        translation.activate(lang)
        return response
    return redirect('/')
