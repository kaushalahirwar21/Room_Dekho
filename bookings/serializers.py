from rest_framework import serializers
from .models import BookingRequest
from rooms.serializers import PropertySerializer

class BookingRequestSerializer(serializers.ModelSerializer):
    property_details = PropertySerializer(source='property', read_only=True)
    seeker_name = serializers.CharField(source='user.name', read_only=True)
    seeker_email = serializers.EmailField(source='user.email', read_only=True)
    seeker_mobile = serializers.CharField(source='user.mobile_number', read_only=True)

    class Meta:
        model = BookingRequest
        fields = ('id', 'user', 'seeker_name', 'seeker_email', 'seeker_mobile', 'property', 'property_details', 'status', 'created_at')
        read_only_fields = ('id', 'user', 'status', 'created_at')
