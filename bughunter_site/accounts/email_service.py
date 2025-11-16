from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_verification_email(user, verification_url):
        """Send email verification email"""
        try:
            subject = "Verify Your Email - BugHunter"
            
            # Simple text message as fallback
            message = f"""Hi {user.name},

Please verify your email address by clicking the link below:
{verification_url}

If you didn't create an account, please ignore this email.

Best regards,
BugHunter Team"""
            
            # Try simple send_mail first
            result = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
            
            logger.info(f"Verification email sent to {user.email}, result: {result}")
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
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