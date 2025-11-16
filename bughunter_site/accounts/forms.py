from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User
import re


class SignUpForm(UserCreationForm):
    name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('name', 'email', 'username', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters.")
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise forms.ValidationError("Username can only contain letters, numbers, underscores, and hyphens.")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            try:
                user = User.objects.get(username=username)
                if not user.is_verified:
                    raise forms.ValidationError("Please verify your email before logging in.")
            except User.DoesNotExist:
                pass
            
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Invalid username or password.")
        
        return self.cleaned_data


class BugHunterForm(forms.Form):
    github_url = forms.URLField(required=False, help_text="GitHub repository URL")
    zip_file = forms.FileField(required=False, help_text="Upload project as .zip file")
    code_input = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 15, 'placeholder': 'Paste your code here...'}),
        required=False,
        help_text="Paste your code directly for quick analysis"
    )
    language = forms.ChoiceField(
        choices=[
            ('python', 'Python'),
            ('javascript', 'JavaScript'),
            ('typescript', 'TypeScript'),
            ('java', 'Java'),
            ('go', 'Go'),
            ('cpp', 'C++'),
            ('c', 'C'),
            ('ruby', 'Ruby'),
            ('php', 'PHP'),
            ('rust', 'Rust'),
            ('kotlin', 'Kotlin'),
            ('other', 'Other')
        ],
        required=False,
        help_text="Select programming language for code input"
    )
    
    def clean(self):
        github_url = self.cleaned_data.get('github_url')
        zip_file = self.cleaned_data.get('zip_file')
        code_input = self.cleaned_data.get('code_input')
        language = self.cleaned_data.get('language')
        
        input_count = sum([bool(github_url), bool(zip_file), bool(code_input)])
        
        if input_count == 0:
            raise forms.ValidationError("Please provide a GitHub URL, upload a .zip file, or paste code directly.")
        
        if input_count > 1:
            raise forms.ValidationError("Please use only one input method.")
        
        if code_input and not language:
            raise forms.ValidationError("Please select a programming language for your code.")
        
        if github_url and 'github.com' not in github_url:
            raise forms.ValidationError("Please provide a valid GitHub repository URL.")
        
        return self.cleaned_data