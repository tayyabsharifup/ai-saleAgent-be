from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.status import HTTP_200_OK
from apps.users.models import CustomUser, LeadModel, AgentModel, ManagerModel
from apps.users.views.admin_view import (
    get_user_counts_by_role,
    get_lead_counts_by_status,
    get_lead_conversion_rate,
    get_leads_assigned_to_agents,
    get_leads_assigned_to_managers,
    get_new_leads_count_by_date_range
)
from datetime import date, timedelta

class DashboardMetricsTest(APITestCase):
    def setUp(self):
        # Create test users
        self.admin_user = CustomUser.objects.create_user(email='admin@example.com', password='password', role='admin')
        self.manager_user = CustomUser.objects.create_user(email='manager@example.com', password='password', role='manager')
        self.agent_user = CustomUser.objects.create_user(email='agent@example.com', password='password', role='agent')
        self.another_agent_user = CustomUser.objects.create_user(email='agent2@example.com', password='password', role='agent')

        # Create manager and agents
        self.manager = ManagerModel.objects.create(user=self.manager_user)
        self.agent1 = AgentModel.objects.create(user=self.agent_user, assign_manager=self.manager)
        self.agent2 = AgentModel.objects.create(user=self.another_agent_user, assign_manager=self.manager)

        # Create leads
        today = date.today()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)

        LeadModel.objects.create(name='Lead 1', status='converted', assign_to=self.agent1, created_at=today)
        LeadModel.objects.create(name='Lead 2', status='in_progress', assign_to=self.agent1, created_at=yesterday)
        LeadModel.objects.create(name='Lead 3', status='not_initiated', assign_to=self.agent2, created_at=today)
        LeadModel.objects.create(name='Lead 4', status='converted', assign_to=self.agent2, created_at=two_days_ago)
        LeadModel.objects.create(name='Lead 5', status='over_due', created_at=today) # Unassigned lead

    def test_get_user_counts_by_role(self):
        counts = get_user_counts_by_role()
        self.assertEqual(counts.get('admin'), 1)
        self.assertEqual(counts.get('manager'), 1)
        self.assertEqual(counts.get('agent'), 2)

    def test_get_lead_counts_by_status(self):
        counts = get_lead_counts_by_status()
        self.assertEqual(counts.get('converted'), 2)
        self.assertEqual(counts.get('in_progress'), 1)
        self.assertEqual(counts.get('not_initiated'), 1)
        self.assertEqual(counts.get('over_due'), 1)

    def test_get_lead_conversion_rate(self):
        rate = get_lead_conversion_rate()
        # 2 converted leads out of 5 total leads = 40.0%
        self.assertAlmostEqual(rate, 40.0)

        # Test with no leads
        LeadModel.objects.all().delete()
        rate_no_leads = get_lead_conversion_rate()
        self.assertEqual(rate_no_leads, 0.0)

    def test_get_leads_assigned_to_agents(self):
        counts = get_leads_assigned_to_agents()
        self.assertEqual(counts.get(self.agent_user.email), 2)
        self.assertEqual(counts.get(self.another_agent_user.email), 2)
        self.assertNotIn(None, counts) # Ensure unassigned leads are not counted here

    def test_get_leads_assigned_to_managers(self):
        counts = get_leads_assigned_to_managers()
        self.assertEqual(counts.get(self.manager_user.email), 4) # 2 leads for agent1 + 2 leads for agent2

    def test_get_new_leads_count_by_date_range(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)

        # Leads created today
        count_today = get_new_leads_count_by_date_range(today, today)
        self.assertEqual(count_today, 3) # Lead 1, Lead 3, Lead 5

        # Leads created yesterday
        count_yesterday = get_new_leads_count_by_date_range(yesterday, yesterday)
        self.assertEqual(count_yesterday, 1) # Lead 2

        # Leads created two days ago
        count_two_days_ago = get_new_leads_count_by_date_range(two_days_ago, two_days_ago)
        self.assertEqual(count_two_days_ago, 1) # Lead 4

        # Leads created in the last 3 days (inclusive)
        count_last_3_days = get_new_leads_count_by_date_range(two_days_ago, today)
        self.assertEqual(count_last_3_days, 5) # All leads