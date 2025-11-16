from django.utils import timezone
from datetime import timedelta
from .models import VerificationToken
import uuid


def create_verification_token(user):
    """Create a new verification token for the user."""
    expires_at = timezone.now() + timedelta(hours=24)
    token = VerificationToken.objects.create(
        user=user,
        expires_at=expires_at
    )
    return token


def verify_token(token_str):
    """Verify a token and return the associated user if valid."""
    try:
        token = VerificationToken.objects.get(token=token_str)
        if token.is_valid():
            token.used = True
            token.save()
            return token.user
    except VerificationToken.DoesNotExist:
        pass
    return None