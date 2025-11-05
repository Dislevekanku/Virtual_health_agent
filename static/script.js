// Virtual Health Assistant - Frontend JavaScript

let currentSessionId = null;
let isTyping = false;
let conversationMessages = [];  // Track messages in current conversation

// DOM Elements
const welcomeScreen = document.getElementById('welcomeScreen');
const messagesContainer = document.getElementById('messagesContainer');
const messages = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const newChatBtn = document.getElementById('newChatBtn');
const typingIndicator = document.getElementById('typingIndicator');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeChat();
    setupEventListeners();
});

function initializeChat() {
    // Create new session
    createNewSession();
}

function setupEventListeners() {
    // Send button
    sendBtn.addEventListener('click', handleSendMessage);
    
    // Enter key to send (Shift+Enter for new line)
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    
    // Auto-resize textarea
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
    });
    
    // New chat button
    newChatBtn.addEventListener('click', startNewChat);
    
    // Quick start buttons
    document.querySelectorAll('.quick-start-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const message = e.target.dataset.message;
            messageInput.value = message;
            handleSendMessage();
        });
    });
}

async function createNewSession() {
    try {
        const response = await fetch('/api/session/new', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        if (data.success) {
            currentSessionId = data.session_id;
        }
    } catch (error) {
        console.error('Error creating session:', error);
        showError('Failed to initialize chat session. Please refresh the page.');
    }
}

async function handleSendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isTyping) {
        return;
    }
    
    // Disable input
    messageInput.disabled = true;
    sendBtn.disabled = true;
    isTyping = true;
    
    // Hide welcome screen
    if (welcomeScreen.style.display !== 'none') {
        welcomeScreen.style.display = 'none';
        messagesContainer.style.display = 'flex';
    }
    
    // Add user message to UI
    addMessage('user', message);
    
    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Send to backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: currentSessionId
            })
        });
        
        const data = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        if (data.success) {
            // Update session ID if needed
            if (data.session_id) {
                currentSessionId = data.session_id;
            }
            
            // Add assistant response
            addMessage('assistant', data.response);
            
            // Check if this is the end of conversation (summary page)
            if (data.current_page === 'Summary' || data.response.includes('summary') || data.response.includes('Summary')) {
                // Save conversation to history
                setTimeout(() => saveConversationToHistory(), 1000);
            }
            
            // Scroll to bottom
            scrollToBottom();
        } else {
            showError(data.error || 'Failed to get response. Please try again.');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();
        showError('Network error. Please check your connection and try again.');
    } finally {
        // Re-enable input
        messageInput.disabled = false;
        sendBtn.disabled = false;
        isTyping = false;
        messageInput.focus();
    }
}

function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? 'You' : 'AI';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // Format message (preserve line breaks)
    const formattedContent = content.split('\n').map(line => {
        if (line.trim() === '') return '<br>';
        return line.trim();
    }).join('<br>');
    
    messageContent.innerHTML = formattedContent;
    
    const messageTime = document.createElement('div');
    messageTime.className = 'message-time';
    messageTime.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageContent.appendChild(messageTime);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    messages.appendChild(messageDiv);
    scrollToBottom();
    
    // Track message for history
    conversationMessages.push({
        role: role,
        content: content,
        timestamp: new Date().toISOString()
    });
}

function showTypingIndicator() {
    typingIndicator.style.display = 'flex';
    messages.appendChild(typingIndicator);
    scrollToBottom();
}

function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
    if (typingIndicator.parentNode) {
        typingIndicator.parentNode.removeChild(typingIndicator);
    }
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    messages.appendChild(errorDiv);
    scrollToBottom();
    
    // Remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}

function saveConversationToHistory() {
    if (conversationMessages.length === 0) return;
    
    // Extract summary from conversation
    const lastAgentMessage = conversationMessages.filter(m => m.role === 'assistant').slice(-1)[0];
    const summary = {
        symptom: conversationMessages.find(m => m.role === 'user' && (m.content.includes('headache') || m.content.includes('nausea') || m.content.includes('dizzy')))?.content || 'N/A',
        triage: 'N/A',
        recommendation: 'N/A'
    };
    
    // Try to extract triage from agent response
    if (lastAgentMessage) {
        const content = lastAgentMessage.content.toLowerCase();
        if (content.includes('emergency') || content.includes('911')) {
            summary.triage = 'emergency';
        } else if (content.includes('urgent') || content.includes('same-day')) {
            summary.triage = 'urgent';
        } else if (content.includes('routine') || content.includes('rest')) {
            summary.triage = 'routine';
        }
    }
    
    const conversation = {
        session_id: currentSessionId,
        timestamp: new Date().toISOString(),
        messages: conversationMessages,
        summary: summary
    };
    
    // Save to server
    fetch('/api/conversation/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(conversation)
    }).catch(err => console.log('History save error:', err));
    
    // Also save to localStorage
    let history = JSON.parse(localStorage.getItem('conversationHistory') || '[]');
    history.push(conversation);
    if (history.length > 50) history = history.slice(-50);  // Keep last 50
    localStorage.setItem('conversationHistory', JSON.stringify(history));
}

function startNewChat() {
    // Save current conversation before starting new one
    if (conversationMessages.length > 0) {
        saveConversationToHistory();
    }
    
    // Clear messages
    messages.innerHTML = '';
    conversationMessages = [];
    
    // Show welcome screen
    welcomeScreen.style.display = 'flex';
    messagesContainer.style.display = 'none';
    
    // Create new session
    createNewSession();
    
    // Clear input
    messageInput.value = '';
    messageInput.focus();
}

// Health check on load
fetch('/api/health')
    .then(response => response.json())
    .then(data => {
        console.log('Server health:', data);
    })
    .catch(error => {
        console.error('Health check failed:', error);
    });

