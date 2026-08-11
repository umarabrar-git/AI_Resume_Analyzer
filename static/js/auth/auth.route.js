/**
 * Auth Module Main Orchestrator
 * Routes JavaScript loading based on current page
 */

// Determine which auth page we're on
const currentPath = window.location.pathname;

if (currentPath.includes('/auth/login')) {
    // Load login-specific interactions
    import('./login/login.route.js').catch(err => console.error('Failed to load login module:', err));
} else if (currentPath.includes('/auth/register')) {
    // Load register-specific interactions
    import('./register/register.route.js').catch(err => console.error('Failed to load register module:', err));
}

// Load shared auth page interactions
import('./auth_page/auth_page.js').catch(err => console.error('Failed to load auth page module:', err));
