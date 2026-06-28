from django.urls import path
from .views import PropertyListCreateView, PropertyDetailView, AdminDeletePropertyView

urlpatterns = [
    path('', PropertyListCreateView.as_view(), name='property-list-create'),
    path('<int:pk>/', PropertyDetailView.as_view(), name='property-detail'),
    path('admin/delete/<int:pk>/', AdminDeletePropertyView.as_view(), name='admin-delete-property'),
]
