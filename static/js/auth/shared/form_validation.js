/**
 * Shared Form Validation Utilities
 */

export const passwordRequirements = {
    length: { regex: /.{8,}/, text: 'At least 8 characters' },
    uppercase: { regex: /[A-Z]/, text: 'Uppercase letter' },
    lowercase: { regex: /[a-z]/, text: 'Lowercase letter' },
    digit: { regex: /\d/, text: 'Number' },
    special: { regex: /[!@#$%^&*(),.?":{}|<>]/, text: 'Special character' }
};

export function isValidEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
}

export function validatePasswordStrength(password) {
    for (let req of Object.values(passwordRequirements)) {
        if (!req.regex.test(password)) {
            return false;
        }
    }
    return true;
}

export function showAlert(message, category = 'error') {
    const alertContainer = document.querySelector('.auth-right__content');
    if (!alertContainer) return;

    // Remove existing alerts
    const existingAlerts = alertContainer.querySelectorAll('.auth-alert');
    existingAlerts.forEach(alert => alert.remove());

    // Create alert
    const alert = document.createElement('div');
    alert.className = `auth-alert auth-alert--${category}`;
    alert.innerHTML = `
        <i class="bi bi-${category === 'success' ? 'check-circle' : category === 'error' ? 'x-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;

    alertContainer.insertBefore(alert, alertContainer.firstChild);

    // Auto-remove after 5 seconds
    setTimeout(() => alert.remove(), 5000);
}
