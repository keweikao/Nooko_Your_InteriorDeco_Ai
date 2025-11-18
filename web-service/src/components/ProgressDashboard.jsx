import React from 'react';

const steps = [
  { id: 'upload', name: '上傳報價單' },
  { id: 'questionnaire', name: '需求深度訪談' },
  { id: 'analysis', name: 'AI 智慧分析' }, // This step is internal, but shown for transparency
    { id: 'booking', name: '預約免費丈量' },
];

const ProgressDashboard = ({ currentStepId }) => {
  return (
    <div className="w-full max-w-4xl mx-auto mb-8 p-4 bg-nooko-white rounded-lg shadow-md">
      <div className="flex justify-between items-center relative">
        {/* Progress Line */}
        <div className="absolute left-0 right-0 h-1 bg-gray-200 top-1/2 -translate-y-1/2 mx-6">
          <div
            className="h-full bg-nooko-terracotta transition-all duration-500 ease-in-out"
            style={{ width: `${(steps.findIndex(step => step.id === currentStepId) / (steps.length - 1)) * 100}%` }}
          ></div>
        </div>

        {steps.map((step, index) => (
          <div key={step.id} className="flex flex-col items-center relative z-10">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300 ease-in-out
                ${index <= steps.findIndex(s => s.id === currentStepId) ? 'bg-nooko-terracotta text-nooko-white' : 'bg-gray-200 text-gray-500'}`}
            >
              {index + 1}
            </div>
            <div
              className={`mt-2 text-center text-xs font-medium transition-colors duration-300 ease-in-out
                ${index <= steps.findIndex(s => s.id === currentStepId) ? 'text-nooko-charcoal' : 'text-gray-500'}`}
            >
              {step.name}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProgressDashboard;
