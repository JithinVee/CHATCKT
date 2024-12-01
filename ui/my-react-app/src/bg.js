import React, { useState } from "react";
import "./bg.css"; // Link to the CSS file

const Bg = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");

  // Handle message send
  const handleSend = () => {
    if (userInput) {
      const newMessages = [
        ...messages,
        { sender: "user", text: userInput },
        { sender: "bot", text: "Hello! How can I assist you?" }, // Placeholder bot response
      ];
      setMessages(newMessages);
      setUserInput(""); // Clear input field after sending message
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <h2>Chat with AI</h2>
      </div>
      <div className="chatbot-messages">
        {messages.map((msg, index) => (
          <div key={index} className={msg.sender}>
            <span>{msg.text}</span>
          </div>
        ))}
      </div>

      <div className="chatbot-input">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Type a message"
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default Bg;
