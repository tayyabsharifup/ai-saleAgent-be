from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.status import *

class AdminAuthTest(APITestCase):
    def setUp(self):
        self.admin_register = reverse('admin-register')
        self.admin_login = reverse('admin-login')
        self.allData= {
            'email': 'admin@email.com',
            'first_name': 'admin',
            'last_name': 'user',
            'password': 'adminpassword',
        }
        self.login_data = {
            'email' : self.allData['email'],
            'password': self.allData['password'],
        }

    def test_createLogin(self):
        response = self.client.post(self.admin_register, self.allData)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        response = self.client.post(self.admin_login, self.login_data)
        self.assertEqual(response.status_code, HTTP_200_OK)
