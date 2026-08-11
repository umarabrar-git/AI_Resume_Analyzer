/**
 * Login Form Interactions
 */

import { isValidEmail, showAlert } from '../shared/form_validation.js';
import { setupPasswordToggle } from '../shared/password_toggle.js';

export function setupLoginForm() {
    const loginForm = document.querySelector('[data-login]');
    if (!loginForm) return;

    // Setup password toggle
    setupPasswordToggle();

    // Form submission
    loginForm.addEventListener('submit', (e) => {
        if (!validateLoginForm(loginForm)) {
            e.preventDefault();
        }
    });

    // Setup form switching
    const switchToRegisterLinks = document.querySelectorAll('[data-switch-to-register]');
    switchToRegisterLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = '/auth/register';
        });
    });
}

function validateLoginForm(form) {
    const email = form.querySelector('#email')?.value.trim();
    const password = form.querySelector('#password')?.value;

    if (!email || !isValidEmail(email)) {
        showAlert('Please enter a valid email address');
        return false;
    }

    if (!password) {
        showAlert('Please enter your password');
        return false;
    }

    return true;
}
