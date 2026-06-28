from django.urls import path
from .views import BookingRequestCreateView, MyBookingRequestsView, UpdateBookingRequestView

urlpatterns = [
    path('request/', BookingRequestCreateView.as_view(), name='booking-request-create'),
    path('my-requests/', MyBookingRequestsView.as_view(), name='my-booking-requests'),
    path('update/<int:pk>/', UpdateBookingRequestView.as_view(), name='booking-request-update'),
]
