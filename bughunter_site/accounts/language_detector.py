import re


def detect_language(code_content):
    """Detect programming language from code content."""
    code = code_content.strip().lower()
    
    # Language patterns with confidence scores
    patterns = {
        'java': [
            (r'\bpublic\s+class\b', 0.9),
            (r'\bprivate\s+\w+\s+\w+\s*\(', 0.8),
            (r'\bpublic\s+static\s+void\s+main\b', 0.95),
            (r'\bimport\s+java\.', 0.9),
            (r'\bSystem\.out\.print', 0.9),
            (r'\bnew\s+\w+\s*\(', 0.7),
            (r'\bextends\s+\w+', 0.8),
            (r'\bimplements\s+\w+', 0.8),
        ],
        'python': [
            (r'\bdef\s+\w+\s*\(', 0.8),
            (r'\bimport\s+\w+', 0.7),
            (r'\bfrom\s+\w+\s+import', 0.8),
            (r'\bif\s+__name__\s*==\s*["\']__main__["\']', 0.95),
            (r'\bprint\s*\(', 0.7),
            (r'\bclass\s+\w+\s*\(', 0.8),
            (r':\s*$', 0.6),  # Colon at end of line
            (r'^\s*#', 0.5),  # Python comments
        ],
        'javascript': [
            (r'\bfunction\s+\w+\s*\(', 0.8),
            (r'\bvar\s+\w+\s*=', 0.7),
            (r'\blet\s+\w+\s*=', 0.8),
            (r'\bconst\s+\w+\s*=', 0.8),
            (r'\bconsole\.log\s*\(', 0.9),
            (r'=>', 0.7),  # Arrow functions
            (r'\brequire\s*\(', 0.8),
            (r'\bexport\s+', 0.8),
        ],
        'typescript': [
            (r':\s*\w+\s*=', 0.8),  # Type annotations
            (r'\binterface\s+\w+', 0.9),
            (r'\btype\s+\w+\s*=', 0.9),
            (r'<\w+>', 0.7),  # Generic types
            (r'\bimport\s+.*from\s+["\']', 0.7),
        ],
        'c': [
            (r'#include\s*<\w+\.h>', 0.9),
            (r'\bint\s+main\s*\(', 0.9),
            (r'\bprintf\s*\(', 0.8),
            (r'\bmalloc\s*\(', 0.8),
            (r'\bfree\s*\(', 0.8),
        ],
        'cpp': [
            (r'#include\s*<iostream>', 0.95),
            (r'\bstd::', 0.9),
            (r'\bcout\s*<<', 0.9),
            (r'\bcin\s*>>', 0.9),
            (r'\bnamespace\s+', 0.8),
            (r'\bclass\s+\w+\s*{', 0.8),
        ],
        'go': [
            (r'\bpackage\s+main', 0.95),
            (r'\bfunc\s+main\s*\(\s*\)', 0.9),
            (r'\bimport\s*\(', 0.8),
            (r'\bfmt\.Print', 0.9),
            (r':=', 0.8),
            (r'\bgo\s+\w+\s*\(', 0.8),
        ],
        'rust': [
            (r'\bfn\s+main\s*\(\s*\)', 0.95),
            (r'\bprintln!\s*\(', 0.9),
            (r'\blet\s+mut\s+', 0.8),
            (r'\bmatch\s+\w+\s*{', 0.8),
            (r'&str', 0.8),
        ],
        'php': [
            (r'<\?php', 0.95),
            (r'\$\w+', 0.8),
            (r'\becho\s+', 0.8),
            (r'\bfunction\s+\w+\s*\(', 0.7),
            (r'->', 0.7),
        ],
        'ruby': [
            (r'\bdef\s+\w+', 0.8),
            (r'\bend\s*$', 0.7),
            (r'\bputs\s+', 0.8),
            (r'\brequire\s+["\']', 0.8),
            (r'@\w+', 0.7),  # Instance variables
        ],
        'kotlin': [
            (r'\bfun\s+main\s*\(', 0.95),
            (r'\bfun\s+\w+\s*\(', 0.8),
            (r'\bval\s+\w+', 0.8),
            (r'\bvar\s+\w+', 0.8),
            (r'\bprintln\s*\(', 0.9),
        ],
        'scala': [
            (r'\bobject\s+\w+', 0.9),
            (r'\bdef\s+main\s*\(', 0.9),
            (r'\bval\s+\w+', 0.8),
            (r'\bvar\s+\w+', 0.8),
            (r'=>', 0.7),
        ],
        'csharp': [
            (r'\busing\s+System', 0.9),
            (r'\bpublic\s+class\s+\w+', 0.9),
            (r'\bstatic\s+void\s+Main', 0.95),
            (r'\bConsole\.Write', 0.9),
            (r'\bnamespace\s+\w+', 0.8),
        ],
        'sql': [
            (r'\bSELECT\s+', 0.9),
            (r'\bFROM\s+\w+', 0.9),
            (r'\bWHERE\s+', 0.8),
            (r'\bINSERT\s+INTO', 0.9),
            (r'\bUPDATE\s+\w+\s+SET', 0.9),
            (r'\bCREATE\s+TABLE', 0.9),
        ],
        'shell': [
            (r'^#!/bin/bash', 0.95),
            (r'^#!/bin/sh', 0.95),
            (r'\becho\s+', 0.7),
            (r'\$\w+', 0.6),
            (r'\bif\s+\[', 0.8),
            (r'\bfor\s+\w+\s+in', 0.8),
        ]
    }
    
    # Calculate scores for each language
    language_scores = {}
    
    for language, pattern_list in patterns.items():
        score = 0
        for pattern, weight in pattern_list:
            matches = len(re.findall(pattern, code, re.MULTILINE | re.IGNORECASE))
            score += matches * weight
        
        if score > 0:
            language_scores[language] = score
    
    # Return the language with highest score
    if language_scores:
        detected_language = max(language_scores, key=language_scores.get)
        confidence = language_scores[detected_language]
        
        # Only return if confidence is reasonable
        if confidence >= 0.5:
            return detected_language, confidence
    
    return None, 0


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
        'c': 'c',
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
        'c': 'C',
        'cpp': 'C++',
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