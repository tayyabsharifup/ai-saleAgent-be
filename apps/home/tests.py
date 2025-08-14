from rest_framework.test import APITestCase
from django.urls import reverse

# Create your tests here.

class TwilioViewTest(APITestCase):
    def setUp(self):
        self.buy_number_url = reverse('buy-number')
    
    def test_buy_number(self):
        response = self.client.get(self.buy_number_url, {
            'country': 'US',
        })
        print(f"Response from buy number: {response.data.get('available_numbers')}")
        self.assertEqual(response.status_code, 200)

        num = response.data.get('available_numbers')[0] if response.data.get('available_numbers') else None
        if num:
            response = self.client.post(self.buy_number_url, {
                'number': num,
            })
            print(f"Response from buy number post: {response.data}")
            self.assertEqual(response.status_code, 201)
            self.assertIn('purchased_number', response.data)
        else:
            print("No available numbers to purchase.")
            self.assertTrue(False, "No available numbers to test purchase.")
    
