from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-email/', views.verify_email_view, name='verify_email'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('bughunter/', views.bughunter_view, name='bughunter'),
    path('bughunter/results/<int:job_id>/', views.bughunter_results_view, name='bughunter_results'),
    path('reports/', views.reports_view, name='reports'),
    path('settings/', views.settings_view, name='settings'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_view, name='reset_password'),
    path('update-api-key/', views.update_api_key_view, name='update_api_key'),
    path('documentation/', views.documentation_view, name='documentation'),
]