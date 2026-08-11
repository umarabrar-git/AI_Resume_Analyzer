/**
 * Register Form Interactions and Validation
 */

import { passwordRequirements, isValidEmail, validatePasswordStrength, showAlert } from '../shared/form_validation.js';
import { setupPasswordToggle } from '../shared/password_toggle.js';

export function setupRegisterForm() {
    const registerForm = document.querySelector('[data-register]');
    if (!registerForm) return;

    // Setup password toggle
    setupPasswordToggle();

    // Setup password validation
    setupPasswordValidation();

    // Form submission
    registerForm.addEventListener('submit', (e) => {
        if (!validateRegisterForm(registerForm)) {
            e.preventDefault();
        }
    });

    // Setup form switching
    const switchToLoginLinks = document.querySelectorAll('[data-switch-to-login]');
    switchToLoginLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = '/auth/login';
        });
    });
}

function setupPasswordValidation() {
    const passwordInput = document.getElementById('password');
    if (!passwordInput) return;

    passwordInput.addEventListener('input', (e) => {
        const password = e.target.value;
        updatePasswordRequirements(password);
    });
}

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

function validateRegisterForm(form) {
    const fullName = form.querySelector('#full_name')?.value.trim();
    const email = form.querySelector('#email')?.value.trim();
    const password = form.querySelector('#password')?.value;
    const confirmPassword = form.querySelector('#confirm_password')?.value;

    if (!fullName || fullName.length < 2) {
        showAlert('Please enter a valid full name');
        return false;
    }

    if (!email || !isValidEmail(email)) {
        showAlert('Please enter a valid email address');
        return false;
    }

    if (!password) {
        showAlert('Please enter a password');
        return false;
    }

    if (!validatePasswordStrength(password)) {
        showAlert('Password does not meet requirements');
        return false;
    }

    if (password !== confirmPassword) {
        showAlert('Passwords do not match');
        return false;
    }

    return true;
}
