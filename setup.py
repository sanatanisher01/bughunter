#!/usr/bin/env python3
"""
BugHunter Setup Script
Automated setup for the BugHunter Django application
"""

import os
import sys
import subprocess
import secrets
import shutil
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None


def create_env_file():
    """Create .env file from template with generated secret key."""
    env_example = Path('.env.example')
    env_file = Path('.env')
    
    if env_file.exists():
        print("⚠️  .env file already exists. Skipping creation.")
        return
    
    if not env_example.exists():
        print("❌ .env.example file not found!")
        return
    
    # Generate a secure secret key
    secret_key = secrets.token_urlsafe(50)
    
    # Read template and replace secret key
    with open(env_example, 'r') as f:
        content = f.read()
    
    content = content.replace('your-secret-key-here', secret_key)
    
    # Write to .env file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file with generated secret key")
    print("⚠️  Please update the .env file with your email and Gemini API settings")


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def setup_virtual_environment():
    """Create and activate virtual environment."""
    venv_path = Path('venv')
    
    if venv_path.exists():
        print("⚠️  Virtual environment already exists")
        return
    
    # Create virtual environment
    if run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
        print("✅ Virtual environment created")
        
        # Determine activation script path
        if os.name == 'nt':  # Windows
            activate_script = venv_path / 'Scripts' / 'activate.bat'
            pip_path = venv_path / 'Scripts' / 'pip.exe'
        else:  # Unix/Linux/macOS
            activate_script = venv_path / 'bin' / 'activate'
            pip_path = venv_path / 'bin' / 'pip'
        
        print(f"📝 To activate virtual environment:")
        if os.name == 'nt':
            print(f"   venv\\Scripts\\activate")
        else:
            print(f"   source venv/bin/activate")
        
        return str(pip_path)
    
    return None


def install_dependencies(pip_path=None):
    """Install Python dependencies."""
    pip_cmd = pip_path if pip_path else 'pip'
    
    # Upgrade pip first
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    
    # Install requirements
    if Path('requirements.txt').exists():
        run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies")
    else:
        print("❌ requirements.txt not found!")


def setup_database():
    """Run Django migrations."""
    python_cmd = 'venv/Scripts/python.exe' if os.name == 'nt' else 'venv/bin/python'
    
    if not Path('venv').exists():
        python_cmd = 'python'
    
    # Make migrations
    run_command(f"{python_cmd} manage.py makemigrations", "Creating migrations")
    
    # Run migrations
    run_command(f"{python_cmd} manage.py migrate", "Running database migrations")


def create_superuser():
    """Prompt to create Django superuser."""
    python_cmd = 'venv/Scripts/python.exe' if os.name == 'nt' else 'venv/bin/python'
    
    if not Path('venv').exists():
        python_cmd = 'python'
    
    print("\n🔐 Would you like to create a superuser account? (y/n): ", end="")
    choice = input().lower().strip()
    
    if choice in ['y', 'yes']:
        print("Creating superuser account...")
        os.system(f"{python_cmd} manage.py createsuperuser")


def print_next_steps():
    """Print instructions for next steps."""
    print("\n" + "="*60)
    print("🎉 BugHunter setup completed successfully!")
    print("="*60)
    print("\n📋 Next steps:")
    print("1. Update your .env file with:")
    print("   - Email SMTP settings (Gmail example provided)")
    print("   - Gemini API key from https://makersuite.google.com/app/apikey")
    print("   - Database settings (if using PostgreSQL)")
    
    print("\n2. Start the development server:")
    if Path('venv').exists():
        if os.name == 'nt':
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
    print("   python manage.py runserver")
    
    print("\n3. Visit http://localhost:8000 to access BugHunter")
    
    print("\n📚 For detailed setup instructions, see README.md")
    print("\n🐛 Happy bug hunting!")


def main():
    """Main setup function."""
    print("🐛 BugHunter Setup Script")
    print("=" * 30)
    
    # Check Python version
    check_python_version()
    
    # Create .env file
    create_env_file()
    
    # Setup virtual environment
    pip_path = setup_virtual_environment()
    
    # Install dependencies
    install_dependencies(pip_path)
    
    # Setup database
    setup_database()
    
    # Create superuser
    create_superuser()
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()