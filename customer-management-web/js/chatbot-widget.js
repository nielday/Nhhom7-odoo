/**
 * AI Chatbot Widget
 * Integrates with Odoo Chatbot Support Module
 */

class ChatbotWidget {
    constructor(config = {}) {
        this.config = {
            apiUrl: config.apiUrl || 'http://localhost:8069',
            sessionId: this.generateSessionId(),
            partnerId: config.partnerId || null,
            autoOpen: config.autoOpen || false,
            ...config
        };

        this.isOpen = false;
        this.conversationId = null;
        this.isTyping = false;

        this.init();
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    init() {
        this.createWidget();
        this.attachEventListeners();
        this.loadWelcomeMessage();

        if (this.config.autoOpen) {
            setTimeout(() => this.toggleChat(), 1000);
        }
    }

    createWidget() {
        const widgetHTML = `
            <div class="chatbot-widget">
                <button class="chatbot-button" id="chatbot-toggle">
                    <svg class="chat-icon" viewBox="0 0 24 24">
                        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                    </svg>
                    <svg class="close-icon" viewBox="0 0 24 24">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                </button>
                
                <div class="chatbot-window" id="chatbot-window">
                    <div class="chatbot-header">
                        <div class="chatbot-avatar">🤖</div>
                        <div class="chatbot-header-text">
                            <h3>Trợ lý AI</h3>
                            <p>Luôn sẵn sàng hỗ trợ bạn</p>
                        </div>
                    </div>
                    
                    <div class="chatbot-messages" id="chatbot-messages">
                        <!-- Messages will be inserted here -->
                    </div>
                    
                    <div class="chatbot-input">
                        <input 
                            type="text" 
                            id="chatbot-input" 
                            placeholder="Nhập tin nhắn..."
                            autocomplete="off"
                        />
                        <button class="chatbot-send-btn" id="chatbot-send">
                            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', widgetHTML);
    }

    attachEventListeners() {
        const toggleBtn = document.getElementById('chatbot-toggle');
        const sendBtn = document.getElementById('chatbot-send');
        const input = document.getElementById('chatbot-input');

        toggleBtn.addEventListener('click', () => this.toggleChat());
        sendBtn.addEventListener('click', () => this.sendMessage());
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        const window = document.getElementById('chatbot-window');
        const button = document.getElementById('chatbot-toggle');

        if (this.isOpen) {
            window.classList.add('active');
            button.classList.add('active');
            document.getElementById('chatbot-input').focus();
        } else {
            window.classList.remove('active');
            button.classList.remove('active');
        }
    }

    async loadWelcomeMessage() {
        try {
            const response = await this.apiCall('/chatbot/api/welcome', {});
            if (response.success) {
                this.addMessage(response.message, 'bot');
            }
        } catch (error) {
            console.error('Failed to load welcome message:', error);
            this.addMessage('Xin chào! Tôi có thể giúp gì cho bạn? 😊', 'bot');
        }
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();

        if (!message || this.isTyping) return;

        // Add user message to UI
        this.addMessage(message, 'user');
        input.value = '';

        // Show typing indicator
        this.showTyping();

        try {
            const response = await this.apiCall('/chatbot/api/chat', {
                message: message,
                session_id: this.config.sessionId,
                partner_id: this.config.partnerId
            });

            this.hideTyping();

            if (response.success) {
                this.conversationId = response.conversation_id;
                this.addMessage(response.response, 'bot');
            } else {
                this.addMessage('Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.', 'bot');
            }
        } catch (error) {
            this.hideTyping();
            console.error('Chat error:', error);
            this.addMessage('Không thể kết nối đến server. Vui lòng thử lại sau.', 'bot');
        }
    }

    addMessage(text, type = 'bot') {
        const messagesContainer = document.getElementById('chatbot-messages');
        const time = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });

        const messageHTML = `
            <div class="chatbot-message ${type}">
                <div class="message-avatar">${type === 'bot' ? '🤖' : '👤'}</div>
                <div class="message-content">
                    ${text}
                    <div class="message-time">${time}</div>
                </div>
            </div>
        `;

        messagesContainer.insertAdjacentHTML('beforeend', messageHTML);
        this.scrollToBottom();
    }

    showTyping() {
        this.isTyping = true;
        const messagesContainer = document.getElementById('chatbot-messages');

        const typingHTML = `
            <div class="chatbot-message bot" id="typing-indicator">
                <div class="message-avatar">🤖</div>
                <div class="typing-indicator active">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;

        messagesContainer.insertAdjacentHTML('beforeend', typingHTML);
        this.scrollToBottom();
    }

    hideTyping() {
        this.isTyping = false;
        const indicator = document.getElementById('typing-indicator');
        if (indicator) indicator.remove();
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatbot-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async apiCall(endpoint, data) {
        const url = `${this.config.apiUrl}${endpoint}`;

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: data,
                id: Date.now()
            })
        });

        const result = await response.json();
        return result.result;
    }
}

// Auto-initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new ChatbotWidget({
        apiUrl: 'http://localhost:3000',  // Use proxy server
        autoOpen: false
    });
});
