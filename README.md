# BugHunter - AI-Powered Code Analysis

BugHunter is a Django web application that uses Google's Gemini AI to analyze code repositories for bugs, security vulnerabilities, and code quality issues.

## Features

- **User Authentication**: Registration with email verification, secure login/logout
- **Code Analysis**: Upload GitHub repositories or .zip files for AI-powered analysis
- **Comprehensive Reports**: Detailed findings categorized by bugs, security vulnerabilities, and code smells
- **Multi-language Support**: Python, JavaScript, TypeScript, Java, Go, C/C++, Ruby, PHP, Rust, Kotlin, and more
- **Responsive Design**: Clean, modern UI that works on desktop and mobile

## Tech Stack

- **Backend**: Django 4.2, Python 3.8+
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (Django templates)
- **Database**: SQLite (development), PostgreSQL (production)
- **AI Integration**: Google Gemini API
- **Email**: SMTP support for email verification

## Setup Instructions

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd bughunter

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
copy .env.example .env

# Edit .env file with your configuration:
# - Set SECRET_KEY (generate a new one for production)
# - Configure email settings (Gmail SMTP example provided)
# - Add your Gemini API key
# - Configure database settings if using PostgreSQL
```

### 3. Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## Configuration Details

### Email Setup (Gmail Example)

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: Google Account → Security → App passwords
3. Use the app password in `EMAIL_HOST_PASSWORD`

### Gemini API Setup

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add the key to your `.env` file as `GEMINI_API_KEY`

### PostgreSQL Setup (Production)

```bash
# Install PostgreSQL and create database
createdb bughunter_db

# Update .env file:
USE_POSTGRES=1
DB_NAME=bughunter_db
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

## Usage Guide

### 1. User Registration

1. Visit the homepage and click "Sign Up"
2. Fill in your details (name, email, username, password)
3. Check your email for verification link
4. Click the verification link to activate your account

### 2. Code Analysis

1. Log in to your verified account
2. Navigate to "BugHunter" from the dashboard
3. Choose one option:
   - **GitHub URL**: Paste a public repository URL
   - **ZIP Upload**: Upload a .zip file containing your project
4. Click "Start Analysis" and wait for results

### 3. View Results

The analysis report includes:

- **Summary**: Overview of files analyzed and issues found
- **Detailed Findings**: Per-file breakdown of:
  - 🐛 **Bugs**: Logic errors, potential crashes
  - 🔒 **Security Vulnerabilities**: Security flaws and unsafe practices
  - 🧹 **Code Smells**: Quality issues and bad practices
- **Suggestions**: AI-powered fixes and code examples

## Project Structure

```
bughunter/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
└── bughunter_site/
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    ├── wsgi.py
    ├── asgi.py
    └── accounts/
        ├── models.py          # User, VerificationToken, BugHunterJob
        ├── views.py           # All application views
        ├── forms.py           # Django forms
        ├── urls.py            # URL patterns
        ├── tokens.py          # Email verification utilities
        ├── gemini_client.py   # Gemini API integration
        ├── utils.py           # File processing utilities
        ├── admin.py           # Django admin configuration
        ├── templates/accounts/ # HTML templates
        └── static/accounts/   # CSS and JavaScript files
```

## Security Features

- CSRF protection on all forms
- Secure password hashing
- Email verification required for login
- Input validation and sanitization
- Environment-based configuration
- File upload size limits
- Secure token generation

## Supported File Types

The analyzer supports these file extensions:
- Python: `.py`
- JavaScript: `.js`, `.jsx`, `.mjs`, `.cjs`
- TypeScript: `.ts`, `.tsx`
- Java: `.java`
- Go: `.go`
- C/C++: `.c`, `.cpp`
- Ruby: `.rb`
- PHP: `.php`
- Rust: `.rs`
- Kotlin: `.kt`
- Scala: `.scala`
- C#: `.cs`
- SQL: `.sql`
- Shell: `.sh`, `.bash`

## Deployment

### Environment Variables for Production

```bash
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
USE_POSTGRES=1
# ... other production settings
```

### Static Files

```bash
# Collect static files for production
python manage.py collectstatic
```

## Troubleshooting

### Common Issues

1. **Email not sending**: Check SMTP settings and app password
2. **Gemini API errors**: Verify API key and check quotas
3. **File upload issues**: Check file size limits and permissions
4. **Database errors**: Ensure migrations are run and database is accessible

### Logs

Check Django logs for detailed error information:
```bash
python manage.py runserver --verbosity=2
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review Django and Gemini API documentation
3. Create an issue in the repository