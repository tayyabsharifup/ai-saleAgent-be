from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.status import *

class AgentAuthTest(APITestCase):

    def setUp(self):
        self.register_url = reverse('agent-register')
        self.login_url = reverse('agent-login') 

        self.data = {
            'email': 'user@email.com',
            'first_name': 'user',
            'last_name': 'cool',
            'password': 'password'
        }
        
        self.login_data = {
            'email': 'user@email.com',
            'password': 'password'
        }
        self.all_data = {
            'email': 'user@email.com',
            'first_name': 'user',
            'last_name': 'cool',
            'password': 'password',
            'phone': '+12345678',
            'smtp_email': 'hello@email.com',
            'smtp_password': '12345'
        }
    def test_create_login(self):
        response = self.client.post(self.register_url, self.all_data)
        self.assertEqual(response.status_code , HTTP_201_CREATED)

