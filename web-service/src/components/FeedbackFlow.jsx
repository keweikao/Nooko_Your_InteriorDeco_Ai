import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Star, CheckCircle, Phone, User, MapPin } from 'lucide-react';

/**
 * Purpose: A multi-step feedback and booking component for the final results page.
 *          It guides the user through satisfaction ratings and optional measurement booking.
 *
 * Input (Props):
 *   - projectId (string): The current project ID.
 *   - apiBaseUrl (string): The base URL for API calls.
 *   - onFeedbackSubmitted (function): Callback after feedback is submitted.
 *   - onBookingSubmitted (function): Callback after booking is submitted.
 *
 * Output:
 *   - Interactive UI for collecting user feedback and booking requests.
 */
const FeedbackFlow = ({ projectId, apiBaseUrl, onFeedbackSubmitted, onBookingSubmitted }) => {
  const [step, setStep] = useState(1); // 1: satisfaction, 2: helpfulness, 3: measurement, 4: booking form, 5: thank you
  const [satisfactionScore, setSatisfactionScore] = useState(0);
  const [helpfulnessScore, setHelpfulnessScore] = useState(0);
  const [wantsMeasurement, setWantsMeasurement] = useState(null); // true/false
  const [bookingName, setBookingName] = useState('');
  const [bookingPhone, setBookingPhone] = useState('');
  const [bookingRegion, setBookingRegion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [bookingSubmitted, setBookingSubmitted] = useState(false);

  const regions = ['基隆', '台北市', '新北市', '桃園'];

  const handleScoreSubmit = async (scoreType, score) => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        satisfaction_score: scoreType === 'satisfaction' ? score : satisfactionScore,
        helpfulness_score: scoreType === 'helpfulness' ? score : helpfulnessScore,
      };
      
      const response = await fetch(`${apiBaseUrl}/projects/${projectId}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Failed to submit feedback');
      }
      
      if (scoreType === 'satisfaction') {
        setSatisfactionScore(score);
        setStep(2); // Move to helpfulness question
      } else if (scoreType === 'helpfulness') {
        setHelpfulnessScore(score);
        setFeedbackSubmitted(true);
        setStep(3); // Move to measurement question
      }
      onFeedbackSubmitted && onFeedbackSubmitted();
    } catch (err) {
      setError('提交回饋失敗，請稍後再試。');
      console.error('Feedback submission error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBookingSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        name: bookingName,
        phone: bookingPhone,
        region: bookingRegion,
      };

      const response = await fetch(`${apiBaseUrl}/projects/${projectId}/book`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Failed to submit booking');
      }

      setBookingSubmitted(true);
      setStep(5); // Move to thank you
      onBookingSubmitted && onBookingSubmitted();
    } catch (err) {
      setError('提交預約失敗，請稍後再試。');
      console.error('Booking submission error:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderStarRating = (currentScore, setScore, scoreType) => (
    <div className="flex space-x-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <Star
          key={star}
          className={`cursor-pointer ${star <= currentScore ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`}
          onClick={() => handleScoreSubmit(scoreType, star)}
          size={32}
        />
      ))}
    </div>
  );

  return (
    <Card className="w-full max-w-md mx-auto mt-8">
      <CardHeader>
        <CardTitle>
          {step === 1 && "您對本次互動滿意嗎？"}
          {step === 2 && "您覺得規格書內容有幫助嗎？"}
          {step === 3 && "希望我們安排免費現場丈量嗎？"}
          {step === 4 && "請留下您的聯絡資訊"}
          {step === 5 && "感謝您的回饋！"}
        </CardTitle>
        <CardDescription>
          {step === 1 && "您的回饋是我們進步的動力！"}
          {step === 2 && "這有助於我們優化內容呈現。"}
          {step === 3 && "我們的專業團隊將為您提供更精準的服務。"}
          {step === 4 && "我們將盡快與您聯繫。"}
          {step === 5 && "我們已收到您的回饋與預約請求。"}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && <p className="text-destructive text-center">{error}</p>}
        {loading && <p className="text-center text-muted-foreground">處理中...</p>}

        {step === 1 && (
          <div className="flex justify-center">
            {renderStarRating(satisfactionScore, setSatisfactionScore, 'satisfaction')}
          </div>
        )}

        {step === 2 && (
          <div className="flex justify-center">
            {renderStarRating(helpfulnessScore, setHelpfulnessScore, 'helpfulness')}
          </div>
        )}

        {step === 3 && (
          <div className="flex flex-col space-y-4">
            <Button onClick={() => { setWantsMeasurement(true); setStep(4); }} size="lg">
              <CheckCircle className="mr-2 h-5 w-5" /> 麻煩安排
            </Button>
            <Button onClick={() => { setWantsMeasurement(false); setStep(5); }} variant="outline" size="lg">
              不需要，謝謝
            </Button>
          </div>
        )}

        {step === 4 && (
          <form onSubmit={(e) => { e.preventDefault(); handleBookingSubmit(); }} className="space-y-4">
            <div className="grid w-full items-center gap-1.5">
              <Label htmlFor="bookingName">聯絡名稱</Label>
              <Input
                id="bookingName"
                type="text"
                placeholder="您的姓名"
                value={bookingName}
                onChange={(e) => setBookingName(e.target.value)}
                required
              />
            </div>
            <div className="grid w-full items-center gap-1.5">
              <Label htmlFor="bookingPhone">聯絡電話</Label>
              <Input
                id="bookingPhone"
                type="tel"
                placeholder="您的電話號碼"
                value={bookingPhone}
                onChange={(e) => setBookingPhone(e.target.value)}
                required
              />
            </div>
            <div className="grid w-full items-center gap-1.5">
              <Label htmlFor="bookingRegion">選擇地區</Label>
              <Select value={bookingRegion} onValueChange={setBookingRegion} required>
                <SelectTrigger id="bookingRegion">
                  <SelectValue placeholder="請選擇地區" />
                </SelectTrigger>
                <SelectContent>
                  {regions.map((region) => (
                    <SelectItem key={region} value={region}>{region}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "提交中..." : "確認預約"}
            </Button>
          </form>
        )}

        {step === 5 && (
          <div className="text-center space-y-2">
            <CheckCircle className="h-12 w-12 text-primary mx-auto" />
            <p className="text-lg font-semibold">
              {wantsMeasurement ? "我們已收到您的預約請求！" : "感謝您的回饋！"}
            </p>
            <p className="text-muted-foreground">
              {wantsMeasurement ? "我們的專員將盡快與您聯繫，確認丈量細節。" : "您的意見對我們非常重要。"}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default FeedbackFlow;