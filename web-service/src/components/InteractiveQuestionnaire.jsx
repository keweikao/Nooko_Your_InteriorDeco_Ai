import React, { useState, useEffect } from 'react';
// import './InteractiveQuestionnaire.css'; // Removed custom CSS import

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
      const response = await fetch(`${apiBaseUrl}/projects/${projectId}/conversation/start`, {
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

      setCurrentQuestion({ ...data.question, agent_name: data.agent_name });
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
      const response = await fetch(`${apiBaseUrl}/projects/${projectId}/conversation/answer`, {
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

      if (data.is_complete) {
        // Interview complete
        setCompleted(true);
        setSummary(data.message);
        setProgress(100);

        if (onComplete) {
          onComplete(data.project_brief);
        }
      } else {
        // Next question
        setCurrentQuestion({ ...data.next_question, agent_name: data.agent_name });
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

  const getAgentInitial = (name) => {
    return name ? name.charAt(0).toUpperCase() : 'AI';
  };

  if (completed) {
    return (
      <div className="flex flex-col items-center justify-center p-6 bg-nooko-white rounded-lg shadow-lg text-nooko-charcoal">
        <div className="flex flex-col items-center justify-center p-8 bg-nooko-white rounded-lg shadow-xl max-w-md w-full text-center">
          <div className="text-6xl text-nooko-terracotta mb-4">✓</div>
          <h2 className="text-3xl font-playfair font-bold mb-4">需求訪談完成！</h2>
          <div className="text-base text-gray-700 leading-relaxed mb-6">
            {summary.split('\n').map((line, index) => (
              <p key={index}>{line}</p>
            ))}
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
            <div className="bg-nooko-terracotta h-2.5 rounded-full" style={{ width: '100%' }}></div>
          </div>
          <span className="text-sm text-gray-500 mb-6">100% 完成</span>
          <p className="text-base text-gray-700">
            我們的專業團隊正在為您準備詳細的報價單與設計圖...
          </p>
        </div>
      </div>
    );
  }

  if (loading && !currentQuestion) {
    return (
      <div className="flex flex-col items-center justify-center p-6 bg-nooko-white rounded-lg shadow-lg text-nooko-charcoal min-h-[300px]">
        <svg className="animate-spin h-10 w-10 text-nooko-terracotta" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p className="mt-4 text-lg">正在準備問題...</p>
      </div>
    );
  }

  if (error && !currentQuestion) {
    return (
      <div className="flex flex-col items-center justify-center p-6 bg-nooko-white rounded-lg shadow-lg text-nooko-charcoal min-h-[300px]">
        <p className="text-red-500 text-lg mb-4">⚠️ {error}</p>
        <button
          onClick={startConversation}
          className="px-4 py-2 bg-nooko-terracotta text-nooko-white rounded-lg hover:bg-nooko-terracotta/90 transition-colors"
        >
          重試
        </button>
      </div>
    );
  }

  if (!currentQuestion) {
    return null;
  }

  return (
    <div className="flex flex-col bg-nooko-white rounded-lg shadow-lg p-6 text-nooko-charcoal max-w-2xl mx-auto">
      {/* Progress Section */}
      <div className="w-full mb-6">
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div className="bg-nooko-terracotta h-2.5 rounded-full" style={{ width: `${progress}%` }}></div>
        </div>
        <span className="text-sm text-gray-500 mt-2 block text-right">{progress}% 完成</span>
      </div>

      {/* Agent Persona */}
      <div className="flex items-center mb-4">
        <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center text-nooko-charcoal font-bold text-lg mr-3">
          {getAgentInitial(currentQuestion.agent_name)}
        </div>
        <span className="font-semibold text-lg">{currentQuestion.agent_name} (您的專屬裝潢顧問)</span>
      </div>

      {/* Question Card */}
      <div className="bg-gray-50 p-5 rounded-lg mb-6 border border-gray-200">
        <div className="mb-3">
          <span className="bg-nooko-terracotta/10 text-nooko-terracotta text-xs font-semibold px-3 py-1 rounded-full">
            {currentQuestion.category}
          </span>
        </div>

        <div className="mb-4">
          <h3 className="text-xl font-playfair font-bold leading-relaxed">{currentQuestion.text}</h3>

          {currentQuestion.empathy_message && (
            <div className="flex items-center mt-3 text-gray-600 text-sm">
              <span className="mr-2">💬</span>
              <span>{currentQuestion.empathy_message}</span>
            </div>
          )}

          {currentQuestion.info_purpose && (
            <div className="flex items-center mt-3 text-gray-600 text-sm">
              <span className="mr-2">ℹ️</span>
              <span>{currentQuestion.info_purpose}</span>
            </div>
          )}

          {currentQuestion.can_skip && currentQuestion.skip_suggestion && (
            <div className="flex items-center mt-3 text-gray-600 text-sm">
              <span className="mr-2">✨</span>
              <span>{currentQuestion.skip_suggestion}</span>
            </div>
          )}
        </div>

        {/* Answer Section */}
        <div className="flex flex-col space-y-3">
          {currentQuestion.options && currentQuestion.options.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {currentQuestion.options.map((option, index) => (
                <button
                  key={index}
                  className={`px-4 py-2 border rounded-lg text-left transition-all duration-200
                    ${answer === option ? 'bg-nooko-terracotta text-nooko-white border-nooko-terracotta' : 'bg-nooko-white text-nooko-charcoal border-gray-300 hover:bg-gray-100'}`}
                  onClick={() => handleOptionSelect(option)}
                  disabled={loading}
                >
                  {option}
                </button>
              ))}
            </div>
          ) : (
            <textarea
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nooko-terracotta focus:border-transparent outline-none transition-all duration-200"
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
            <div className="mt-2">
              <input
                type="text"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nooko-terracotta focus:border-transparent outline-none transition-all duration-200"
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
          <div className="mt-4 text-center text-sm text-red-500">
            <p>⚠️ {error}</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 mt-6">
          {currentQuestion.can_skip && (
            <button
              className="px-5 py-2 border border-gray-300 text-nooko-charcoal rounded-lg hover:bg-gray-100 transition-colors"
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
            className={`px-5 py-2 rounded-lg font-bold text-nooko-white transition-all duration-300 ease-in-out
              ${loading || !answer.trim() ? 'bg-gray-400 cursor-not-allowed' : 'bg-nooko-terracotta hover:bg-nooko-terracotta/90 shadow-md'}`}
            onClick={submitAnswer}
            disabled={loading || !answer.trim()}
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                處理中...
              </span>
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
