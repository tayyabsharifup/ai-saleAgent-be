from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.status import *
from apps.users.models.lead_model import LeadModel


class LeadAuthTest(APITestCase):
    def setUp(self):
        self.agent_register = reverse('agent-register')
        self.agent_login = reverse('agent-login')
        self.lead_register = reverse('lead-register')

        self.agent_data = {
            'email': 'user@email.com',
            'first_name': 'user',
            'last_name': 'cool',
            'password': 'password',
            'phone': '+12345678',
            'smtp_email': 'hello@email.com',
            'smtp_password': '12345'
        }

        self.agent_login_data = {
            'email': self.agent_data['email'],
            'password': self.agent_data['password']
        }

        self.lead_data = {
            'name': 'lead_user',
            'company': 'company',
            'destination': 'ceo',
            'assign_to': 'user@email.com',
            'city': 'London',
            'state': 'State',
            'zip_code': '12345',
            'address': 'Adress Here',
            'status': 'in_progress',  # 'in_progress', 'not_initiated', 'over_due', 'converted'
            # 'assign_date':
            'lead_phone': [{'phone_number': '+123456', 'type': 'personal'}, {'phone_number': '+123456', }],
            'lead_email': [{'email': 'email@email.com', 'type': 'personal'}, {'email': 'email2@email.com'}]
        }

        self.unassigned_lead_data = {
            'name': 'Unassigned Lead',
            'company': 'Unassigned Company',
            'destination': 'Unassigned Destination',
            'city': 'Unassigned City',
            'state': 'Unassigned State',
            'zip_code': '00000',
            'address': 'Unassigned Address',
            'status': 'not_initiated'
        }
    
    def test_create(self):
        response = self.client.post(self.agent_register, self.agent_data)
        if response.status_code != HTTP_201_CREATED:
            print(response.data)
        self.assertEqual(response.status_code , HTTP_201_CREATED)

        response = self.client.post(self.agent_login, self.agent_login_data)
        self.assertEqual( response.status_code , HTTP_200_OK)

        response = self.client.post(self.lead_register, self.lead_data)
        if response.status_code != HTTP_201_CREATED:
            print(response.data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_update_lead(self):
        response = self.client.post(self.agent_register, self.agent_data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        response = self.client.post(self.lead_register, self.lead_data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        
        lead = LeadModel.objects.first()
        self.assertIsNotNone(lead)

        update_url = reverse('lead-update', kwargs={'id': lead.id})
        update_data = {
            'name': 'updated_lead_user',
            'company': 'updated_company',
            'status': 'converted',
        }
        response = self.client.patch(update_url, update_data, format='json')
        
        if response.status_code != HTTP_200_OK:
            print(response.data)
        self.assertEqual(response.status_code, HTTP_200_OK)

        lead.refresh_from_db()
        self.assertEqual(lead.name, update_data['name'])
        self.assertEqual(lead.company, update_data['company'])
        self.assertEqual(lead.status, update_data['status'])

    def test_list_lead(self):
        # Create an agent
        response = self.client.post(self.agent_register, self.agent_data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        # Create a lead
        response = self.client.post(self.lead_register, self.lead_data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        list_url = reverse('lead-list')

        # Test filtering by agent email
        response = self.client.get(list_url, {'email': self.agent_data['email']})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.lead_data['name'])

        # Test filtering by non-existent agent email
        response = self.client.get(list_url, {'email': 'wrong@email.com'})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_list_unassigned_leads(self):
        response = self.client.post(self.lead_register, self.unassigned_lead_data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        list_url = reverse('lead-list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.unassigned_lead_data['name'])
        self.assertIsNone(response.data[0]['assign_to'])

