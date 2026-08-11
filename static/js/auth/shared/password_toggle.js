/**
 * Password Show/Hide Toggle
 */

export function setupPasswordToggle() {
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

        // Make wrapper position relative
        wrapper.style.position = 'relative';
        wrapper.appendChild(toggleBtn);
    });
}
