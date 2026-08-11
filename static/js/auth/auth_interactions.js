/**
 * Authentication interactions and form validation
 */

// Password validation rules
const passwordRequirements = {
    length: { regex: /.{8,}/, text: 'At least 8 characters' },
    uppercase: { regex: /[A-Z]/, text: 'Uppercase letter' },
    lowercase: { regex: /[a-z]/, text: 'Lowercase letter' },
    digit: { regex: /\d/, text: 'Number' },
    special: { regex: /[!@#$%^&*(),.?":{}|<>]/, text: 'Special character' }
};

// Initialize auth page
function initAuth() {
    setupPasswordValidation();
    setupFormSwitching();
    setupShowPasswordToggle();
}

/**
 * Setup real-time password validation
 */
function setupPasswordValidation() {
    const passwordInput = document.getElementById('password');
    if (!passwordInput) return;

    passwordInput.addEventListener('input', (e) => {
        const password = e.target.value;
        updatePasswordRequirements(password);
    });
}

/**
 * Update password requirements visual feedback
 */
function updatePasswordRequirements(password) {
    Object.entries(passwordRequirements).forEach(([key, requirement]) => {
        const element = document.querySelector(`[data-req="${key}"]`);
        if (element) {
            if (requirement.regex.test(password)) {
                element.classList.add('met');
            } else {
                element.classList.remove('met');
            }
        }
    });
}

/**
 * Setup form field switching (login to register and vice versa)
 */
function setupFormSwitching() {
    const switchToRegisterLinks = document.querySelectorAll('[data-switch-to-register]');
    const switchToLoginLinks = document.querySelectorAll('[data-switch-to-login]');

    switchToRegisterLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = '/auth/register';
        });
    });

    switchToLoginLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = '/auth/login';
        });
    });
}

/**
 * Setup show/hide password toggle
 */
function setupShowPasswordToggle() {
    const passwordInputs = document.querySelectorAll('[type="password"]');

    passwordInputs.forEach(input => {
        const wrapper = input.parentElement;
        
        // Create toggle button
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'password-toggle';
        toggleBtn.innerHTML = '<i class="bi bi-eye"></i>';
        toggleBtn.style.cssText = `
            position: absolute;
            right: 0.75rem;
            top: 2.25rem;
            background: none;
            border: none;
            cursor: pointer;
            color: #94a3b8;
            font-size: 1rem;
            padding: 0.25rem;
            transition: color 0.2s ease;
        `;

        toggleBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            toggleBtn.innerHTML = `<i class="bi bi-eye${isPassword ? '-slash' : ''}"></i>`;
            toggleBtn.style.color = isPassword ? '#1d4ed8' : '#94a3b8';
        });

        // Make wrapper position relative for absolute positioning
        wrapper.style.position = 'relative';
        wrapper.appendChild(toggleBtn);
    });
}

/**
 * Setup form submission handlers
 */
function setupFormSubmission() {
    const loginForm = document.querySelector('[data-login]');
    const registerForm = document.querySelector('[data-register]');

    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            if (!validateLoginForm(loginForm)) {
                e.preventDefault();
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            if (!validateRegisterForm(registerForm)) {
                e.preventDefault();
            }
        });
    }
}

/**
 * Validate login form
 */
function validateLoginForm(form) {
    const email = form.querySelector('#email')?.value.trim();
    const password = form.querySelector('#password')?.value;

    if (!email || !isValidEmail(email)) {
        showError('Please enter a valid email address');
        return false;
    }

    if (!password) {
        showError('Please enter your password');
        return false;
    }

    return true;
}

/**
 * Validate register form
 */
function validateRegisterForm(form) {
    const fullName = form.querySelector('#full_name')?.value.trim();
    const email = form.querySelector('#email')?.value.trim();
    const password = form.querySelector('#password')?.value;
    const confirmPassword = form.querySelector('#confirm_password')?.value;

    if (!fullName || fullName.length < 2) {
        showError('Please enter a valid full name');
        return false;
    }

    if (!email || !isValidEmail(email)) {
        showError('Please enter a valid email address');
        return false;
    }

    if (!password) {
        showError('Please enter a password');
        return false;
    }

    if (!validatePasswordStrength(password)) {
        showError('Password does not meet requirements');
        return false;
    }

    if (password !== confirmPassword) {
        showError('Passwords do not match');
        return false;
    }

    return true;
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
}

/**
 * Validate password strength
 */
function validatePasswordStrength(password) {
    for (let req of Object.values(passwordRequirements)) {
        if (!req.regex.test(password)) {
            return false;
        }
    }
    return true;
}

/**
 * Show error message
 */
function showError(message) {
    const alertContainer = document.querySelector('.auth-right__content');
    if (!alertContainer) return;

    // Remove existing alerts
    const existingAlerts = alertContainer.querySelectorAll('.auth-alert');
    existingAlerts.forEach(alert => alert.remove());

    // Create error alert
    const alert = document.createElement('div');
    alert.className = 'auth-alert auth-alert--error';
    alert.innerHTML = `
        <i class="bi bi-x-circle"></i>
        <span>${message}</span>
    `;

    alertContainer.insertBefore(alert, alertContainer.firstChild);

    // Auto-remove after 5 seconds
    setTimeout(() => alert.remove(), 5000);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAuth);
} else {
    initAuth();
}

setupFormSubmission();
