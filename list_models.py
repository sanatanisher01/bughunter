#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bughunter_site.settings')
django.setup()

import google.generativeai as genai

# List available models
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    
    print("Available Gemini models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"- {model.name}")
            
except Exception as e:
    print(f"Error listing models: {e}")