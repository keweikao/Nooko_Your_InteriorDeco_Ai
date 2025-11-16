import React from 'react';
import '../ConversationUI.css';

/**
 * 對話進度指示器
 * 顯示當前階段和進度百分比
 */
function ConversationProgress({ progress }) {
  const getStageLabel = (stage) => {
    const stages = {
      greeting: '問候',
      assessment: '評估',
      clarification: '澄清',
      summary: '總結',
      complete: '完成'
    };
    return stages[stage] || stage;
  };

  const getStageColor = (stage) => {
    const colors = {
      greeting: 'stage-greeting',
      assessment: 'stage-assessment',
      clarification: 'stage-clarification',
      summary: 'stage-summary',
      complete: 'stage-complete'
    };
    return colors[stage] || 'stage-greeting';
  };

  return (
    <div className="conversation-progress">
      <div className="progress-info">
        <span className={`progress-stage ${getStageColor(progress?.stage)}`}>
          {getStageLabel(progress?.stage)}
        </span>
        <span className="progress-percentage">{progress?.current || 0}%</span>
      </div>

      <div className="progress-bar-container">
        <div
          className="progress-bar"
          style={{ width: `${progress?.current || 0}%` }}
        >
          <div className="progress-shimmer"></div>
        </div>
      </div>

      <p className="progress-description">{progress?.description}</p>
    </div>
  );
}

export default ConversationProgress;
