from django.contrib import admin
from .models import User, OTP

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'role', 'is_verified', 'is_active', 'is_staff')
    list_filter = ('role', 'is_verified', 'is_active')
    search_fields = ('email', 'name', 'mobile_number')
    actions = ['ban_users']

    def ban_users(self, request, queryset):
        queryset.update(is_active=False)
    ban_users.short_description = "Ban selected users"

admin.site.register(User, UserAdmin)
admin.site.register(OTP)
