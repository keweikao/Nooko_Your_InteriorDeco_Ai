import React, { useState } from 'react';

const BookingForm = ({ projectId }) => {
  const [name, setName] = useState('');
  const [contact, setContact] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    // In a real app, this would call a backend API
    console.log({
      projectId,
      name,
      contact,
    });
    setIsSubmitted(true);
  };

  const formStyle = {
    maxWidth: '500px',
    margin: '40px auto',
    padding: '30px',
    borderRadius: '8px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
    backgroundColor: '#fff',
  };

  const inputStyle = {
    width: '100%',
    padding: '12px',
    marginBottom: '20px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    boxSizing: 'border-box',
  };

  const buttonStyle = {
    width: '100%',
    padding: '15px',
    fontSize: '1em',
    fontWeight: 'bold',
    color: 'white',
    backgroundColor: '#28a745',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  };

  if (isSubmitted) {
    return (
      <div style={formStyle}>
        <h3>感謝您的預約！</h3>
        <p>我們的專員將會盡快與您聯絡。</p>
        <p>您的專案 ID 是：<strong>{projectId}</strong></p>
      </div>
    );
  }

  return (
    <form style={formStyle} onSubmit={handleSubmit}>
      <h2 style={{ textAlign: 'center', marginBottom: '30px' }}>預約免費到府丈量</h2>
      <p>請留下您的聯絡資訊，專員會盡快與您聯繫，安排專業團隊到府丈量與訪談。</p>
      
      <div>
        <label htmlFor="name">姓名</label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={inputStyle}
          required
        />
      </div>
      
      <div>
        <label htmlFor="contact">聯絡電話或 Email</label>
        <input
          id="contact"
          type="text"
          value={contact}
          onChange={(e) => setContact(e.target.value)}
          style={inputStyle}
          required
        />
      </div>

      <input type="hidden" value={projectId} />

      <button type="submit" style={buttonStyle}>
        確認送出
      </button>
    </form>
  );
};

export default BookingForm;
