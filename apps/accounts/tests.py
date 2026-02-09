from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RegistrationFlowTests(APITestCase):
    def test_registration_flow(self):
        payload = {'name': 'Test User', 'email': 'test@example.com'}
        response = self.client.post(reverse('register'), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('player', response.data)
