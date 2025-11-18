import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload';
import InteractiveQuestionnaire from './components/InteractiveQuestionnaire';
import ConversationUI from './components/ConversationUI';
import FinalResult from './components/FinalResult';
import BookingForm from './components/BookingForm';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Button as UiButton } from './components/ui/button';
import { ComponentGallery } from './components/ComponentGallery';
import StyleGuide from './components/StyleGuide'; // Import StyleGuide component
import ProgressDashboard from './components/ProgressDashboard'; // Import ProgressDashboard


function App() {
  const [apiBaseUrl, setApiBaseUrl] = useState('');
  const [projectId, setProjectId] = useState(null);
  const [currentStep, setCurrentStep] = useState('welcome'); // welcome, upload, questionnaire, analysis, results, booking
  const [welcomeMessage, setWelcomeMessage] = useState('');
  const [projectBrief, setProjectBrief] = useState(null);

  useEffect(() => {
    // Set the API base URL - use environment variable or default to local development
    const baseUrl = import.meta.env.VITE_APP_API_BASE_URL || 'http://localhost:8000';
    setApiBaseUrl(baseUrl);

    // Create a new project when the component mounts
    createNewProject(baseUrl);
  }, []);

  const createNewProject = async (baseUrl) => {
    try {
      const response = await fetch(`${baseUrl}/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      setProjectId(data.project_id);
      setWelcomeMessage(data.welcome_message || '歡迎來到 HouseIQ 裝潢 AI 夥伴！');
    } catch (error) {
      console.error('Error creating project:', error);
      setWelcomeMessage('抱歉，無法建立專案。請重新整理頁面再試一次。');
    }
  };

  const handleFileUploaded = () => {
    // Move to questionnaire step after file upload
    setCurrentStep('questionnaire');
  };

  const handleQuestionnaireComplete = (brief) => {
    setProjectBrief(brief);
    // Trigger Agent1 (Contractor Agent) to start processing
    triggerAgent1(brief);

    // Move to analysis step after questionnaire completes
    setCurrentStep('analysis');

    // Simulate analysis time, then move to results
    setTimeout(() => {
      setCurrentStep('results');
    }, 5000); // Simulate 5 seconds of analysis
  };

  const triggerAgent1 = async (brief) => {
    try {
      // Trigger the contractor agent (Agent1) to analyze the project brief
      const response = await fetch(`${apiBaseUrl}/projects/${projectId}/trigger-agent-1`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_brief: brief,
          timestamp: new Date().toISOString(),
        }),
      });

      if (!response.ok) {
        console.error('Failed to trigger Agent1:', response.statusText);
      }
    } catch (error) {
      console.error('Error triggering Agent1:', error);
    }
  };

  const handleBookingRequest = () => {
    setCurrentStep('booking');
  };

  const handleBookingComplete = () => {
    alert('預約成功！我們會盡快與您聯繫。');
  };

  const isShowcaseEnabled = import.meta.env.VITE_ENABLE_UI_SHOWCASE === 'true';

  const flowContent = (
    <>
      {currentStep === 'welcome' && (
        <div className="flex justify-center py-8">
          <div className="w-full max-w-2xl bg-card p-8 rounded-lg shadow-lg border border-border">
            <h2 className="text-3xl font-bold text-center mb-6 text-primary">{welcomeMessage}</h2>
            <p className="text-lg text-center mb-8 text-muted-foreground">
              我們了解裝潢是一項重大投資，但資訊不對稱往往讓您無所適從。
              HouseIQ 運用 AI 技術，幫助您：
            </p>
            <ul className="list-disc list-inside space-y-2 mb-8 text-foreground">
              <li>✓ 分析現有報價單，找出可能遺漏的項目</li>
              <li>✓ 深入了解您的需求，提供客製化建議</li>
              <li>✓ 產出詳細的規格報價單，建立資訊透明度</li>
              <li>✓ 提供專業設計概念圖</li>
            </ul>
            <div className="text-center">
              <UiButton
                className="px-8 py-3 text-lg"
                onClick={() => setCurrentStep('upload')}
                disabled={!projectId}
              >
                開始使用 →
              </UiButton>
            </div>
            {projectId && (
              <p className="text-sm text-center text-muted-foreground mt-4">專案 ID: {projectId}</p>
            )}
          </div>
        </div>
      )}

      {currentStep === 'upload' && (
        <div className="flex justify-center py-8">
          <div className="w-full max-w-2xl bg-card p-8 rounded-lg shadow-lg border border-border">
            <div className="text-sm text-primary mb-2">步驟 1/3</div>
            <h2 className="text-2xl font-bold mb-4 text-primary">上傳您的報價單</h2>
            <p className="text-muted-foreground mb-6">
              請上傳您目前掌握的報價單（支援 PDF、Excel 或圖片格式）。
              如果還沒有報價單，也可以直接進入需求訪談。
            </p>
            {projectId && (
              <>
                <FileUpload
                  projectId={projectId}
                  apiBaseUrl={apiBaseUrl}
                  onUploadSuccess={handleFileUploaded}
                />
                <div className="text-center mt-6">
                  <UiButton
                    variant="link"
                    onClick={() => setCurrentStep('questionnaire')}
                  >
                    跳過上傳，直接進入需求訪談 →
                  </UiButton>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {currentStep === 'questionnaire' && (
        <div className="flex justify-center py-8">
          <div className="w-full max-w-2xl bg-card p-8 rounded-lg shadow-lg border border-border min-h-[600px]">
            {projectId && (
              <ConversationUI
                projectId={projectId}
                apiBaseUrl={apiBaseUrl}
                onConversationComplete={(result) => {
                  setProjectBrief({}); // Clear projectBrief for new flow
                  setCurrentStep('results');
                }}
              />
            )}
          </div>
        </div>
      )}


      {currentStep === 'results' && (
        <div className="flex justify-center py-8">
          <div className="w-full max-w-2xl bg-card p-8 rounded-lg shadow-lg border border-border">
            <div className="text-sm text-primary mb-2">步驟 3/3</div>
            <h2 className="text-2xl font-bold mb-4 text-primary">專業分析結果</h2>
            <p className="text-muted-foreground mb-6">
              我們的專業團隊已為您準備好詳細的分析報告
            </p>
            {projectId && (
              <FinalResult
                projectId={projectId}
                apiBaseUrl={apiBaseUrl}
                projectBrief={projectBrief}
                onBookingRequest={handleBookingRequest}
              />
            )}
          </div>
        </div>
      )}

      {currentStep === 'booking' && (
        <div className="flex justify-center py-8">
          <div className="w-full max-w-2xl bg-card p-8 rounded-lg shadow-lg border border-border">
            <h2 className="text-2xl font-bold mb-4 text-primary">預約免費丈量</h2>
            <p className="text-muted-foreground mb-6">
              請留下您的聯絡資訊，我們的專業團隊將盡快與您聯繫
            </p>
            {projectId && (
              <BookingForm
                projectId={projectId}
                apiBaseUrl={apiBaseUrl}
                onBookingComplete={handleBookingComplete}
              />
            )}
          </div>
        </div>
      )}
    </>
  );

  return (
    <div className="min-h-screen bg-background text-foreground font-sans antialiased flex flex-col">
      <header className="bg-card border-b border-border py-4 shadow-sm">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-primary">🏠 HouseIQ 裝潢 AI 夥伴</h1>
          <p className="text-sm text-muted-foreground hidden md:block">透明報價 • 專業建議 • 讓裝潢不再是資訊不對稱的遊戲</p>
          {isShowcaseEnabled && (
            <div className="flex items-center space-x-4">
              <UiButton variant="ghost" onClick={() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })}>
                查看 UI Showcase
              </UiButton>
            </div>
          )}
        </div>
      </header>

      <main className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {isShowcaseEnabled ? (
          <Tabs defaultValue="flow" className="w-full space-y-6">
            <TabsList className="mx-auto grid w-full max-w-md grid-cols-3">
              <TabsTrigger value="flow">互動流程</TabsTrigger>
              <TabsTrigger value="gallery">UI 組件展示</TabsTrigger>
              <TabsTrigger value="styleguide">Style Guide</TabsTrigger>
            </TabsList>
            <TabsContent value="flow">
              {currentStep !== 'welcome' && <ProgressDashboard currentStepId={currentStep} />}
              {flowContent}
            </TabsContent>
            <TabsContent value="gallery">
              <ComponentGallery />
            </TabsContent>
            <TabsContent value="styleguide">
              <StyleGuide />
            </TabsContent>
          </Tabs>
        ) : (
          <>
            {currentStep !== 'welcome' && <ProgressDashboard currentStepId={currentStep} />}
            {flowContent}
          </>
        )}
      </main>

      <footer className="bg-card border-t border-border py-4 text-center text-sm text-muted-foreground">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <p>© 2024 HouseIQ 裝潢 AI 夥伴 | 讓裝潢資訊透明化</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
