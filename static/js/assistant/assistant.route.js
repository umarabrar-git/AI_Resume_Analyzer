const assistantCard = document.querySelector('.career-assistant-card');

if (assistantCard) {
    const input = assistantCard.querySelector('#assistantPrompt');
    const sendBtn = assistantCard.querySelector('.assistant-send');
    const actionButtons = assistantCard.querySelectorAll('.action-chip');
    const messages = assistantCard.querySelector('.assistant-bubbles');

    const buildBubble = (role, text) => {
        const bubble = document.createElement('div');
        bubble.className = `assistant-bubble ${role}`;
        const label = document.createElement('strong');
        label.textContent = role === 'user' ? 'You' : 'AI';
        const paragraph = document.createElement('p');
        paragraph.textContent = text;
        bubble.appendChild(label);
        bubble.appendChild(paragraph);
        return bubble;
    };

    const appendMessage = (role, text) => {
        if (!messages) {
            return;
        }

        const bubble = buildBubble(role, text);
        messages.appendChild(bubble);
        messages.scrollTop = messages.scrollHeight;
    };

    const disableInputs = () => {
        if (input) input.disabled = true;
        if (sendBtn) sendBtn.disabled = true;
        if (sendBtn) sendBtn.classList.add('is-loading');
    };

    const enableInputs = () => {
        if (input) input.disabled = false;
        if (sendBtn) sendBtn.disabled = false;
        if (sendBtn) sendBtn.classList.remove('is-loading');
    };

    const sendMessage = async (message, action = null) => {
        if (!message || !message.trim()) return;
        if (sendBtn && sendBtn.disabled) return;

        appendMessage('user', message.trim());

        if (input) input.value = '';
        disableInputs();

        try {
            const response = await fetch('/api/agent/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, action }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.errors?.[0] || 'Unable to reach the assistant.');
            }

            appendMessage('ai', data.content || 'The assistant did not return a response.');
        } catch (error) {
            appendMessage('ai', error.message || 'The assistant is temporarily unavailable.');
        } finally {
            enableInputs();
            if (input) input.focus();
        }
    };

    sendBtn?.addEventListener('click', () => {
        const value = input?.value || '';
        sendMessage(value);
    });

    input?.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            const value = input.value || '';
            sendMessage(value);
        }
    });

    actionButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const actionKey = button.textContent?.trim().toLowerCase().replace(/\s+/g, '_');
            const actionMap = {
                'improve_ats': 'improve_ats',
                'rewrite_summary': 'rewrite_summary',
                'add_skills': 'add_skills',
                'create_resume': 'create_resume',
                'generate_cover_letter': 'generate_cover_letter',
                'interview_prep': 'interview_prep',
            };
            const action = actionMap[actionKey] || null;
            sendMessage(button.textContent?.trim() || '', action);
        });
    });
}
