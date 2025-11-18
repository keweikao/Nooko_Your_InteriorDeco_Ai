import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { CheckCircle, AlertTriangle, DollarSign } from 'lucide-react';

const BudgetCard = ({ tradeoffs }) => (
  <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2"><DollarSign /> 預算取捨建議</CardTitle>
      <CardDescription>{tradeoffs.budget_analysis_summary}</CardDescription>
    </CardHeader>
    <CardContent className="space-y-6">
      <div>
        <h4 className="font-semibold text-lg flex items-center gap-2 mb-2"><AlertTriangle className="text-destructive" /> 不可妥協項目</h4>
        <ul className="space-y-2">
          {tradeoffs.essential_items.map((item, i) => (
            <li key={i} className="p-2 bg-muted/50 rounded-md">
              <p className="font-semibold">{item.item_name}</p>
              <p className="text-sm text-muted-foreground">{item.reason}</p>
            </li>
          ))}
        </ul>
      </div>
      <div>
        <h4 className="font-semibold text-lg flex items-center gap-2 mb-2"><CheckCircle className="text-primary" /> 可妥協項目</h4>
        <ul className="space-y-2">
          {tradeoffs.flexible_items.map((item, i) => (
            <li key={i} className="p-2 bg-muted/50 rounded-md">
              <p className="font-semibold">{item.item_name}</p>
              <p className="text-sm text-muted-foreground mb-2">{item.reason}</p>
              {item.alternatives.map((alt, j) => (
                <div key={j} className="text-xs border-l-2 border-primary pl-2 ml-2">
                  <p><strong>替代方案:</strong> {alt.suggestion}</p>
                  <p><strong>預估節省:</strong> <span className="font-mono text-primary">{alt.estimated_saving}</span></p>
                </div>
              ))}
            </li>
          ))}
        </ul>
      </div>
    </CardContent>
  </Card>
);

export default BudgetCard;
