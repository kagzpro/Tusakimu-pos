# core/admin.py
from django.contrib import admin
from .models import Location, ExchangeRate, UserProfile  # Add UserProfile import

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'is_active', 'phone')
    search_fields = ('name', 'address')
    list_filter = ('is_active',)

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('rate', 'updated_by', 'updated_at')
    readonly_fields = ('updated_at',)
    list_filter = ('updated_at',)

# ADD THIS - Register UserProfile to admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'assigned_location', 'role', 'phone', 'email_verified')
    list_filter = ('assigned_location', 'role', 'email_verified', 'can_manage_inventory')
    search_fields = ('user__username', 'user__email', 'phone')
    raw_id_fields = ('user',)  # Better for performance with many users
    
    # Fields to display in the form
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role', 'assigned_location')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address')
        }),
        ('Permissions', {
            'fields': ('can_manage_inventory', 'can_manage_sales', 'can_manage_purchases', 
                      'can_manage_customers', 'can_view_reports', 'can_manage_users')
        }),
        ('Verification', {
            'fields': ('email_verified',)
        }),
    )
    
    # Enable editing assigned_location directly in the list view
    list_editable = ('assigned_location', 'role')
    
    # Actions for bulk updates
    actions = ['assign_default_location']
    
    def assign_default_location(self, request, queryset):
        """Bulk assign a default location to selected profiles"""
        default_location = Location.objects.first()
        if default_location:
            updated = queryset.update(assigned_location=default_location)
            self.message_user(request, f'Assigned {updated} profiles to {default_location.name}')
        else:
            self.message_user(request, 'No location found to assign!', level='ERROR')
    assign_default_location.short_description = "Assign default location to selected profiles"