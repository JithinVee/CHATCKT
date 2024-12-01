import React, { useState } from 'react';
import './Chatbot.css';  // Import the CSS file

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');

  // Handle message send
  const handleSend = async () => {
    if (userInput) {
      // Add the user's message to the UI
      const newMessages = [...messages, { sender: 'user', text: userInput }];
      setMessages(newMessages);
      setUserInput('');
  
      try {
        // Make the API call
        const response = await fetch('http://127.0.0.1:8000/query', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ question: userInput }), // Use the user's input as the query
        });
  
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
  
        const data = await response.json();
  
        // Check the response status and display the bot's response
        if (data.status) {
          setMessages((prevMessages) => [
            ...prevMessages,
            { sender: 'bot', text: data.response }, // Display the response from the API
          ]);
        } else {
          setMessages((prevMessages) => [
            ...prevMessages,
            { sender: 'bot', text: 'I didn’t understand that.' },
          ]);
        }
      } catch (error) {
        console.error('Error making API call:', error);
  
        // Add an error message to the bot's response
        setMessages((prevMessages) => [
          ...prevMessages,
          { sender: 'bot', text: 'An error occurred. Please try again later.' },
        ]);
      }
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
              className={`chat-message ${msg.sender === 'user' ? 'user-message' : 'bot-message'}`} // Fixed here
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
