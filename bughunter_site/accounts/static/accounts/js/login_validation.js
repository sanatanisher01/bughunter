document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('login-form');
    const usernameField = document.getElementById('id_username');
    const passwordField = document.getElementById('id_password');

    function validateUsername() {
        const username = usernameField.value.trim();
        const errorDiv = document.getElementById('username-error');
        
        if (!username) {
            showError(errorDiv, 'Username is required.');
            return false;
        }
        
        clearError(errorDiv);
        return true;
    }

    function validatePassword() {
        const password = passwordField.value;
        const errorDiv = document.getElementById('password-error');
        
        if (!password) {
            showError(errorDiv, 'Password is required.');
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
    usernameField.addEventListener('blur', validateUsername);
    passwordField.addEventListener('blur', validatePassword);

    // Form submission validation
    form.addEventListener('submit', function(e) {
        const isUsernameValid = validateUsername();
        const isPasswordValid = validatePassword();
        
        if (!isUsernameValid || !isPasswordValid) {
            e.preventDefault();
        }
    });
});