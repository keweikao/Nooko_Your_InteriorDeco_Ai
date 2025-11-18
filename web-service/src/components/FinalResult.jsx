import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { User, FileText } from 'lucide-react';
import FeedbackFlow from './FeedbackFlow';
import SpecCard from './results/SpecCard';
import BudgetCard from './results/BudgetCard';
import QuoteTable from './results/QuoteTable';

/**
 * Purpose: Renders the final analysis result in a modern dashboard layout.
 *          This is a presentational component that receives all data via props.
 *          It also orchestrates the display of the FeedbackFlow component.
 *
 * Input (Props):
 *   - analysisResult (Object): Contains all the data for the final report, including
 *     briefing, budget_tradeoffs, and quote.
 *   - projectId (string): The current project ID.
 *   - apiBaseUrl (string): The base URL for API calls.
 *
 * Output:
 *   - A dashboard displaying the complete solution package and the FeedbackFlow.
 */
const FinalResult = ({ analysisResult, projectId, apiBaseUrl }) => {
  const [showFeedbackFlow, setShowFeedbackFlow] = useState(false);

  if (!analysisResult) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="text-center">
          <h2 className="text-2xl font-semibold mb-2">正在生成您的專屬分析結果...</h2>
          <p className="text-muted-foreground">請稍候，AI 正在為您整合最終報告。</p>
        </div>
      </div>
    );
  }

  const { briefing, budget_tradeoffs, quote, summary } = analysisResult;

  return (
    <div className="min-h-screen bg-background text-foreground p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-bold tracking-tight">您的專屬設計方案</h1>
          <p className="text-lg text-muted-foreground mt-2">{summary}</p>
        </header>

        <main className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-6">
            {quote && <QuoteTable quoteData={quote} />}
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {briefing && <SpecCard brief={briefing} />}
            {budget_tradeoffs && <BudgetCard tradeoffs={budget_tradeoffs} />}
            
            {!showFeedbackFlow && (
              <Card>
                <CardHeader>
                  <CardTitle>準備好開始了嗎？</CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col gap-4">
                  <Button size="lg" onClick={() => setShowFeedbackFlow(true)}>
                    <User className="mr-2 h-5 w-5" /> 提供回饋與預約丈量
                  </Button>
                  <Button size="lg" variant="outline" onClick={() => window.print()}>
                    <FileText className="mr-2 h-5 w-5" /> 下載或列印報告
                  </Button>
                </CardContent>
              </Card>
            )}
            
            {showFeedbackFlow && (
              <FeedbackFlow 
                projectId={projectId} 
                apiBaseUrl={apiBaseUrl} 
                onFeedbackSubmitted={() => console.log("Feedback submitted!")}
                onBookingSubmitted={() => console.log("Booking submitted!")}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default FinalResult;
