import { setupRegisterForm } from './register_form.js';

// Initialize register form when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupRegisterForm);
} else {
    setupRegisterForm();
}
