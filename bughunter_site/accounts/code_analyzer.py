import json
from .gemini_client import initialize_gemini
from .gemini_language_detector import detect_language_with_gemini, normalize_language_name, get_language_display_name


def analyze_code_directly(code_content, language, api_key=None):
    """Analyze code directly with detailed suggestions and fixes."""
    # Detect actual language from code using Gemini
    detection_result = detect_language_with_gemini(code_content, api_key)
    
    # Check if selected language matches detected language
    selected_normalized = normalize_language_name(language)
    detected_normalized = normalize_language_name(detection_result['language']) if detection_result['language'] != 'unknown' else None
    
    language_mismatch = None
    if detected_normalized and detected_normalized != selected_normalized and detection_result['confidence'] > 0.7:
        language_mismatch = {
            'selected': get_language_display_name(selected_normalized),
            'detected': get_language_display_name(detected_normalized),
            'confidence': detection_result['confidence'],
            'reasoning': detection_result['reasoning']
        }
    
    model = initialize_gemini(api_key)
    
    # Include language detection info in prompt if there's a mismatch
    language_note = ""
    if language_mismatch:
        language_note = f"""

IMPORTANT: The user selected {language_mismatch['selected']} as the language, but the code appears to be {language_mismatch['detected']} (confidence: {language_mismatch['confidence']:.1f}). Please analyze it as {language_mismatch['detected']} and mention this language mismatch in your assessment.
"""
    
    prompt = f"""
You are a senior software engineer and code reviewer. Analyze the following code and provide comprehensive feedback.{language_note}

Code to analyze:
```
{code_content}
```

Return ONLY valid JSON in this exact format:
{{
  "overall_assessment": {{
    "quality_score": 85,
    "readability": "good|fair|poor",
    "maintainability": "high|medium|low",
    "performance": "excellent|good|fair|poor"
  }},
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
      "title": "Security issue title",
      "severity": "low|medium|high|critical", 
      "description": "Security issue description",
      "line_range": [start_line, end_line],
      "suggested_fix": "Security fix recommendation",
      "fixed_code_example": "Secure code example"
    }}
  ],
  "improvements": [
    {{
      "title": "Improvement suggestion",
      "category": "performance|readability|maintainability|best_practices",
      "description": "What can be improved",
      "line_range": [start_line, end_line],
      "suggested_fix": "How to improve",
      "improved_code_example": "Better code example"
    }}
  ],
  "best_practices": [
    {{
      "title": "Best practice recommendation",
      "description": "Recommendation description",
      "example": "Code example following best practices"
    }}
  ]
}}

Focus on:
1. Actual bugs and logic errors
2. Security vulnerabilities
3. Performance improvements
4. Code readability and maintainability
5. Language-specific best practices
6. Error handling improvements

If no issues are found in a category, return empty arrays.
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
        
        # Add language mismatch info to result
        if language_mismatch:
            result['language_mismatch'] = language_mismatch
        
        return result
    except Exception as e:
        print(f"Error analyzing code: {e}")
        return {
            "overall_assessment": {
                "quality_score": 0,
                "readability": "unknown",
                "maintainability": "unknown", 
                "performance": "unknown"
            },
            "bugs": [],
            "vulnerabilities": [],
            "improvements": [],
            "best_practices": []
        }