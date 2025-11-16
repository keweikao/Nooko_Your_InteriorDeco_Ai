import React, { useState, useEffect } from 'react';
import './InteractiveQuestionnaire.css';

const InteractiveQuestionnaire = ({ projectId, apiBaseUrl, onComplete }) => {
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationStarted, setConversationStarted] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [summary, setSummary] = useState('');

  useEffect(() => {
    if (projectId && !conversationStarted) {
      startConversation();
    }
  }, [projectId]);

  const startConversation = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/api/projects/${projectId}/conversation/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (data.error) {
        setError(data.error);
        return;
      }

      setCurrentQuestion(data.question);
      setProgress(data.progress);
      setConversationStarted(true);
    } catch (err) {
      setError('無法啟動對話流程：' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!answer.trim()) {
      setError('請提供您的回答');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/api/projects/${projectId}/conversation/answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question_id: currentQuestion.id,
          answer: answer,
        }),
      });

      const data = await response.json();

      if (data.error) {
        setError(data.error);
        return;
      }

      if (data.completed) {
        // Interview complete
        setCompleted(true);
        setSummary(data.summary);
        setProgress(100);

        if (onComplete) {
          onComplete(data.project_brief);
        }
      } else {
        // Next question
        setCurrentQuestion(data.question);
        setProgress(data.progress);
        setAnswer(''); // Reset answer for next question

        // Check if we should show style images
        if (data.generate_images) {
          // TODO: Integrate with image generation service
          console.log('Generating style images for:', data.style_preference);
        }
      }
    } catch (err) {
      setError('提交答案時發生錯誤：' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOptionSelect = (option) => {
    setAnswer(option);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !loading) {
      submitAnswer();
    }
  };

  if (completed) {
    return (
      <div className="questionnaire-container completed">
        <div className="completion-card">
          <div className="completion-icon">✓</div>
          <h2>需求訪談完成！</h2>
          <div className="summary-content">
            {summary.split('\n').map((line, index) => (
              <p key={index}>{line}</p>
            ))}
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: '100%' }}></div>
            <span className="progress-text">100% 完成</span>
          </div>
          <p className="next-steps">
            我們的專業團隊正在為您準備詳細的報價單與設計圖...
          </p>
        </div>
      </div>
    );
  }

  if (loading && !currentQuestion) {
    return (
      <div className="questionnaire-container loading">
        <div className="loading-spinner"></div>
        <p>正在準備問題...</p>
      </div>
    );
  }

  if (error && !currentQuestion) {
    return (
      <div className="questionnaire-container error">
        <div className="error-message">
          <p>⚠️ {error}</p>
          <button onClick={startConversation}>重試</button>
        </div>
      </div>
    );
  }

  if (!currentQuestion) {
    return null;
  }

  return (
    <div className="questionnaire-container">
      <div className="progress-section">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }}></div>
          <span className="progress-text">{progress}% 完成</span>
        </div>
      </div>

      <div className="question-card">
        <div className="question-category">
          <span className="category-badge">{currentQuestion.category}</span>
        </div>

        <div className="question-content">
          <h3>{currentQuestion.text}</h3>

          {currentQuestion.empathy_message && (
            <div className="empathy-message">
              <span className="empathy-icon">💬</span>
              <span>{currentQuestion.empathy_message}</span>
            </div>
          )}

          {currentQuestion.info_purpose && (
            <div className="info-purpose">
              <span className="info-icon">ℹ️</span>
              <span>{currentQuestion.info_purpose}</span>
            </div>
          )}

          {currentQuestion.can_skip && currentQuestion.skip_suggestion && (
            <div className="skip-suggestion">
              <span className="skip-icon">✨</span>
              <span>{currentQuestion.skip_suggestion}</span>
            </div>
          )}
        </div>

        <div className="answer-section">
          {currentQuestion.options && currentQuestion.options.length > 0 ? (
            <div className="options-grid">
              {currentQuestion.options.map((option, index) => (
                <button
                  key={index}
                  className={`option-button ${answer === option ? 'selected' : ''}`}
                  onClick={() => handleOptionSelect(option)}
                  disabled={loading}
                >
                  {option}
                </button>
              ))}
            </div>
          ) : (
            <textarea
              className="answer-input"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="請輸入您的回答..."
              disabled={loading}
              rows={4}
            />
          )}

          {/* Always show text input for additional comments */}
          {currentQuestion.options && currentQuestion.options.length > 0 && (
            <div className="additional-input">
              <input
                type="text"
                className="additional-text-input"
                value={!currentQuestion.options.includes(answer) ? answer : ''}
                onChange={(e) => setAnswer(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="其他說明或補充..."
                disabled={loading}
              />
            </div>
          )}
        </div>

        {error && (
          <div className="error-message inline">
            <p>⚠️ {error}</p>
          </div>
        )}

        <div className="action-buttons">
          {currentQuestion.can_skip && (
            <button
              className="skip-button"
              onClick={() => {
                setAnswer('稍後由設計師現場確認');
                setTimeout(submitAnswer, 100);
              }}
              disabled={loading}
            >
              稍後再決定
            </button>
          )}
          <button
            className="submit-button"
            onClick={submitAnswer}
            disabled={loading || !answer.trim()}
          >
            {loading ? (
              <>
                <span className="loading-spinner small"></span>
                處理中...
              </>
            ) : (
              '下一步 →'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default InteractiveQuestionnaire;
