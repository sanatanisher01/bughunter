import os
import tempfile
import shutil
import zipfile
import subprocess
from pathlib import Path
from .gemini_client import analyze_code_chunk, chunk_text


SUPPORTED_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.c', '.cpp', 
    '.rb', '.php', '.rs', '.kt', '.scala', '.cs', '.sql', '.sh', '.bash'
}

SKIP_DIRS = {
    '.git', 'node_modules', 'dist', 'build', '__pycache__', '.venv', 
    'venv', 'env', '.env', 'target', 'bin', 'obj', '.next', 'coverage'
}


def download_github_repo(github_url, temp_dir):
    """Download GitHub repository to temporary directory."""
    try:
        # Use git clone with depth 1 for faster download
        cmd = ['git', 'clone', '--depth', '1', github_url, temp_dir]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise Exception(f"Git clone failed: {result.stderr}")
        
        return temp_dir
    except Exception as e:
        raise Exception(f"Failed to download repository: {str(e)}")


def extract_zip_file(zip_file, temp_dir):
    """Extract uploaded zip file to temporary directory."""
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        return temp_dir
    except Exception as e:
        raise Exception(f"Failed to extract zip file: {str(e)}")


def collect_code_files(project_dir):
    """Collect all code files from project directory."""
    code_files = []
    project_path = Path(project_dir)
    
    for file_path in project_path.rglob('*'):
        if file_path.is_file():
            # Skip files in ignored directories
            if any(skip_dir in file_path.parts for skip_dir in SKIP_DIRS):
                continue
            
            # Check file extension
            if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                try:
                    # Try to read file as text
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Skip very large files (>1MB)
                    if len(content) > 1024 * 1024:
                        print(f"Skipping large file: {file_path} ({len(content)} bytes)")
                        continue
                    
                    code_files.append({
                        'path': str(file_path.relative_to(project_path)),
                        'content': content
                    })
                except Exception as e:
                    # Skip files that can't be read
                    print(f"Skipping unreadable file: {file_path} - {e}")
                    continue
    
    return code_files


def analyze_project(code_files, api_key=None):
    """Analyze all code files and return aggregated results."""
    all_results = {
        'summary': {
            'total_files': len(code_files),
            'total_bugs': 0,
            'total_vulnerabilities': 0,
            'total_smells': 0,
            'critical_issues': 0,
            'analyzed_files': [],
            'skipped_files': []
        },
        'files': {}
    }
    
    for file_info in code_files:
        file_path = file_info['path']
        content = file_info['content']
        
        print(f"Analyzing: {file_path} ({len(content)} chars)")
        all_results['summary']['analyzed_files'].append({
            'path': file_path,
            'size': len(content),
            'language': get_file_language(file_path)
        })
        
        # Split content into chunks
        chunks = chunk_text(content)
        print(f"   Split into {len(chunks)} chunks")
        
        file_results = {
            'bugs': [],
            'vulnerabilities': [],
            'smells': []
        }
        
        # Analyze each chunk
        for chunk_index, chunk in enumerate(chunks):
            try:
                print(f"   AI analyzing chunk {chunk_index + 1}/{len(chunks)}...")
                chunk_results = analyze_code_chunk(file_path, chunk_index, chunk, api_key)
                
                # Merge results
                file_results['bugs'].extend(chunk_results.get('bugs', []))
                file_results['vulnerabilities'].extend(chunk_results.get('vulnerabilities', []))
                file_results['smells'].extend(chunk_results.get('smells', []))
                
            except Exception as e:
                print(f"Error analyzing chunk {chunk_index} of {file_path}: {e}")
                continue
        
        # Update summary
        all_results['summary']['total_bugs'] += len(file_results['bugs'])
        all_results['summary']['total_vulnerabilities'] += len(file_results['vulnerabilities'])
        all_results['summary']['total_smells'] += len(file_results['smells'])
        
        # Count critical issues
        for bug in file_results['bugs']:
            if bug.get('severity') == 'critical':
                all_results['summary']['critical_issues'] += 1
        
        for vuln in file_results['vulnerabilities']:
            if vuln.get('severity') == 'critical':
                all_results['summary']['critical_issues'] += 1
        
        # Log results for this file
        total_findings = len(file_results['bugs']) + len(file_results['vulnerabilities']) + len(file_results['smells'])
        if total_findings > 0:
            print(f"   Found {total_findings} issues")
            all_results['files'][file_path] = file_results
        else:
            print(f"   No issues found")
            
        print()  # Empty line for readability
    
    # Calculate risk score (0-100)
    total_issues = (
        all_results['summary']['total_bugs'] + 
        all_results['summary']['total_vulnerabilities']
    )
    critical_weight = all_results['summary']['critical_issues'] * 10
    all_results['summary']['risk_score'] = min(100, total_issues + critical_weight)
    
    return all_results


def get_file_language(file_path):
    """Get programming language from file extension."""
    ext = Path(file_path).suffix.lower()
    language_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.jsx': 'JavaScript (React)',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript (React)',
        '.java': 'Java',
        '.go': 'Go',
        '.c': 'C',
        '.cpp': 'C++',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.rs': 'Rust',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.cs': 'C#',
        '.sql': 'SQL',
        '.sh': 'Shell',
        '.bash': 'Bash'
    }
    return language_map.get(ext, 'Unknown')


def cleanup_temp_dir(temp_dir):
    """Clean up temporary directory."""
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass