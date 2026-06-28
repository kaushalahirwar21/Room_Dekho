from django.contrib import admin
from .models import BookingRequest

class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__email', 'user__name', 'property__title')

admin.site.register(BookingRequest, BookingRequestAdmin)
