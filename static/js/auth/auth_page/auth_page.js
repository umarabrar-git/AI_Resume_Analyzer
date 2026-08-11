/**
 * Auth Page Interactions
 */

import { setupPasswordToggle } from '../shared/password_toggle.js';

export function setupAuthPage() {
    // Setup password toggles for all password inputs
    setupPasswordToggle();
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupAuthPage);
} else {
    setupAuthPage();
}
