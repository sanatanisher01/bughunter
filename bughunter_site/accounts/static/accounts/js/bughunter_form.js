document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('bughunter-form');
    const githubUrlField = document.getElementById('id_github_url');
    const zipFileField = document.getElementById('id_zip_file');
    const analyzeBtn = document.getElementById('analyze-btn');
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoading = analyzeBtn.querySelector('.btn-loading');

    const codeInputField = document.getElementById('id_code_input');
    const languageField = document.getElementById('id_language');
    const languageGroup = document.getElementById('language-group');
    
    function validateForm() {
        const githubUrl = githubUrlField.value.trim();
        const zipFile = zipFileField.files[0];
        const codeInput = codeInputField.value.trim();
        const language = languageField.value;
        
        const githubError = document.getElementById('github-url-error');
        const zipError = document.getElementById('zip-file-error');
        const codeError = document.getElementById('code-input-error');
        const langError = document.getElementById('language-error');
        
        // Clear previous errors
        clearError(githubError);
        clearError(zipError);
        clearError(codeError);
        clearError(langError);
        
        const inputCount = [githubUrl, zipFile, codeInput].filter(Boolean).length;
        
        // Check if at least one input is provided
        if (inputCount === 0) {
            showError(githubError, 'Please provide a GitHub URL, upload a .zip file, or paste code directly.');
            return false;
        }
        
        // Check if multiple inputs are provided
        if (inputCount > 1) {
            showError(githubError, 'Please use only one input method.');
            return false;
        }
        
        // Validate code input requires language
        if (codeInput && !language) {
            showError(langError, 'Please select a programming language for your code.');
            return false;
        }
        
        // Validate GitHub URL format
        if (githubUrl) {
            if (!githubUrl.includes('github.com')) {
                showError(githubError, 'Please provide a valid GitHub repository URL.');
                return false;
            }
            
            const githubRegex = /^https?:\/\/(www\.)?github\.com\/[\w\-\.]+\/[\w\-\.]+\/?$/;
            if (!githubRegex.test(githubUrl)) {
                showError(githubError, 'Please provide a valid GitHub repository URL (e.g., https://github.com/user/repo).');
                return false;
            }
        }
        
        // Validate zip file
        if (zipFile) {
            if (!zipFile.name.toLowerCase().endsWith('.zip')) {
                showError(zipError, 'Please upload a .zip file.');
                return false;
            }
            
            // Check file size (50MB limit)
            const maxSize = 50 * 1024 * 1024; // 50MB in bytes
            if (zipFile.size > maxSize) {
                showError(zipError, 'File size must be less than 50MB.');
                return false;
            }
        }
        
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

    function showLoading() {
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline';
        analyzeBtn.disabled = true;
        
        // Show progress section
        const progressSection = document.getElementById('analysis-progress');
        progressSection.style.display = 'block';
        
        // Simulate progress steps
        setTimeout(() => updateProgress('step-download', '✅', 'Project downloaded/extracted'), 1000);
        setTimeout(() => updateProgress('step-collect', '✅', 'Code files collected'), 3000);
        setTimeout(() => updateProgress('step-analyze', '🤖', 'AI analyzing code... (this may take a while)'), 5000);
    }
    
    function updateProgress(stepId, icon, text) {
        const step = document.getElementById(stepId);
        const stepIcon = step.querySelector('.step-icon');
        const stepText = step.querySelector('.step-text');
        
        stepIcon.textContent = icon;
        stepText.textContent = text;
        step.classList.add('completed');
    }

    function hideLoading() {
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        analyzeBtn.disabled = false;
    }

    // Clear other fields when one is selected
    githubUrlField.addEventListener('input', function() {
        if (this.value.trim()) {
            zipFileField.value = '';
            codeInputField.value = '';
            languageGroup.style.display = 'none';
        }
    });

    zipFileField.addEventListener('change', function() {
        if (this.files[0]) {
            githubUrlField.value = '';
            codeInputField.value = '';
            languageGroup.style.display = 'none';
        }
    });
    
    codeInputField.addEventListener('input', function() {
        if (this.value.trim()) {
            githubUrlField.value = '';
            zipFileField.value = '';
            languageGroup.style.display = 'block';
        } else {
            languageGroup.style.display = 'none';
        }
    });

    // Form submission
    form.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
            return;
        }
        
        // Show loading state
        showLoading();
        
        // Add a timeout to prevent infinite loading in case of errors
        setTimeout(function() {
            hideLoading();
        }, 300000); // 5 minutes timeout
    });

    // Real-time validation
    githubUrlField.addEventListener('blur', function() {
        if (this.value.trim()) {
            validateForm();
        }
    });

    zipFileField.addEventListener('change', function() {
        if (this.files[0]) {
            validateForm();
        }
    });
});