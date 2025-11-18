#!/bin/bash

# HouseIQ 快速啟動腳本
# 使用方法：chmod +x QUICK_START.sh && ./QUICK_START.sh

echo "🚀 HouseIQ 裝潢 AI 夥伴 - 本地測試啟動"
echo "=================================="
echo ""

# 顏色定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}請在兩個終端機視窗分別執行以下指令：${NC}"
echo ""

echo -e "${GREEN}終端機 1 - 啟動後端：${NC}"
echo "cd analysis-service"
echo "pip3 install -r requirements.txt"
echo "uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
echo ""

echo -e "${GREEN}終端機 2 - 啟動前端：${NC}"
echo "cd web-service"
echo "npm install"
echo "npm run dev"
echo ""

echo -e "${BLUE}或者使用以下一鍵指令：${NC}"
echo ""

echo -e "${GREEN}方案 A - 使用 tmux（推薦）：${NC}"
echo "tmux new-session -d -s houseiq 'cd analysis-service && pip3 install -r requirements.txt && uvicorn src.main:app --reload'"
echo "tmux split-window -h 'cd web-service && npm install && npm run dev'"
echo "tmux attach -t houseiq"
echo ""

echo -e "${GREEN}方案 B - 背景執行：${NC}"
echo "cd analysis-service && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 &"
echo "cd web-service && npm run dev"
echo ""

echo -e "${RED}注意：${NC}"
echo "- 後端會在 http://localhost:8000 啟動"
echo "- 前端會在 http://localhost:5173 啟動"
echo "- 首次執行需要安裝依賴，可能需要幾分鐘"
echo ""

echo "詳細說明請查看 START_TESTING.md"
