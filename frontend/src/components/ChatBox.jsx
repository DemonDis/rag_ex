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

    let res; // Declare res outside the try block
    try {
      res = await fetch('http://localhost:8000/api/ask', {
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
      let errorMessage = "Ошибка сети: " + err.message;

      if (res) {
        errorMessage = `HTTP error! status: ${res.status} ${res.statusText}. `;
        if (err instanceof SyntaxError) {
          // Attempt to get raw response text if JSON parsing failed
          res.text().then(text => {
            errorMessage += `Malformed JSON response: ${text}`;
            setMessages(prev => [...prev, { text: errorMessage, isUser: false }]);
          }).catch(() => {
            // If .text() also fails, use the original error message
            errorMessage += "Could not parse response text.";
            setMessages(prev => [...prev, { text: errorMessage, isUser: false }]);
          });
        } else {
          // If res is defined but it's not a SyntaxError, use the original error message
          setMessages(prev => [...prev, { text: errorMessage + err.message, isUser: false }]);
        }
      } else {
        // If res is not defined (e.g., network error before fetch even completes)
        setMessages(prev => [...prev, { text: errorMessage, isUser: false }]);
      }
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
