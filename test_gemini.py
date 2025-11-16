#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bughunter_site.settings')
django.setup()

from bughunter_site.accounts.gemini_client import initialize_gemini

# Test Gemini API
try:
    print(f"GEMINI_API_KEY: {settings.GEMINI_API_KEY[:10]}...")
    model = initialize_gemini()
    
    response = model.generate_content("Hello, test message")
    print("Gemini API working!")
    print(f"Response: {response.text[:100]}...")
    
except Exception as e:
    print(f"Gemini API failed: {e}")
    print(f"API Key length: {len(settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else 'None'}")
    print(f"API Key starts with: {settings.GEMINI_API_KEY[:20] if settings.GEMINI_API_KEY else 'None'}")