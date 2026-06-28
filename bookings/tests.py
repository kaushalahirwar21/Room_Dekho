from django.core import mail
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from rooms.models import Property
from bookings.models import BookingRequest


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    EMAIL_HOST_USER='noreply@roomdekho.test',
)
class BookingRequestTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='ownerpass123',
            name='Owner User',
            role='Owner',
            is_verified=True,
        )
        self.seeker = User.objects.create_user(
            email='seeker@example.com',
            password='seekerpass123',
            name='Seeker User',
            mobile_number='9876543210',
            role='Seeker',
            is_verified=True,
        )
        self.property = Property.objects.create(
            owner=self.owner,
            title='Near MP Nagar',
            description='Clean room with wifi',
            price='4500.00',
            location='MP Nagar',
            room_type='1RK',
            bachelor_allowed=True,
        )

    def test_seeker_can_create_request_and_owner_gets_email(self):
        self.client.force_authenticate(user=self.seeker)

        response = self.client.post(
            '/api/bookings/request/',
            {'property': self.property.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookingRequest.objects.count(), 1)
        self.assertEqual(mail.outbox[0].to, [self.owner.email])
        self.assertIn(self.property.title, mail.outbox[0].subject)

    def test_owner_cannot_request_own_property(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            '/api/bookings/request/',
            {'property': self.property.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(BookingRequest.objects.count(), 0)
