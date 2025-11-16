from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.utils.html import strip_tags
from .models import User
import logging

logger = logging.getLogger(__name__)

class PasswordResetService:
    def __init__(self):
        self.token_generator = PasswordResetTokenGenerator()
    
    def send_reset_email(self, request, email):
        """Send password reset email if user exists"""
        try:
            user = User.objects.get(email=email)
            
            # Generate token and uid
            token = self.token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL
            reset_url = request.build_absolute_uri(
                reverse('reset_password', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Prepare email context
            context = {
                'user': user,
                'reset_url': reset_url,
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
            }
            
            # Render email templates
            html_content = render_to_string('accounts/emails/password_reset.html', context)
            text_content = strip_tags(html_content)
            
            # Send email
            msg = EmailMultiAlternatives(
                subject='🔑 Reset Your BugHunter Password',
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Password reset email sent to {user.email}")
            return True
            
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            logger.info(f"Password reset attempted for non-existent email: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            return False
    
    def verify_reset_token(self, uidb64, token):
        """Verify password reset token and return user"""
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            if self.token_generator.check_token(user, token):
                return user
            return None
            
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None
    
    def reset_password(self, user, new_password):
        """Reset user password"""
        try:
            user.set_password(new_password)
            user.save()
            logger.info(f"Password reset successful for user: {user.username}")
            return True
        except Exception as e:
            logger.error(f"Failed to reset password for user {user.username}: {e}")
            return False