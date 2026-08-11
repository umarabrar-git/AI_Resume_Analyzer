import { setupLoginForm } from './login_form.js';

// Initialize login form when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupLoginForm);
} else {
    setupLoginForm();
}
