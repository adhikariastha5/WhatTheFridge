import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './ChatInterface.css';

function ChatInterface({ conversationId }) {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    
    // Add user message to UI
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/chat', {
        message: userMessage,
        conversation_id: conversationId,
      });

      // Add assistant response to UI
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.data.response 
      }]);

      // If recipes were updated, show notification
      if (response.data.updated_recipes) {
        setMessages(prev => [...prev, {
          role: 'system',
          content: 'Recipe has been customized! Check the updated recipe above.'
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'system',
        content: `Error: ${error.response?.data?.detail || error.message}`
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-interface">
      <h3>Chat with Your Cooking Assistant</h3>
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <p>Ask me anything about your recipes!</p>
            <p className="suggestions">
              Try: "Make it for 4 people", "I don't have an oven", or "Make it spicier"
            </p>
          </div>
        )}
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="message-content">
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="message-content loading">
              Thinking...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSend} className="chat-input-form">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask about your recipes..."
          className="chat-input"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !inputMessage.trim()}
          className="send-btn"
        >
          Send
        </button>
      </form>
    </div>
  );
}

export default ChatInterface;

