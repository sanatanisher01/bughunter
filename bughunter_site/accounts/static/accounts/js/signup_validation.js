document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('signup-form');
    const nameField = document.getElementById('id_name');
    const emailField = document.getElementById('id_email');
    const usernameField = document.getElementById('id_username');
    const password1Field = document.getElementById('id_password1');
    const password2Field = document.getElementById('id_password2');

    // Validation functions
    function validateName() {
        const name = nameField.value.trim();
        const errorDiv = document.getElementById('name-error');
        
        if (!name) {
            showError(errorDiv, 'Name is required.');
            return false;
        }
        
        clearError(errorDiv);
        return true;
    }

    function validateEmail() {
        const email = emailField.value.trim();
        const errorDiv = document.getElementById('email-error');
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!email) {
            showError(errorDiv, 'Email is required.');
            return false;
        }
        
        if (!emailRegex.test(email)) {
            showError(errorDiv, 'Please enter a valid email address.');
            return false;
        }
        
        clearError(errorDiv);
        return true;
    }

    function validateUsername() {
        const username = usernameField.value.trim();
        const errorDiv = document.getElementById('username-error');
        const usernameRegex = /^[a-zA-Z0-9_-]+$/;
        
        if (!username) {
            showError(errorDiv, 'Username is required.');
            return false;
        }
        
        if (username.length < 3) {
            showError(errorDiv, 'Username must be at least 3 characters.');
            return false;
        }
        
        if (!usernameRegex.test(username)) {
            showError(errorDiv, 'Username can only contain letters, numbers, underscores, and hyphens.');
            return false;
        }
        
        clearError(errorDiv);
        return true;
    }

    function validatePassword() {
        const password = password1Field.value;
        const errorDiv = document.getElementById('password1-error');
        
        if (!password) {
            showError(errorDiv, 'Password is required.');
            return false;
        }
        
        if (password.length < 8) {
            showError(errorDiv, 'Password must be at least 8 characters.');
            return false;
        }
        
        if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(password)) {
            showError(errorDiv, 'Password must contain at least one letter and one number.');
            return false;
        }
        
        clearError(errorDiv);
        return true;
    }

    function validatePasswordConfirm() {
        const password1 = password1Field.value;
        const password2 = password2Field.value;
        const errorDiv = document.getElementById('password2-error');
        
        if (!password2) {
            showError(errorDiv, 'Please confirm your password.');
            return false;
        }
        
        if (password1 !== password2) {
            showError(errorDiv, 'Passwords do not match.');
            return false;
        }
        
        clearError(errorDiv);
        return true;
    }

    function showError(errorDiv, message) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }

    function clearError(errorDiv) {
        errorDiv.textContent = '';
        errorDiv.style.display = 'none';
    }

    // Add event listeners
    nameField.addEventListener('blur', validateName);
    emailField.addEventListener('blur', validateEmail);
    usernameField.addEventListener('blur', validateUsername);
    password1Field.addEventListener('blur', validatePassword);
    password2Field.addEventListener('blur', validatePasswordConfirm);
    
    // Validate password confirmation when password1 changes
    password1Field.addEventListener('input', function() {
        if (password2Field.value) {
            validatePasswordConfirm();
        }
    });

    // Form submission validation
    form.addEventListener('submit', function(e) {
        const isNameValid = validateName();
        const isEmailValid = validateEmail();
        const isUsernameValid = validateUsername();
        const isPasswordValid = validatePassword();
        const isPasswordConfirmValid = validatePasswordConfirm();
        
        if (!isNameValid || !isEmailValid || !isUsernameValid || !isPasswordValid || !isPasswordConfirmValid) {
            e.preventDefault();
        }
    });
});