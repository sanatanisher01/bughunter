import os
import json
import google.generativeai as genai
from django.conf import settings


def initialize_gemini(api_key=None):
    """Initialize Gemini client with API key."""
    if not api_key:
        api_key = settings.GEMINI_API_KEY
    
    if not api_key or api_key.strip() == '':
        raise ValueError("GEMINI_API_KEY not configured")
    
    genai.configure(api_key=api_key.strip())
    return genai.GenerativeModel('gemini-2.0-flash')


def analyze_code_chunk(file_path, chunk_index, code_content, api_key=None):
    """Analyze a code chunk using Gemini API."""
    model = initialize_gemini(api_key)
    
    prompt = f"""
You are a senior code reviewer and security expert. Analyze the following code chunk and return a strict JSON response with bugs, security vulnerabilities, and code smells.

File: {file_path}
Chunk: {chunk_index + 1}

Code:
```
{code_content}
```

Return ONLY valid JSON in this exact format:
{{
  "bugs": [
    {{
      "title": "Bug title",
      "severity": "low|medium|high|critical",
      "description": "Detailed description",
      "line_range": [start_line, end_line],
      "suggested_fix": "How to fix it",
      "fixed_code_example": "Example of fixed code"
    }}
  ],
  "vulnerabilities": [
    {{
      "title": "Vulnerability title",
      "severity": "low|medium|high|critical",
      "description": "Security issue description",
      "line_range": [start_line, end_line],
      "suggested_fix": "Security fix recommendation",
      "fixed_code_example": "Secure code example"
    }}
  ],
  "smells": [
    {{
      "title": "Code smell title",
      "description": "Code quality issue",
      "line_range": [start_line, end_line],
      "suggested_fix": "Improvement suggestion"
    }}
  ]
}}

If no issues are found, return empty arrays. Focus on real issues, not minor style preferences.
"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Clean up the response to extract JSON
        if result_text.startswith('```json'):
            result_text = result_text[7:]
        if result_text.endswith('```'):
            result_text = result_text[:-3]
        
        return json.loads(result_text)
    except Exception as e:
        print(f"Error analyzing code chunk: {e}")
        return {"bugs": [], "vulnerabilities": [], "smells": []}


def chunk_text(text, max_chars=8000):
    """Split text into chunks that fit within token limits."""
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    lines = text.split('\n')
    current_chunk = []
    current_length = 0
    
    for line in lines:
        line_length = len(line) + 1  # +1 for newline
        if current_length + line_length > max_chars and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_length = line_length
        else:
            current_chunk.append(line)
            current_length += line_length
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks