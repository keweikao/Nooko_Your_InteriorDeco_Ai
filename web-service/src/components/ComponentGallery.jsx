import { useMemo } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./ui/card";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Badge } from "./ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "./ui/accordion";
import { SpotlightCard } from "./magicui/SpotlightCard";
import { MagicButton } from "./magicui/MagicButton";
import { AuroraBackground } from "./magicui/AuroraBackground";
import { BentoGrid, BentoCard } from "./magicui/BentoGrid";
import { RetroButton } from "./retro/RetroButton";
import { RetroCard } from "./retro/RetroCard";

const accordionItems = [
  {
    id: "item-1",
    question: "為什麼選擇 shadcn/ui？",
    answer: "使用 Tailwind CSS 搭配 headless Radix 元件，帶來一致且易於客製化的設計語言。"
  },
  {
    id: "item-2",
    question: "MagicUI 可以用在哪裡？",
    answer: "適合用於 hero banners、背景動效、互動式行銷內容，讓體驗更有科技感。"
  },
  {
    id: "item-3",
    question: "Retro UI 風格怎麼搭配？",
    answer: "Neo-brutalism 肯定能凸顯 CTA 或特別活動，吸引用戶目光。"
  }
];

export function ComponentGallery() {
  const magicCards = useMemo(
    () => [
      {
        title: "AI 空間分析",
        description: "分析格局、動線以及自然採光，提供最合適的配置建議。",
        footer: "MagicUI Bento",
        children: <p className="text-sm text-slate-200">支援 2D / 3D 平面圖，並能疊加預算估算。</p>
      },
      {
        title: "靈感拼貼",
        description: "快速建立靈感板，整合風格、材質與軟裝方案。",
        footer: "MagicUI Bento",
        children: <MagicButton>探索靈感</MagicButton>
      },
      {
        title: "瑕疵檢視",
        description: "整合現場拍照紀錄，協助統包商追蹤修復事項。",
        footer: "MagicUI Bento",
        children: <p className="text-sm text-slate-200">結合行事曆，提供通知與簽核流程。</p>
      }
    ],
    []
  );

  return (
    <div className="space-y-12">
      <section className="space-y-4">
        <div>
          <Badge variant="secondary">shadcn/ui</Badge>
          <h2 className="mt-2 text-2xl font-semibold">表單與資訊卡</h2>
          <p className="text-muted-foreground">將專案流程的輸入、說明、FAQ 改用 shadcn/ui，維持一致的 UI token。</p>
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>預約丈量</CardTitle>
              <CardDescription>整合 shadcn 的 Button / Input / Textarea</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input placeholder="姓名" />
              <div className="grid gap-3 md:grid-cols-2">
                <Input placeholder="聯絡電話" />
                <Input placeholder="Email" />
              </div>
              <Textarea placeholder="想補充的需求" />
            </CardContent>
            <CardFooter className="flex justify-between">
              <Badge>專案 ID #A12</Badge>
              <Button>送出預約</Button>
            </CardFooter>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>常見問題</CardTitle>
              <CardDescription>Accordion 搭配 tailwind-animate</CardDescription>
            </CardHeader>
            <CardContent>
              <Accordion type="single" collapsible className="w-full">
                {accordionItems.map((item) => (
                  <AccordionItem key={item.id} value={item.id}>
                    <AccordionTrigger>{item.question}</AccordionTrigger>
                    <AccordionContent>{item.answer}</AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </CardContent>
          </Card>
        </div>
      </section>

      <section className="space-y-4">
        <div>
          <Badge variant="secondary">MagicUI</Badge>
          <h2 className="mt-2 text-2xl font-semibold">互動式行銷素材</h2>
          <p className="text-muted-foreground">帶有 Spotlight、Aurora、Bento grid 等特效的組件，可用於 hero 區或 AB 測試。</p>
        </div>
        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <AuroraBackground className="min-h-full">
            <div className="flex flex-wrap items-center gap-3 text-sm uppercase tracking-[0.35em] text-slate-200">
              <span>Smart Budget</span>
              <span className="h-px w-10 bg-slate-400/50" />
              <span>Style Companion</span>
            </div>
            <h3 className="text-3xl font-semibold leading-tight">讓 AI 成為你的室內設計夥伴</h3>
            <p className="text-base text-slate-300">
              MagicUI Aurora 背景讓 CTA 更突出，同時保持高階感。可以套用在首頁 hero 或對話式 landing page。
            </p>
            <div className="flex flex-wrap gap-3 pt-4">
              <MagicButton>立即體驗</MagicButton>
              <MagicButton className="from-slate-800 via-slate-800 to-slate-800 border-white/10">
                下載方案
              </MagicButton>
            </div>
          </AuroraBackground>
          <div className="space-y-4">
            <SpotlightCard title="AI 報價解析" description="自動解析 PDF / 圖片報價，標記缺漏項目。" icon="✨">
              不論是泥作、水電或軟裝，都能快速比對單價，讓使用者掌握市場行情。
            </SpotlightCard>
            <SpotlightCard title="智能追蹤" description="MagicUI Spotlight" icon="🛰️">
              任務完成後觸發自動更新、Slack 通知與版本紀錄。
            </SpotlightCard>
          </div>
        </div>
        <BentoGrid className="mt-4">
          {magicCards.map((card) => (
            <BentoCard key={card.title} {...card} />
          ))}
        </BentoGrid>
      </section>

      <section className="space-y-4">
        <div>
          <Badge variant="secondary">Retro UI</Badge>
          <h2 className="mt-2 text-2xl font-semibold">Neo-Brutalism CTA</h2>
          <p className="text-muted-foreground">對於活動頁或新功能介紹，可以用 Retro UI 的 Button/Card 讓資訊更醒目。</p>
        </div>
        <div className="grid gap-4 lg:grid-cols-[1fr_0.6fr]">
          <RetroCard title="限時免費丈量" description="Retro UI 卡片適合拿來呈現強烈主張或活動資訊。">
            <ul className="list-disc space-y-2 pl-5">
              <li>0 元丈量，7 天內提供設計概念。</li>
              <li>不限坪數，提供三種風格參考。</li>
              <li>與 shadcn 表單完美搭配，建立立即行動的 CTA。</li>
            </ul>
          </RetroCard>
          <div className="flex flex-col items-center justify-center gap-4 rounded-3xl border-4 border-black bg-[#D9F99D] p-6 text-center shadow-[8px_8px_0_0_#000]">
            <p className="text-xl font-black uppercase tracking-widest text-black">Retro Button</p>
            <RetroButton>立即預約</RetroButton>
            <p className="text-sm font-semibold text-slate-800">具體又大膽的線條，很適合作為 Landing Page 的第二 CTA。</p>
          </div>
        </div>
      </section>
    </div>
  );
}
