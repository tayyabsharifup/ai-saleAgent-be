from django.urls import path
from .views.user_view import (
    VerifyOtpView,
    SendOtpView,
    ChangePasswordView,
    ResetPasswordWithOtpView,
    LoginUserView,

)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views.agent_view import (
    RegisterAgentView,
    LoginAgentView,
    AgentProfileView,
    AgentDashboardView,
    AgentCallAnalytics,
    UpdateAgentView,
)

from .views.lead_view import (
    LeadRegisterView,
    LeadUpdateView,
    LeadListView,
    LeadDetailView,
)

from .views.manager_view import (
    ManagerLoginView,
    ManagerRegisterView,
    ManagerDashboardView,
    ManagerLeadListView,
    ManagerAgentListView,
    ManagerCallAnalytics,
    ManagerShortSurveyView,
    GetAllManagerView,
)
from .views.admin_view import (
    AdminLoginView,
    ChangeStatusView,
    AdminLeadListView,
    AdminCallAnalyticsView,
    AdminTeamListView,
    AdminDashboardView
)

user = [
    path('user/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('user/verify_otp/', VerifyOtpView.as_view(), name='verify-otp'),
    path('user/send_otp/', SendOtpView.as_view(), name='send-otp'),
    path('user/change_password/', ChangePasswordView.as_view(), name='change-password'),
    path('user/reset_password_otp/', ResetPasswordWithOtpView.as_view(), name='reset-password-otp'),
    path('user/login/', LoginUserView.as_view(), name='login'),

]

agent = [
    path('agent/register/', RegisterAgentView.as_view(), name='agent-register'),
    path('agent/login/', LoginAgentView.as_view(), name='agent-login'),
    path('agent/profile/', AgentProfileView.as_view(), name='agent-profile'),
    path('agent/dashboard/', AgentDashboardView.as_view(), name='agent-dashboard'),
    path('agent/call-analytics/', AgentCallAnalytics.as_view(), name='agent-call-analytics'),
    path('agent/update-profile/', UpdateAgentView.as_view(), name='agent-update-profile'),
]

lead = [
    path('lead/register/', LeadRegisterView.as_view(), name='lead-register'),
    path('lead/update/<int:id>/', LeadUpdateView.as_view(), name='lead-update'),
    path('lead/list/', LeadListView.as_view(), name='lead-list'),
    path('lead/detail/', LeadDetailView.as_view(), name='lead-detail'),
]

manager = [
    path('manager/register/', ManagerRegisterView.as_view(), name='manager-register'),
    path('manager/login/', ManagerLoginView.as_view(), name='manager-login'),
    path('manager/dashboard/', ManagerDashboardView.as_view(), name='manager-dashboard'),
    path('manager/lead-list/', ManagerLeadListView.as_view(), name='manager-list'),
    path('manager/agent-list/', ManagerAgentListView.as_view(), name='manager-agent-list'),
    path('manager/call-analytics/', ManagerCallAnalytics.as_view(), name='manager-call-analytics'),
    path('manager/short-survey/', ManagerShortSurveyView.as_view(), name='manager-short-survey'),
    path('manager/all-manager/', GetAllManagerView.as_view(), name='get-all-manager'),
]

admin = [
    path('admin/login/', AdminLoginView.as_view(), name='admin-login'),
    path('admin/change-status/', ChangeStatusView.as_view(), name='change-status'),
    path('admin/call-analytics/', AdminCallAnalyticsView.as_view(), name='admin-call-analytics'),
    path('admin/lead-list/', AdminLeadListView.as_view(), name='admin-lead-list'),
    path('admin/team-list/', AdminTeamListView.as_view(), name='admin-team-list'),
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard')
]

urlpatterns = [
    *user, *agent, *lead, *manager, *admin
]