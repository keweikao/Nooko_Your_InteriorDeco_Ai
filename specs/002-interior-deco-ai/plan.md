# Implementation Plan: 裝潢 AI 夥伴 (Interior Decoration AI Partner)

**Branch**: `002-interior-deco-ai` | **Date**: 2025-11-14 | **Spec**: `specs/002-interior-deco-ai/spec.md`
**Input**: Feature specification from user prompt.

## Summary

本專案旨在開發一個「裝潢 AI 夥伴」，以解決消費者在裝潢時面臨的資訊不對稱問題。此 AI Agent 將分析使用者提供的報價單（PDF 或 Excel），透過互動式問答了解其詳細需求，最終生成一份包含完整規格、指出潛在缺失項目與風險的標準化報價單。此舉旨在建立資訊透明度，並引導潛在客戶與我們的設計師或統包商進行免費的現場丈量與進一步洽談。

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI (for web service), Pytorch (for AI/ML), pdfplumber (for PDF extraction), openpyxl (for Excel extraction)
**Storage**: Firestore (for user session and quote data)
**Testing**: pytest
**Target Platform**: Google Cloud Run (as a containerized web service)
**Project Type**: Web Service
**Performance Goals**: 報價單分析在 60 秒內完成，互動式問答回應時間 < 3 秒。
**Constraints**: 需處理多種格式不一的報價單，確保 AI 回覆的專業性與準確性。
**Scale/Scope**: 初期支援每日 100 位使用者，處理 PDF 與 Excel 格式。

## Constitution Check

*此階段暫無違反憲法原則。*

## Project Structure

### Documentation (this feature)

```text
specs/002-interior-deco-ai/
├── plan.md              # 本文件
├── spec.md              # 功能規格 (下一步產出)
└── tasks.md             # 開發任務清單 (未來產出)
```

### Source Code (repository root)

```text
# 選擇 Web Application 結構

# 後端服務 (AI Agent 核心)
analysis-service/
├── src/
│   ├── agents/              # 新增: 裝潢 AI Agent 模組
│   │   ├── quote_analyzer.py # 報價單分析器
│   │   └── requirement_interviewer.py # 需求訪談器
│   ├── models/              # 資料模型 (e.g., Quote, Item, Spec)
│   ├── services/            # 核心服務 (e.g., file_processing, ai_interaction)
│   └── api/                 # API endpoints
└── tests/

# 前端介面 (使用者互動)
web-service/
├── src/
│   ├── components/          # 新增: 上傳區、對話視窗
│   ├── pages/               # 新增: AI 夥伴主頁
│   └── services/            # API 呼叫
└── tests/
```

**Structure Decision**: 採用前後端分離的 Web 應用程式結構。`analysis-service` 負責處理核心的 AI 分析與商業邏輯，`web-service` 負責提供使用者上傳檔案與互動的介面。這樣的結構有助於未來獨立擴展 AI 功能與使用者介面。

## Complexity Tracking

> 本專案目前無須填寫。
