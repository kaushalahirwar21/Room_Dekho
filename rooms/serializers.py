from rest_framework import serializers
from django.templatetags.static import static
from .models import Property, PropertyImage

class PropertyImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = PropertyImage
        fields = ('id', 'image')

    def get_image(self, obj):
        return build_image_url(obj.image, self.context.get('request'))

class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    first_image = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = (
            'id', 'owner', 'owner_name', 'title', 'description', 'price', 
            'location', 'room_type', 'bachelor_allowed', 'created_at', 
            'images', 'first_image',
            'floor', 'room_size', 'bathroom', 'furnishing', 'parking', 'available_from'
        )
        read_only_fields = ('id', 'owner', 'created_at')

    def get_first_image(self, obj):
        first = obj.images.first()
        if first:
            return build_image_url(first.image, self.context.get('request'))
        return None

    def create(self, validated_data):
        uploaded_images = self.context.get('request').FILES.getlist('uploaded_images', [])
        property_obj = Property.objects.create(**validated_data)
        
        for image in uploaded_images:
            if image:
                PropertyImage.objects.create(property=property_obj, image=image)
        
        return property_obj

    def update(self, instance, validated_data):
        uploaded_images = self.context.get('request').FILES.getlist('uploaded_images', [])
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        for image in uploaded_images:
            if image:
                PropertyImage.objects.create(property=instance, image=image)
            
        return instance


def build_image_url(image_field, request):
    if not image_field or not image_field.name:
        return build_static_url('images/logo.png', request)

    try:
        image_url = image_field.url
    except Exception:
        return build_static_url('images/logo.png', request)

    if request:
        return request.build_absolute_uri(image_url)
    return image_url


def build_static_url(path, request):
    asset_url = static(path)
    if request:
        return request.build_absolute_uri(asset_url)
    return asset_url
