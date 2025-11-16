from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse
import tempfile
import os

from .models import User, BugHunterJob
from .forms import SignUpForm, LoginForm, BugHunterForm
from .tokens import create_verification_token, verify_token
from .utils import download_github_repo, extract_zip_file, collect_code_files, analyze_project, cleanup_temp_dir
from .email_service import EmailService
from .password_reset import PasswordResetService
from .email_service import EmailService


def landing_view(request):
    """Public landing page."""
    return render(request, 'accounts/landing.html')


def signup_view(request):
    """User registration with email verification."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            
            # Check if unverified user already exists
            existing_user = User.objects.filter(email=email, is_verified=False).first()
            if existing_user:
                # Delete existing unverified user to allow re-registration
                existing_user.delete()
                messages.info(request, 'Previous unverified account removed. Creating new account...')
            
            user = form.save(commit=False)
            user.name = form.cleaned_data['name']
            user.email = email
            user.is_verified = False
            user.save()
            
            # Create verification token
            token = create_verification_token(user)
            
            # Send verification email
            verification_url = request.build_absolute_uri(
                reverse('verify_email') + f'?token={token.token}'
            )
            
            # Always show success message to prevent email enumeration
            messages.success(request, 'Registration successful! Please check your email to verify your account. If you don\'t receive the email, you can request a new one from the login page.')
            
            # Try to send email but don't fail registration if it fails
            try:
                EmailService.send_verification_email(user, verification_url)
            except Exception as e:
                # Log error but don't show to user
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send verification email to {email}: {e}")
            
            return redirect('login')
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    """User login with verification check."""
    unverified_user = None
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user:
                if user.is_verified:
                    login(request, user)
                    return redirect('dashboard')
                else:
                    unverified_user = user
                    messages.error(request, 'Please verify your email before logging in.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form, 'unverified_user': unverified_user})


def logout_view(request):
    """User logout."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('landing')


def verify_email_view(request):
    """Email verification handler."""
    token = request.GET.get('token')
    if token:
        user = verify_token(token)
        if user:
            user.is_verified = True
            user.save()
            messages.success(request, 'Email verified successfully! You can now log in.')
            return render(request, 'accounts/verify_success.html')
    
    messages.error(request, 'Invalid or expired verification token.')
    return render(request, 'accounts/verify_failed.html')


def resend_verification_view(request):
    """Resend verification email for unverified users."""
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                user = User.objects.get(email=email, is_verified=False)
                
                # Create new verification token
                token = create_verification_token(user)
                
                # Send verification email
                verification_url = request.build_absolute_uri(
                    reverse('verify_email') + f'?token={token.token}'
                )
                
                if EmailService.send_verification_email(user, verification_url):
                    messages.success(request, 'Verification email sent! Please check your inbox.')
                else:
                    messages.error(request, 'Failed to send verification email. Please try again.')
                    
            except User.DoesNotExist:
                # Don't reveal if email exists or not for security
                messages.success(request, 'If an unverified account with that email exists, we\'ve sent a verification link.')
        
        return redirect('login')
    
    return redirect('login')


def verified_user_required(view_func):
    """Decorator to require authenticated and verified user."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        
        if not request.user.is_verified:
            messages.error(request, 'Please verify your email to access this page.')
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return wrapper


@verified_user_required
def dashboard_view(request):
    """Protected dashboard for verified users."""
    recent_jobs = BugHunterJob.objects.filter(user=request.user).order_by('-created_at')[:5]
    return render(request, 'accounts/dashboard.html', {'recent_jobs': recent_jobs})


@verified_user_required
def bughunter_view(request):
    """BugHunter analysis form and processing."""
    # Check if user has API key
    if not request.user.gemini_api_key:
        messages.error(request, 'Please add your Gemini API key in the dashboard before starting analysis.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = BugHunterForm(request.POST, request.FILES)
        if form.is_valid():
            # Create job record
            job = BugHunterJob.objects.create(
                user=request.user,
                github_url=form.cleaned_data.get('github_url'),
                zip_file=form.cleaned_data.get('zip_file'),
                code_input=form.cleaned_data.get('code_input'),
                language=form.cleaned_data.get('language')
            )
            
            # Send analysis started email
            EmailService.send_analysis_started(request.user, job)
            
            temp_dir = None
            try:
                # Handle direct code input
                if job.code_input:
                    print(f"Analyzing {job.language} code directly...")
                    from .code_analyzer import analyze_code_directly
                    
                    results = analyze_code_directly(job.code_input, job.language, request.user.gemini_api_key)
                    
                    # Check for language mismatch and show warning
                    if 'language_mismatch' in results:
                        mismatch = results['language_mismatch']
                        messages.warning(
                            request, 
                            f"Language Mismatch Detected: You selected {mismatch['selected']} but the code appears to be {mismatch['detected']} (confidence: {mismatch['confidence']:.1%}). Reason: {mismatch['reasoning']} Analysis was performed using the detected language."
                        )
                    
                    # Convert to standard format
                    summary = {
                        'total_files': 1,
                        'total_bugs': len(results.get('bugs', [])),
                        'total_vulnerabilities': len(results.get('vulnerabilities', [])),
                        'total_smells': len(results.get('improvements', [])),
                        'critical_issues': sum(1 for item in results.get('bugs', []) + results.get('vulnerabilities', []) if item.get('severity') == 'critical'),
                        'analyzed_files': [{
                            'path': f'code_input.{job.language}',
                            'size': len(job.code_input),
                            'language': job.language.title()
                        }],
                        'overall_assessment': results.get('overall_assessment', {})
                    }
                    
                    details = {
                        f'code_input.{job.language}': {
                            'bugs': results.get('bugs', []),
                            'vulnerabilities': results.get('vulnerabilities', []),
                            'smells': results.get('improvements', []),
                            'best_practices': results.get('best_practices', [])
                        }
                    }
                    
                    job.summary = summary
                    job.details = details
                    job.status = 'COMPLETED'
                    job.save()
                    
                    # Send completion email
                    EmailService.send_analysis_completed(request.user, job, summary)
                    
                    print(f"Direct code analysis complete!")
                    return redirect('bughunter_results', job_id=job.id)
                
                # Handle GitHub/ZIP analysis (existing code)
                # Create temporary directory
                temp_dir = tempfile.mkdtemp()
                
                # Download or extract project
                if job.github_url:
                    print(f"Downloading GitHub repository: {job.github_url}")
                    project_dir = download_github_repo(job.github_url, temp_dir)
                    print(f"Repository downloaded successfully")
                else:
                    print(f"Extracting ZIP file: {job.zip_file.name}")
                    project_dir = extract_zip_file(job.zip_file, temp_dir)
                    print(f"ZIP file extracted successfully")
                
                # Collect and analyze code files
                print(f"Collecting code files from project...")
                code_files = collect_code_files(project_dir)
                
                if not code_files:
                    job.status = 'FAILED'
                    job.save()
                    messages.error(request, 'No supported code files found in the project.')
                    return redirect('bughunter')
                
                print(f"Found {len(code_files)} code files to analyze")
                print(f"Starting AI-powered analysis...")
                print("=" * 50)
                
                # Analyze project
                results = analyze_project(code_files, request.user.gemini_api_key)
                
                print("=" * 50)
                print(f"Analysis complete! Found {results['summary']['total_bugs'] + results['summary']['total_vulnerabilities']} issues")
                
                # Save results
                job.summary = results['summary']
                job.details = results['files']
                job.status = 'COMPLETED'
                job.save()
                
                # Send completion email
                EmailService.send_analysis_completed(request.user, job, results['summary'])
                
                return redirect('bughunter_results', job_id=job.id)
                
            except Exception as e:
                job.status = 'FAILED'
                job.save()
                
                # Send failure email
                EmailService.send_analysis_failed(request.user, job, str(e))
                
                messages.error(request, f'Analysis failed: {str(e)}')
                return redirect('bughunter')
            
            finally:
                if temp_dir:
                    cleanup_temp_dir(temp_dir)
    else:
        form = BugHunterForm()
    
    return render(request, 'accounts/bughunter_form.html', {'form': form})


@verified_user_required
def bughunter_results_view(request, job_id):
    """Display BugHunter analysis results."""
    job = get_object_or_404(BugHunterJob, id=job_id, user=request.user)
    
    if job.status != 'COMPLETED':
        messages.error(request, 'Analysis is not completed yet.')
        return redirect('bughunter')
    
    return render(request, 'accounts/bughunter_result.html', {'job': job})
@verified_user_required
def reports_view(request):
    """View analysis reports history."""
    jobs = BugHunterJob.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/reports.html', {'jobs': jobs})


@verified_user_required
def settings_view(request):
    """User settings and preferences."""
    return render(request, 'accounts/settings.html')
def forgot_password_view(request):
    """Handle forgot password form"""
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            password_reset_service = PasswordResetService()
            if password_reset_service.send_reset_email(request, email):
                messages.success(request, 'If an account with that email exists, we\'ve sent a password reset link.')
            else:
                messages.error(request, 'There was an error sending the reset email. Please try again.')
        return redirect('login')
    
    return render(request, 'accounts/forgot_password.html')


def reset_password_view(request, uidb64, token):
    """Handle password reset form"""
    password_reset_service = PasswordResetService()
    user = password_reset_service.verify_reset_token(uidb64, token)
    
    if not user:
        messages.error(request, 'Invalid or expired password reset link.')
        return redirect('login')
    
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 and password2:
            if password1 == password2:
                if len(password1) >= 8:
                    if password_reset_service.reset_password(user, password1):
                        messages.success(request, 'Your password has been reset successfully. You can now sign in.')
                        return redirect('login')
                    else:
                        messages.error(request, 'There was an error resetting your password. Please try again.')
                else:
                    messages.error(request, 'Password must be at least 8 characters long.')
            else:
                messages.error(request, 'Passwords do not match.')
        else:
            messages.error(request, 'Please fill in both password fields.')
    
    return render(request, 'accounts/reset_password.html', {'user': user})


@verified_user_required
def update_api_key_view(request):
    """Update user's Gemini API key."""
    if request.method == 'POST':
        api_key = request.POST.get('api_key', '').strip()
        if api_key:
            request.user.gemini_api_key = api_key
            request.user.save()
            messages.success(request, 'Gemini API key updated successfully!')
        else:
            messages.error(request, 'Please provide a valid API key.')
    
    return redirect('dashboard')


def documentation_view(request):
    """Documentation page."""
    return render(request, 'accounts/documentation.html')