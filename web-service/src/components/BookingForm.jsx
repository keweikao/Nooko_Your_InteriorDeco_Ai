import React, { useState } from 'react';

/**
 * 簡化版預約表單：僅收集姓名與電話，
 * Input: projectId (從 App 傳入)，Output: 之後可串接 /projects/book API。
 */
const BookingForm = ({ projectId, apiBaseUrl, onBookingComplete }) => {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      const response = await fetch(`${apiBaseUrl}/projects/${projectId}/book`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, phone })
      });

      if (!response.ok) {
        const detail = await response.json().catch(() => null);
        throw new Error(detail?.detail || '預約送出失敗，請稍後再試');
      }

      setIsSubmitted(true);
      if (onBookingComplete) {
        onBookingComplete();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
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
      {error && (
        <p style={{ color: '#d32f2f', fontSize: '0.9em' }}>{error}</p>
      )}
      
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
        <label htmlFor="phone">聯絡電話</label>
        <input
          id="phone"
          type="tel"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          style={inputStyle}
          required
        />
      </div>

      <input type="hidden" value={projectId} />

      <button type="submit" style={buttonStyle} disabled={isSubmitting}>
        {isSubmitting ? '送出中...' : '確認送出'}
      </button>
    </form>
  );
};

export default BookingForm;
