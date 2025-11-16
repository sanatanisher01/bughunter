from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging
import threading
from functools import wraps

logger = logging.getLogger(__name__)

def async_email(func):
    """Decorator to send emails asynchronously"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Always send synchronously but with timeout to prevent worker issues
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False
    return wrapper

class EmailService:
    @staticmethod
    @async_email
    def send_verification_email(user, verification_url):
        """Send email verification email"""
        try:
            logger.info(f"Attempting to send verification email to {user.email}")
            logger.info(f"Email settings - Host: {settings.EMAIL_HOST}, Port: {settings.EMAIL_PORT}, User: {settings.EMAIL_HOST_USER}")
            
            subject = "🔍 Verify Your Email - BugHunter"
            
            context = {
                'user': user,
                'verification_url': verification_url,
                'site_url': 'https://bughunters.onrender.com'
            }
            
            html_content = render_to_string('accounts/emails/email_verification.html', context)
            text_content = strip_tags(html_content)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            
            result = msg.send()
            logger.info(f"Email send result: {result}")
            
            if result:
                logger.info(f"Verification email sent successfully to {user.email}")
                return True
            else:
                logger.error(f"Email send returned 0 - no emails sent")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False
    
    @staticmethod
    def send_analysis_started(user, job):
        """Send email when analysis starts"""
        try:
            subject = f"🔍 Analysis Started - {job.project_name}"
            
            context = {
                'user': user,
                'job': job,
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
            }
            
            html_content = render_to_string('accounts/emails/analysis_started.html', context)
            text_content = strip_tags(html_content)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Analysis started email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send analysis started email: {e}")
            return False
    
    @staticmethod
    def send_analysis_completed(user, job, results_summary):
        """Send email when analysis completes successfully"""
        try:
            subject = f"✅ Analysis Complete - {job.project_name}"
            
            context = {
                'user': user,
                'job': job,
                'results_summary': results_summary,
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
            }
            
            html_content = render_to_string('accounts/emails/analysis_completed.html', context)
            text_content = strip_tags(html_content)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Analysis completed email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send analysis completed email: {e}")
            return False
    
    @staticmethod
    def send_analysis_failed(user, job, error_message):
        """Send email when analysis fails"""
        try:
            subject = f"❌ Analysis Failed - {job.project_name}"
            
            context = {
                'user': user,
                'job': job,
                'error_message': error_message,
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
            }
            
            html_content = render_to_string('accounts/emails/analysis_failed.html', context)
            text_content = strip_tags(html_content)
            
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Analysis failed email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send analysis failed email: {e}")
            return False