import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { FileText } from 'lucide-react';

const SpecCard = ({ brief }) => (
  <Card className="w-full">
    <CardHeader>
      <CardTitle className="flex items-center gap-2"><FileText /> 專案規格書</CardTitle>
      <CardDescription>{brief.project_id}</CardDescription>
    </CardHeader>
    <CardContent>
      <div className="space-y-4">
        <div>
          <h4 className="font-semibold text-md mb-2">客戶資訊</h4>
          <ul className="list-disc list-inside text-muted-foreground space-y-1">
            {Object.entries(brief.user_profile).map(([key, value]) =>
              value && <li key={key}><strong>{key}:</strong> {Array.isArray(value) ? value.join(', ') : value}</li>
            )}
          </ul>
        </div>
        <div>
          <h4 className="font-semibold text-md mb-2">關鍵需求</h4>
          <ul className="list-disc list-inside text-muted-foreground space-y-1">
            {brief.key_requirements.map((req, i) => <li key={i}>{req}</li>)}
          </ul>
        </div>
        <div>
          <h4 className="font-semibold text-md mb-2">偏好風格</h4>
          <div className="flex flex-wrap gap-2">
            {brief.style_preferences.map((style, i) =>
              <span key={i} className="px-3 py-1 bg-secondary text-secondary-foreground rounded-full text-sm">{style}</span>
            )}
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
);

export default SpecCard;
