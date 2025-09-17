// frontend/src/components/ChatBox.jsx

import React, { useState } from 'react';
import '../styles/ChatBox.css';

const ChatBox = ({ selectedModel }) => {
  const [messages, setMessages] = useState([
    { text: "Привет! Загрузи документ и задай вопрос.", isUser: false }
  ]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { text: input, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const res = await fetch('http://localhost:8000/api/ask', { // ← ✅ ИСПРАВЛЕНО!
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: input,
          model: selectedModel
        })
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      const botMessage = { text: data.answer, isUser: false };
      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error("Fetch error:", err);
      setMessages(prev => [...prev, { text: "Ошибка сети: " + err.message, isUser: false }]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      {messages.map((msg, i) => (
        <div
          key={i}
          className={`message ${msg.isUser ? 'user-message' : 'bot-message'}`}
        >
          {msg.text}
        </div>
      ))}
      <div className="input-area">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Задайте вопрос..."
          rows="2"
        />
        <button onClick={sendMessage}>Отправить</button>
      </div>
    </div>
  );
};

export default ChatBox;