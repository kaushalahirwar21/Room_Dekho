from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.conf import settings
from .models import BookingRequest
from .serializers import BookingRequestSerializer

class BookingRequestCreateView(generics.CreateAPIView):
    serializer_class = BookingRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'Seeker':
            raise PermissionDenied("Only Seekers can make booking requests.")
        
        property_obj = serializer.validated_data['property']
        if property_obj.owner == self.request.user:
            raise ValidationError("You cannot send a request for your own property.")

        if BookingRequest.objects.filter(user=self.request.user, property=property_obj).exists():
            raise ValidationError("You have already sent a request for this property.")

        booking_request = serializer.save(user=self.request.user)
        notify_owner_about_booking_request(booking_request)

class MyBookingRequestsView(generics.ListAPIView):
    serializer_class = BookingRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Owner':
            # For owners, return all booking requests made TO properties they own
            return BookingRequest.objects.filter(property__owner=user).order_by('-created_at')
        elif user.role == 'Seeker':
            # For seekers, return all their booking requests
            return BookingRequest.objects.filter(user=user).order_by('-created_at')
        return BookingRequest.objects.none()

class UpdateBookingRequestView(generics.UpdateAPIView):
    serializer_class = BookingRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = BookingRequest.objects.all()

    def perform_update(self, serializer):
        booking = self.get_object()
        if self.request.user != booking.property.owner:
            raise PermissionDenied("Only the property owner can update the status.")
            
        # Only allow updating the status
        status = self.request.data.get('status')
        if status not in ['Pending', 'Approved', 'Rejected']:
            raise ValidationError("Invalid status.")
            
        serializer.save(status=status)


def notify_owner_about_booking_request(booking_request):
    try:
        owner = booking_request.property.owner
        seeker = booking_request.user

        if not owner.email:
            return

        from accounts.email_service import EmailService
        EmailService.send_booking_notification(
            owner_email=owner.email,
            owner_name=owner.name,
            seeker_name=seeker.name,
            seeker_email=seeker.email,
            seeker_mobile=seeker.mobile_number or 'Not provided',
            property_title=booking_request.property.title,
            property_location=booking_request.property.location,
            property_price=booking_request.property.price
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send booking notification email: {str(e)}")
