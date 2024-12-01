import React, { useState } from 'react';
import './Chatbot.css';  // Import the CSS file
const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');

  // Handle message send
  const handleSend = () => {
    if (userInput) {
      const newMessages = [
        ...messages,
        { sender: 'user', text: userInput },
        { sender: 'bot', text: 'Hello! How can I assist you?' },
      ];
      setMessages(newMessages);
      setUserInput(''); // Clear input field after sending message
    }
  };

  return (
    <div className="chat-app-container">
      <div className="chat-container">
        <div className="chat-header">CrickLyst</div>
        <div className="chat-body">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`chat-message ${msg.sender === 'user' ? 'user-message' : 'bot-message'}`}
            >
              {msg.text}
            </div>
          ))}
        </div>
        <div className="chat-input">
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Type a message..."
          />
          <button onClick={handleSend}>Send</button>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
