import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Wrench } from 'lucide-react';

const QuoteTable = ({ quoteData }) => {
  const formatCurrency = (amount) => new Intl.NumberFormat('zh-TW', {
    style: 'currency', currency: 'TWD', minimumFractionDigits: 0
  }).format(amount);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><Wrench /> 詳細規格報價單</CardTitle>
        <CardDescription>根據您的需求和我們的專業分析，為您整理的詳細報價。</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-muted-foreground uppercase bg-muted/50">
              <tr>
                <th className="px-4 py-3">項目</th>
                <th className="px-4 py-3">規格</th>
                <th className="px-4 py-3 text-right">數量</th>
                <th className="px-4 py-3 text-right">單價</th>
                <th className="px-4 py-3 text-right">總價</th>
              </tr>
            </thead>
            <tbody>
              {quoteData.line_items.map((item, index) => (
                <tr key={index} className="border-b">
                  <td className="px-4 py-3 font-medium">{item.item_name}</td>
                  <td className="px-4 py-3 text-muted-foreground">{item.spec}</td>
                  <td className="px-4 py-3 text-right">{item.quantity} {item.unit}</td>
                  <td className="px-4 py-3 text-right font-mono">{formatCurrency(item.unit_price)}</td>
                  <td className="px-4 py-3 text-right font-mono">{formatCurrency(item.total_price)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="font-semibold text-lg">
                <td colSpan="4" className="px-4 py-3 text-right">報價總計</td>
                <td className="px-4 py-3 text-right font-mono">{formatCurrency(quoteData.total_price)}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};

export default QuoteTable;
