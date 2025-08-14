from rest_framework.test import APITestCase
from dotenv import load_dotenv
import os
from django.urls import reverse
import json
import datetime
from rest_framework.status import *
from apps.users.models import AgentModel, LeadModel, LeadEmailModel

load_dotenv(override=True)

# Create your tests here.

class emailTest(APITestCase):
    def setUp(self):
        self.from_email = os.getenv('EMAIL')
        self.password = os.getenv('EMAIL_APP_PASSWORD')
        self.to_email = os.getenv('TO_EMAIL')
        self.fetch_email_url = reverse('fetch-email')
        self.send_email_url = reverse('send-email')
        self.search_email_url = reverse('search-email')
        self.register_agent_url = reverse('agent-register')
        self.register_lead_url = reverse('lead-register')

        self.agent_data = {
            'email': self.from_email,
            'first_name': 'user',
            'last_name': 'cool',
            'password': 'password',
            'phone': '+12345678',
            'smtp_email': self.from_email,
            'smtp_password': self.password,
        }

        # register lead data
        self.lead_data = {
            'name': 'lead_user',
            'company': 'company',
            'destination': 'ceo',
            'assign_to': self.from_email,
            'city': 'London',
            'state': 'State',
            'zip_code': '12345',
            'address': 'Adress Here',
            'status': 'in_progress',
            'lead_phone': [{'phone_number': '+123456', 'type': 'personal'}],
            'lead_email': [{'email': self.to_email, 'type': 'personal'}]
        }


        self.data_emailPass = {
            'email': self.from_email,
            'password': self.password,
        }

        self.data_emailPassTo = {
            'to_email': [self.to_email, 'hello@info.n8n.io']
        }

        self.data_all = {
            'to_email': self.to_email,
            'subject': 'Subject Heading here',
            'body': 'body of the email heading here...'

        }

    def test_search_email(self):
        response = self.client.post(self.register_agent_url, self.agent_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        response = self.client.post(self.register_lead_url, self.lead_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        # login as agent
        agent_login_url = reverse('agent-login')
        agent_login_data = {
            'email': self.from_email,
            'password': self.agent_data['password']
        }
        response = self.client.post(agent_login_url, agent_login_data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        access = response.data['access']
        refresh = response.data['refresh']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

        response = self.client.post(self.search_email_url, self.data_emailPassTo, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.data_emailPassTo['to_email'] = self.to_email
        response = self.client.post(self.search_email_url, self.data_emailPassTo, format='json')
        self.assertEqual(response.status_code, HTTP_200_OK)


    def test_send_email(self):
        response = self.client.post(self.register_agent_url, self.agent_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        response = self.client.post(self.register_lead_url, self.lead_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        # login as agent
        agent_login_url = reverse('agent-login')
        agent_login_data = {
            'email': self.from_email,
            'password': self.agent_data['password']
        }
        response = self.client.post(agent_login_url, agent_login_data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        access = response.data['access']
        refresh = response.data['refresh']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        response = self.client.post(self.send_email_url, self.data_all, format='json')

        self.assertEqual(response.status_code, HTTP_200_OK)

        # wrong to_email
        self.data_all['to_email'] = 'hello@info.n8n.io'
        response = self.client.post(self.send_email_url, self.data_all, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'You can only send emails to leads assigned to you.')


        


        
    
    def test_fetch_email(self):
        response = self.client.post(self.register_agent_url, self.agent_data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        response = self.client.post(self.register_lead_url, self.lead_data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        # login as agent
        agent_login_url = reverse('agent-login')
        agent_login_data = {
            'email': self.from_email,
            'password': self.agent_data['password']
        }
        response = self.client.post(agent_login_url, agent_login_data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        access = response.data['access']
        refresh = response.data['refresh']

        # send access to Fetch Inbox
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        response = self.client.post(self.fetch_email_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        


        
