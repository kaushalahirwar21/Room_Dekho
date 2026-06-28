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
    owner = booking_request.property.owner
    seeker = booking_request.user

    if not owner.email:
        return

    subject = f"New booking request for {booking_request.property.title}"
    message = (
        f"Hello {owner.name},\n\n"
        f"You have received a new booking request on Room Dekho.\n\n"
        f"Property: {booking_request.property.title}\n"
        f"Location: {booking_request.property.location}\n"
        f"Price: Rs. {booking_request.property.price}/month\n\n"
        f"Seeker details:\n"
        f"Name: {seeker.name}\n"
        f"Email: {seeker.email}\n"
        f"Mobile: {seeker.mobile_number or 'Not provided'}\n\n"
        f"Please log in to your dashboard to review this request.\n\n"
        f"Thank you,\n"
        f"Room Dekho Team"
    )

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [owner.email],
        fail_silently=True,
    )
