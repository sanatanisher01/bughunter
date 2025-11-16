import json
from .gemini_client import initialize_gemini


def detect_language_with_gemini(code_content, api_key=None):
    """Use Gemini AI to detect programming language from code content."""
    model = initialize_gemini(api_key)
    
    prompt = f"""
Analyze the following code and identify the programming language. Return ONLY a JSON response with the detected language and confidence.

Code to analyze:
```
{code_content}
```

Return ONLY valid JSON in this exact format:
{{
  "detected_language": "language_name",
  "confidence": 0.95,
  "reasoning": "Brief explanation of why this language was detected"
}}

Supported languages: python, javascript, typescript, java, go, cpp, ruby, php, rust, kotlin, scala, csharp, sql, shell

If you cannot determine the language with high confidence, set confidence to 0.0 and detected_language to "unknown".
"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Clean up the response to extract JSON
        if result_text.startswith('```json'):
            result_text = result_text[7:]
        if result_text.endswith('```'):
            result_text = result_text[:-3]
        
        result = json.loads(result_text)
        
        # Validate result structure
        if 'detected_language' in result and 'confidence' in result:
            return {
                'language': result['detected_language'],
                'confidence': float(result['confidence']),
                'reasoning': result.get('reasoning', '')
            }
        
    except Exception as e:
        print(f"Error detecting language with Gemini: {e}")
    
    return {
        'language': 'unknown',
        'confidence': 0.0,
        'reasoning': 'Could not detect language'
    }


def normalize_language_name(language):
    """Normalize language names for comparison."""
    language_map = {
        'javascript': 'javascript',
        'js': 'javascript',
        'typescript': 'typescript',
        'ts': 'typescript',
        'python': 'python',
        'py': 'python',
        'java': 'java',
        'c': 'cpp',
        'cpp': 'cpp',
        'c++': 'cpp',
        'csharp': 'csharp',
        'c#': 'csharp',
        'go': 'go',
        'golang': 'go',
        'rust': 'rust',
        'php': 'php',
        'ruby': 'ruby',
        'rb': 'ruby',
        'kotlin': 'kotlin',
        'kt': 'kotlin',
        'scala': 'scala',
        'sql': 'sql',
        'shell': 'shell',
        'bash': 'shell',
        'sh': 'shell'
    }
    
    return language_map.get(language.lower(), language.lower())


def get_language_display_name(language):
    """Get display name for language."""
    display_names = {
        'javascript': 'JavaScript',
        'typescript': 'TypeScript',
        'python': 'Python',
        'java': 'Java',
        'cpp': 'C/C++',
        'csharp': 'C#',
        'go': 'Go',
        'rust': 'Rust',
        'php': 'PHP',
        'ruby': 'Ruby',
        'kotlin': 'Kotlin',
        'scala': 'Scala',
        'sql': 'SQL',
        'shell': 'Shell/Bash'
    }
    
    return display_names.get(language, language.title())