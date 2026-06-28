from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from .models import Property
from .serializers import PropertySerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class PropertyListCreateView(generics.ListCreateAPIView):
    serializer_class = PropertySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        queryset = Property.objects.all().order_by('-created_at')
        
        # Filtering logic
        location = self.request.query_params.get('location', None)
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        room_type = self.request.query_params.get('room_type', None)
        bachelor_allowed = self.request.query_params.get('bachelor_allowed', None)

        if location:
            queryset = queryset.filter(location__icontains=location)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if room_type:
            queryset = queryset.filter(room_type=room_type)
        if bachelor_allowed is not None:
            bachelor_allowed = str(bachelor_allowed).lower() in ['true', '1', 't']
            queryset = queryset.filter(bachelor_allowed=bachelor_allowed)

        # For Owner dashboard
        owner_id = self.request.query_params.get('owner', None)
        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)

        return queryset

    def perform_create(self, serializer):
        if self.request.user.role != 'Owner':
            raise PermissionDenied("Only Owners can list properties.")
        serializer.save(owner=self.request.user)

class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsOwnerOrReadOnly]

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

class AdminDeletePropertyView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        try:
            prop = Property.objects.get(pk=pk)
            prop.delete()
            return Response({"message": "Property deleted successfully."}, status=status.HTTP_200_OK)
        except Property.DoesNotExist:
            return Response({"error": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

from django.views.generic import DetailView

class PropertyWebDetailView(DetailView):
    model = Property
    template_name = 'property_detail.html'
    context_object_name = 'property'
