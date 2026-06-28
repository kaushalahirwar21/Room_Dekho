from django.db import models
from django.conf import settings

class Property(models.Model):
    ROOM_TYPES = (
        ('1RK', '1RK'),
        ('1BHK', '1BHK'),
        ('2BHK', '2BHK'),
        ('PG', 'PG'),
        ('Hostel', 'Hostel'),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    room_type = models.CharField(max_length=50, choices=ROOM_TYPES)
    bachelor_allowed = models.BooleanField(default=True)
    
    # New specification fields
    floor = models.CharField(max_length=50, blank=True, null=True)
    room_size = models.CharField(max_length=50, blank=True, null=True)
    bathroom = models.CharField(max_length=50, blank=True, null=True)
    furnishing = models.CharField(max_length=50, blank=True, null=True)
    parking = models.CharField(max_length=50, blank=True, null=True)
    available_from = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    
    def __str__(self):
        return f"{self.property.title} - Image"
