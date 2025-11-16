import React from 'react';

const FinalResult = ({ quote, renderingUrl }) => {

  const tableHeaderStyle = {
    backgroundColor: '#f2f2f2',
    padding: '12px',
    textAlign: 'left',
    borderBottom: '2px solid #ddd',
  };

  const tableCellStyle = {
    padding: '12px',
    borderBottom: '1px solid #ddd',
  };

  const suggestionRowStyle = {
    backgroundColor: '#fffbe6', // Light yellow for suggested items
  };

  const ctaButtonStyle = {
    display: 'block',
    width: '100%',
    padding: '15px',
    marginTop: '40px',
    fontSize: '1.2em',
    fontWeight: 'bold',
    color: 'white',
    backgroundColor: '#007bff',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    textAlign: 'center',
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('zh-TW', { style: 'currency', currency: 'TWD', minimumFractionDigits: 0 }).format(amount);
  };

  const handleBooking = () => {
    // This will be implemented in a later task
    alert('「預約免費丈量」功能將在後續實現！');
  };

  return (
    <div style={{ fontFamily: 'sans-serif', padding: '20px' }}>
      <h2>您的專屬設計方案</h2>
      
      <div style={{ marginBottom: '30px' }}>
        <h3>概念渲染圖</h3>
        <p>這是我們根據您的需求，為您量身打造的風格概念圖：</p>
        <img 
          src={renderingUrl} 
          alt="Final Concept Rendering" 
          style={{ maxWidth: '100%', height: 'auto', borderRadius: '8px', boxShadow: '0 4px 8px rgba(0,0,0,0.1)' }} 
        />
      </div>

      <div>
        <h3>詳細規格報價單</h3>
        <p>以下是根據您的需求和我們的專業建議，為您整理的詳細報價：</p>
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
          <thead>
            <tr>
              <th style={tableHeaderStyle}>項目</th>
              <th style={tableHeaderStyle}>規格</th>
              <th style={tableHeaderStyle}>數量</th>
              <th style={tableHeaderStyle}>單價</th>
              <th style={tableHeaderStyle}>總價</th>
            </tr>
          </thead>
          <tbody>
            {quote.line_items.map((item, index) => (
              <tr key={index} style={item.is_suggestion ? suggestionRowStyle : {}}>
                <td style={tableCellStyle}>
                  {item.item_name}
                  {item.is_suggestion && <span style={{ color: '#d97706', marginLeft: '8px', fontSize: '0.8em' }}>[建議項目]</span>}
                </td>
                <td style={tableCellStyle}>{item.spec}</td>
                <td style={tableCellStyle}>{`${item.quantity} ${item.unit}`}</td>
                <td style={tableCellStyle}>{formatCurrency(item.unit_price)}</td>
                <td style={tableCellStyle}>{formatCurrency(item.total_price)}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <td colSpan="4" style={{ ...tableCellStyle, textAlign: 'right', fontWeight: 'bold', fontSize: '1.2em' }}>總計：</td>
              <td style={{ ...tableCellStyle, fontWeight: 'bold', fontSize: '1.2em' }}>{formatCurrency(quote.total_price)}</td>
            </tr>
          </tfoot>
        </table>
      </div>

      <button style={ctaButtonStyle} onClick={handleBooking}>
        預約免費丈量
      </button>
    </div>
  );
};

export default FinalResult;
