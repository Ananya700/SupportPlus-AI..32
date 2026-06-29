document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    
    const feedbackIssue = document.getElementById('feedback-issue');
    const feedbackSolution = document.getElementById('feedback-solution');
    const submitFeedbackBtn = document.getElementById('submit-feedback-btn');
    const feedbackStatus = document.getElementById('feedback-status');

    // Generate a unique session ID for this browser tab/session
    const sessionId = 'session_' + Math.random().toString(36).substring(2, 15);

    // Configure marked.js to be secure
    marked.setOptions({
        headerIds: false,
        mangle: false,
        breaks: true
    });

    // Auto-resize textarea
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if (this.value.trim() === '') {
            sendBtn.disabled = true;
        } else {
            sendBtn.disabled = false;
        }
    });

    // Handle sending message
    const sendMessage = async () => {
        const text = userInput.value.trim();
        if (!text) return;

        // Add user message to UI
        appendMessage(text, 'user');
        
        // Reset input
        userInput.value = '';
        userInput.style.height = 'auto';
        sendBtn.disabled = true;

        // Add loading state
        const loadingId = appendLoading();

        try {
            const response = await fetch('/api/support/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: text, user_id: 'default_user', session_id: sessionId })
            });

            const data = await response.json();
            removeLoading(loadingId);
            appendMessage(
                data.answer || "I couldn't generate an answer.",
                'system',
                { cached: data.cached, source: data.source }
            );
        } catch (error) {
            removeLoading(loadingId);
            appendMessage("**Error:** Could not connect to the server.", 'system');
            console.error('Error:', error);
        }
    };

    // Handle feedback submission
    const submitFeedback = async () => {
        const issue = feedbackIssue.value.trim();
        const solution = feedbackSolution.value.trim();

        if (!issue || !solution) {
            showStatus('Please fill in both fields.', 'error');
            return;
        }

        submitFeedbackBtn.disabled = true;
        submitFeedbackBtn.querySelector('.btn-text').textContent = 'Storing...';

        try {
            const response = await fetch('/api/support/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    issue, 
                    preferred_solution: solution,
                    user_id: 'default_user' 
                })
            });

            if (response.ok) {
                showStatus('Solution learned!', 'success');
                feedbackIssue.value = '';
                feedbackSolution.value = '';
            } else {
                showStatus('Failed to store solution.', 'error');
            }
        } catch (error) {
            showStatus('Connection error.', 'error');
            console.error('Error:', error);
        } finally {
            submitFeedbackBtn.disabled = false;
            submitFeedbackBtn.querySelector('.btn-text').textContent = 'Store in Memory';
        }
    };

    // UI Helpers
    const SOURCE_LABELS = {
        'cache': { icon: '⚡', label: 'Cached', cls: 'badge-cache' },
        'rag': { icon: '📚', label: 'Internal FAQ', cls: 'badge-rag' },
        'web': { icon: '🌐', label: 'Web Search', cls: 'badge-web' },
        'memory+rag': { icon: '🧠', label: 'Memory + FAQ', cls: 'badge-memory' },
        'memory+web': { icon: '🧠', label: 'Memory + Web', cls: 'badge-memory' },
    };

    const appendMessage = (text, sender, meta = {}) => {
        const div = document.createElement('div');
        div.className = `message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = `avatar ${sender}-avatar`;
        if (sender === 'user') {
            avatar.textContent = 'Y';
        } else {
            avatar.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>';
        }
        
        const content = document.createElement('div');
        content.className = 'content markdown-body';
        
        // Parse markdown using marked.js
        content.innerHTML = marked.parse(text);

        // Add source badge for system messages
        if (sender === 'system' && meta.source) {
            const info = SOURCE_LABELS[meta.source] || { icon: '🤖', label: meta.source, cls: 'badge-default' };
            const badge = document.createElement('div');
            badge.className = `source-badge ${info.cls}`;
            badge.innerHTML = `${info.icon} ${info.label}`;
            content.appendChild(badge);
        }

        div.appendChild(avatar);
        div.appendChild(content);
        chatBox.appendChild(div);
        
        scrollToBottom();
    };

    const appendLoading = () => {
        const id = 'loading-' + Date.now();
        const div = document.createElement('div');
        div.className = 'message system-message';
        div.id = id;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar system-avatar';
        avatar.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>';
        
        const content = document.createElement('div');
        content.className = 'content';
        content.innerHTML = `
            <div class="loading-indicator">
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
            </div>
        `;

        div.appendChild(avatar);
        div.appendChild(content);
        chatBox.appendChild(div);
        
        scrollToBottom();
        return id;
    };

    const removeLoading = (id) => {
        const el = document.getElementById(id);
        if (el) el.remove();
    };

    const showStatus = (text, type) => {
        feedbackStatus.textContent = text;
        feedbackStatus.className = `status-msg status-${type}`;
        setTimeout(() => {
            feedbackStatus.textContent = '';
        }, 3000);
    };

    const scrollToBottom = () => {
        chatBox.scrollTo({
            top: chatBox.scrollHeight,
            behavior: 'smooth'
        });
    };

    // Event Listeners
    sendBtn.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.disabled) sendMessage();
        }
    });

    submitFeedbackBtn.addEventListener('click', submitFeedback);
    
    // Initial state
    sendBtn.disabled = true;
});
