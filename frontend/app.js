const BACKEND_URL = 'http://localhost:8000';
let conversationId = null;
let authToken = localStorage.getItem('auth_token');
let userId = localStorage.getItem('user_id');

// Check authentication
if (!authToken || !userId) {
    alert('Please log in first');
    // For development, you can set mock values:
    // authToken = 'mock_token';
    // userId = 'test_user';
}

// Send message to backend
async function sendMessage(message) {
    try {
        const response = await fetch(`${BACKEND_URL}/api/${userId}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                conversation_id: conversationId,
                message: message
            })
        });

        if (response.status === 401) {
            // Token expired
            localStorage.removeItem('auth_token');
            alert('Session expired. Please log in again.');
            return null;
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error);
        }

        const data = await response.json();
        conversationId = data.conversation_id;  // Save for next request
        return data.response;
    } catch (error) {
        console.error('Error sending message:', error);
        throw error;
    }
}

// Initialize ChatKit
const chat = ChatKit.create({
    container: document.getElementById('chat-container'),
    placeholder: 'Ask me to manage your tasks...',
    onSend: async (message) => {
        try {
            const response = await sendMessage(message);
            if (response) {
                chat.addMessage({ role: 'assistant', content: response });
            }
        } catch (error) {
            chat.addMessage({
                role: 'system',
                content: `Error: ${error.message}`
            });
        }
    }
});
