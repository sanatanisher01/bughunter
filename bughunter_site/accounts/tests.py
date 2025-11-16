from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import VerificationToken, BugHunterJob
from .tokens import create_verification_token, verify_token

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            name='Test User',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, 'Test User')
        self.assertFalse(user.is_verified)


class VerificationTokenTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            name='Test User',
            password='testpass123'
        )

    def test_create_verification_token(self):
        token = create_verification_token(self.user)
        self.assertEqual(token.user, self.user)
        self.assertFalse(token.used)
        self.assertTrue(token.is_valid())

    def test_verify_token(self):
        token = create_verification_token(self.user)
        verified_user = verify_token(str(token.token))
        self.assertEqual(verified_user, self.user)
        
        # Token should be marked as used
        token.refresh_from_db()
        self.assertTrue(token.used)


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            name='Test User',
            password='testpass123',
            is_verified=True
        )

    def test_landing_page(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BugHunter')

    def test_signup_page(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')

    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome Back')

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_dashboard_with_verified_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome, Test User')

    def test_bughunter_requires_verification(self):
        # Create unverified user
        unverified_user = User.objects.create_user(
            username='unverified',
            email='unverified@example.com',
            name='Unverified User',
            password='testpass123',
            is_verified=False
        )
        
        self.client.login(username='unverified', password='testpass123')
        response = self.client.get(reverse('bughunter'))
        self.assertEqual(response.status_code, 302)  # Redirect due to unverified


class FormsTest(TestCase):
    def test_signup_form_validation(self):
        from .forms import SignUpForm
        
        # Test valid form
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'username': 'testuser',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test invalid username (too short)
        form_data['username'] = 'ab'
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_bughunter_form_validation(self):
        from .forms import BugHunterForm
        
        # Test with GitHub URL
        form_data = {'github_url': 'https://github.com/user/repo'}
        form = BugHunterForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test with invalid URL
        form_data = {'github_url': 'https://example.com/repo'}
        form = BugHunterForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Test with no input
        form = BugHunterForm(data={})
        self.assertFalse(form.is_valid())