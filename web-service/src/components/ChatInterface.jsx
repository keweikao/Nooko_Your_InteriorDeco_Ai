import React, { useState } from 'react';

const ChatInterface = ({ initialMessages = [] }) => {
  const [messages, setMessages] = useState(initialMessages);
  const [inputValue, setInputValue] = useState('');

  const handleSendMessage = () => {
    if (inputValue.trim() === '') return;

    const userMessage = {
      agent: 'USER',
      message: inputValue,
    };

    // In a real app, this would call the backend API
    // and the response would be a new agent message.
    // For now, we simulate a response.
    const agentResponse = {
        agent: 'CLIENT_MANAGER',
        message: `您提到了 "${inputValue}"，關於這點，我想更深入了解...`,
        metadata: inputValue.includes("風格") ? { image_url: 'https://via.placeholder.com/400x300.png?text=Style+Reference' } : null
    };

    setMessages([...messages, userMessage, agentResponse]);
    setInputValue('');
  };

  const Message = ({ msg }) => {
    const isUser = msg.agent === 'USER';
    const avatarSrc = isUser 
      ? 'https://placehold.co/40x40/dcf8c6/888?text=S&font=sans' 
      : 'https://placehold.co/40x40/EBF0F4/7C8490?text=A&font=sans';

    return (
      <div style={{ 
        margin: '10px', 
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        alignItems: 'flex-start',
        alignSelf: isUser ? 'flex-end' : 'flex-start',
      }}>
        <img 
          src={avatarSrc} 
          alt={`${msg.agent} avatar`} 
          style={{ width: '40px', height: '40px', borderRadius: '50%', margin: '0 10px' }} 
        />
        <div style={{ 
          padding: '10px', 
          borderRadius: '8px', 
          backgroundColor: isUser ? '#dcf8c6' : '#fff',
          maxWidth: '70%',
          border: '1px solid #eee'
        }}>
          <p style={{ margin: '0' }}>{msg.message}</p>
          {msg.metadata?.image_url && (
            <img 
              src={msg.metadata.image_url} 
              alt="Style Reference" 
              style={{ maxWidth: '100%', borderRadius: '4px', marginTop: '10px' }} 
            />
          )}
        </div>
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '80vh', border: '1px solid #ccc' }}>
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', padding: '10px' }}>
        {messages.map((msg, index) => (
          <Message key={index} msg={msg} />
        ))}
      </div>
      <div style={{ display: 'flex', padding: '10px', borderTop: '1px solid #ccc' }}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          style={{ flex: 1, padding: '10px', borderRadius: '20px', border: '1px solid #ccc' }}
        />
        <button onClick={handleSendMessage} style={{ marginLeft: '10px', padding: '10px 20px', borderRadius: '20px', border: 'none', backgroundColor: '#007bff', color: 'white' }}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
