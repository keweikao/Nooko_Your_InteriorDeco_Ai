# Implementation Plan: AI 裝潢顧問 (AI Decor Advisor)

**Branch**: `003-ai-decor-advisor` | **Date**: 2025-11-17 | **Spec**: `specs/002-interior-deco-ai/spec.md`
**Input**: Refined product vision from user discussion.

## Summary

本專案旨在開發一個「AI 裝潢顧問」，為已有報價單但充滿疑慮的屋主提供專業、中立的第二意見。此 AI 將分析使用者上傳的報價單，透過流暢的深度對話補全個人化需求，並即時產出三大核心價值：一份不含價格的標準化「工程規格書」、一份「預算取捨建議」、以及一張「概念渲染圖」。

此產品的核心目標是透過提供具體價值和建立信任，最終引導使用者選擇我們的施工服務，並以 AI 產出的規格書作為合作基礎，有效提升轉換率。

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, Google GenAI SDK (for Gemini), Firestore Client
**Storage**: Firestore (for user conversations, specs, and generated assets)
**Testing**: pytest
**Target Platform**: Google Cloud Run (as a containerized web service)
**Project Type**: Web Service (Backend + Frontend)
**Performance Goals**: 對話回應時間 < 2 秒，分析與產出流程在 60 秒內完成。
**Constraints**: 需處理多種格式不一的報價單，確保 AI 回覆的專業性與準確性。

## Constitution Check

*此階段暫無違反憲法原則。*

## Project Structure

### Documentation

```text
specs/002-interior-deco-ai/
├── plan.md              # 本文件 (已更新)
├── spec.md              # 功能規格 (下一步討論)
└── tasks.md             # 開發任務清單 (待更新)
```

### Source Code (repository root)

```text
# 後端服務 (單一 AI 核心)
analysis-service/
├── src/
│   ├── services/
│   │   ├── gemini_service.py    # 核心：整合對話、分析、人格模擬
│   │   ├── image_service.py     # 處理與圖片生成模型的互動
│   │   ├── conversation_service.py # 對話與資料庫狀態管理
│   │   └── quote_parser.py      # (可選) 用於解析複雜的報價單檔案
│   ├── models/              # Pydantic 資料模型
│   └── api/                 # API endpoints
└── tests/

# 前端介面
web-service/
├── src/
│   ├── components/
│   └── ...
```

**Structure Decision**: 採用前後端分離架構。後端將採用「**單一 AI 核心，多重專家人格**」模式，由 `gemini_service` 統一處理與大型語言模型的互動，並根據需要模擬不同專家（如統包、設計師）的思維模式。這種架構簡化了後端複雜性，避免了多 Agent 間的通訊與狀態同步問題，更能確保使用者獲得流暢、即時、無中斷的對話體驗，符合產品的「顧問」定位。

## Complexity Tracking

> 本專案目前無須填寫。