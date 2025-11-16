#!/usr/bin/env python3
"""
Quick start script for BugHunter development server
"""

import os
import sys
import subprocess
from pathlib import Path


def check_setup():
    """Check if the project is properly set up."""
    issues = []
    
    # Check if .env file exists
    if not Path('.env').exists():
        issues.append("❌ .env file not found. Run 'python setup.py' first.")
    
    # Check if virtual environment exists
    if not Path('venv').exists():
        issues.append("❌ Virtual environment not found. Run 'python setup.py' first.")
    
    # Check if database exists
    if not Path('db.sqlite3').exists():
        issues.append("❌ Database not found. Run migrations first.")
    
    return issues


def run_server():
    """Start the Django development server."""
    # Determine Python path
    if os.name == 'nt':  # Windows
        python_cmd = 'venv\\Scripts\\python.exe'
    else:  # Unix/Linux/macOS
        python_cmd = 'venv/bin/python'
    
    # Fallback to system Python if venv doesn't exist
    if not Path('venv').exists():
        python_cmd = 'python'
    
    print("🚀 Starting BugHunter development server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([python_cmd, 'manage.py', 'runserver'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        print("💡 Try running 'python setup.py' to fix setup issues.")


def main():
    """Main function."""
    print("🐛 BugHunter Development Server")
    print("=" * 35)
    
    # Check setup
    issues = check_setup()
    
    if issues:
        print("⚠️  Setup issues found:")
        for issue in issues:
            print(f"   {issue}")
        print("\n💡 Run 'python setup.py' to fix these issues.")
        sys.exit(1)
    
    # Start server
    run_server()


if __name__ == "__main__":
    main()