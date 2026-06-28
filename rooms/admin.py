from django.contrib import admin
from .models import Property, PropertyImage

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1

class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'location', 'price', 'room_type', 'bachelor_allowed', 'created_at')
    list_filter = ('room_type', 'bachelor_allowed', 'location')
    search_fields = ('title', 'description', 'location')
    inlines = [PropertyImageInline]
    actions = ['delete_fake_listings']

    def delete_fake_listings(self, request, queryset):
        queryset.delete()
    delete_fake_listings.short_description = "Delete fake/spam listings"

admin.site.register(Property, PropertyAdmin)
