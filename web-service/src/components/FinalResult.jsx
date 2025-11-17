import React, { useState, useEffect } from 'react';
import './FinalResult.css';

const FinalResult = ({ projectId, apiBaseUrl, projectBrief, onBookingRequest }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);

  useEffect(() => {
    if (projectId && apiBaseUrl) {
      fetchAnalysisResult();
    }
  }, [projectId, apiBaseUrl]);

  const fetchAnalysisResult = async () => {
    try {
      setLoading(true);
      // 從後端 /analysis-result 取得多 Agent 的成果（input: projectId, output: quote/rendering_summary）
      const response = await fetch(`${apiBaseUrl}/projects/${projectId}/analysis-result`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAnalysisResult(data);
        setError(null);
      } else {
        setError('無法載入分析結果');
      }
    } catch (err) {
      console.error('Error fetching analysis result:', err);
      setError('載入分析結果時發生錯誤');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('zh-TW', {
      style: 'currency',
      currency: 'TWD',
      minimumFractionDigits: 0
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="final-result-container loading">
        <div className="loading-spinner"></div>
        <p>正在生成您的專屬分析結果...</p>
      </div>
    );
  }

  if (error || !analysisResult) {
    return (
      <div className="final-result-container error">
        <div className="error-message">
          <p>⚠️ {error || '無法載入分析結果'}</p>
          <button onClick={fetchAnalysisResult} className="retry-button">重新試試</button>
        </div>
      </div>
    );
  }

  const { rendering_url, quote, summary } = analysisResult;

  return (
    <div className="final-result-container">
      {/* 概念渲染圖區塊 */}
      <div className="result-section rendering-section">
        <h3 className="section-title">
          <span className="section-icon">🎨</span>
          您的專屬設計概念
        </h3>
        {rendering_url && (
          <div className="rendering-container">
            <img
              src={rendering_url}
              alt="Final Concept Rendering"
              className="rendering-image"
            />
          </div>
        )}
        {summary && (
          <div className="summary-box">
            <p className="summary-text">{summary}</p>
          </div>
        )}
      </div>

      {/* 報價單區塊 */}
      <div className="result-section quote-section">
        <h3 className="section-title">
          <span className="section-icon">📋</span>
          詳細規格報價單
        </h3>
        <p className="section-description">
          根據您的需求和我們的專業分析，為您整理的詳細報價
        </p>

        {quote && quote.line_items && (
          <div className="quote-table-wrapper">
            <table className="quote-table">
              <thead>
                <tr>
                  <th>項目</th>
                  <th>規格</th>
                  <th>數量</th>
                  <th>單價</th>
                  <th>總價</th>
                </tr>
              </thead>
              <tbody>
                {quote.line_items.map((item, index) => (
                  <tr key={index} className={item.is_suggestion ? 'suggestion-row' : ''}>
                    <td className="item-name">
                      {item.item_name}
                      {item.is_suggestion && <span className="suggestion-badge">AI 建議</span>}
                    </td>
                    <td className="item-spec">{item.spec}</td>
                    <td className="item-quantity">{item.quantity} {item.unit}</td>
                    <td className="item-unit-price">{formatCurrency(item.unit_price)}</td>
                    <td className="item-total-price">{formatCurrency(item.total_price)}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="total-row">
                  <td colSpan="4">報價總計</td>
                  <td className="total-amount">{formatCurrency(quote.total_price)}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        )}
      </div>

      {/* CTA 按鈕 */}
      <div className="result-actions">
        <button
          className="booking-button"
          onClick={onBookingRequest}
        >
          <span className="button-icon">📞</span>
          預約免費丈量
        </button>
        <button
          className="download-button"
          onClick={() => window.print()}
        >
          <span className="button-icon">📥</span>
          下載報告
        </button>
      </div>
    </div>
  );
};

export default FinalResult;
