from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.status import *

class ManagerAuthTest(APITestCase):
    def setUp(self):
        self.manager_register = reverse('manager-register')
        self.manager_login = reverse('manager-login')
        self.allData= {
            'email': 'manager@email.com',
            'first_name': 'manager',
            'last_name': 'last',
            'password': 'manager',
            # 'language': 'manager',
            'offer': 'Selling Furniture',
            'selling_point': 'Quality Furniture',
            'faq': 'None',
        }
        self.login_data = {
            'email' : self.allData['email'],
            'password': self.allData['password'],
        }

    def test_createLogin(self):
        response = self.client.post(self.manager_register, self.allData)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        response = self.client.post(self.manager_login, self.login_data)
        self.assertEqual(response.status_code, HTTP_200_OK)
