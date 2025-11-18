# ✅ 問題已修復 - 啟動指南

## 🔧 已修復的問題

**問題**: `ModuleNotFoundError: No module named 'api'`

**原因**: Python 模組需要 `__init__.py` 文件來標識目錄為可導入的包

**解決方案**: 已添加所有必要的 `__init__.py` 文件和修正導入路徑

---

## 🚀 現在可以啟動了！

### 方法 1: 兩個終端機（推薦）

#### 終端機 1 - 後端
```bash
cd /Users/stephen/Desktop/Nooko_Your_InteriorDeco_Ai/analysis-service
pip3 install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**預期輸出**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx]
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **測試**: 開啟 http://localhost:8000 應該看到:
```json
{"message": "Analysis Service is running!"}
```

#### 終端機 2 - 前端
```bash
cd /Users/stephen/Desktop/Nooko_Your_InteriorDeco_Ai/web-service
npm install
npm run dev
```

**預期輸出**:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

✅ **測試**: 開啟 http://localhost:5173 應該看到歡迎頁面

---

### 方法 2: 使用背景執行（單一終端機）

```bash
# 進入專案根目錄
cd /Users/stephen/Desktop/Nooko_Your_InteriorDeco_Ai

# 啟動後端（背景執行）
cd analysis-service
pip3 install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "後端 PID: $BACKEND_PID"

# 啟動前端（前台執行）
cd ../web-service
npm install
npm run dev

# 停止時使用：
# kill $BACKEND_PID
```

---

### 方法 3: 使用 tmux（進階用戶）

```bash
cd /Users/stephen/Desktop/Nooko_Your_InteriorDeco_Ai

# 創建新 session 並分割視窗
tmux new-session -s houseiq \; \
  send-keys 'cd analysis-service && pip3 install -r requirements.txt && uvicorn src.main:app --reload' C-m \; \
  split-window -h \; \
  send-keys 'cd web-service && npm install && npm run dev' C-m

# 退出 tmux: Ctrl+B 然後按 D
# 重新連接: tmux attach -t houseiq
# 關閉: tmux kill-session -t houseiq
```

---

## 📋 啟動檢查清單

### 後端檢查
- [ ] `pip3 install` 成功完成
- [ ] 看到 "Application startup complete"
- [ ] http://localhost:8000 可以訪問
- [ ] http://localhost:8000/docs 可以看到 API 文件

### 前端檢查
- [ ] `npm install` 成功完成
- [ ] 看到 "Local: http://localhost:5173/"
- [ ] http://localhost:5173 可以訪問
- [ ] 看到 "🏠 HouseIQ 裝潢 AI 夥伴" 標題
- [ ] 頁面底部有 "專案 ID: xxx"

---

## 🐛 常見問題排除

### 問題 1: 後端啟動失敗 - ModuleNotFoundError

**症狀**:
```
ModuleNotFoundError: No module named 'xxx'
```

**解決**:
```bash
cd analysis-service
pip3 install -r requirements.txt --upgrade
```

如果還是有問題：
```bash
pip3 install fastapi uvicorn pydantic python-multipart
```

---

### 問題 2: 前端依賴安裝失敗

**症狀**:
```
npm ERR! code ELIFECYCLE
```

**解決**:
```bash
cd web-service
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

---

### 問題 3: 端口被占用

**症狀**:
```
ERROR: Address already in use
```

**解決**:

檢查並關閉占用端口的進程：
```bash
# 檢查 8000 端口
lsof -ti:8000 | xargs kill -9

# 檢查 5173 端口
lsof -ti:5173 | xargs kill -9
```

或改用其他端口：
```bash
# 後端使用 8001
uvicorn src.main:app --reload --port 8001

# 前端使用 5174
npm run dev -- --port 5174
```

---

### 問題 4: CORS 錯誤

**症狀**:
```
Access to fetch at ... has been blocked by CORS policy
```

**原因**: 後端的 CORS 設置已經允許所有來源，這個錯誤通常是因為後端沒有啟動

**解決**: 確認後端正在運行，並檢查端口

---

### 問題 5: Pydantic 警告

**症狀**:
```
UserWarning: Valid config keys have changed in V2:
* 'allow_population_by_field_name' has been renamed to 'validate_by_name'
```

**說明**: 這只是警告，不影響功能。可以忽略。

如果想修復，編輯 `src/models/project.py`：
```python
# 將
class Config:
    allow_population_by_field_name = True

# 改為
class Config:
    populate_by_name = True
```

---

## ✅ 成功啟動的標誌

看到以下畫面就代表成功了：

### 後端終端機
```
INFO:     Application startup complete.
```

### 前端終端機
```
➜  Local:   http://localhost:5173/
```

### 瀏覽器 (http://localhost:5173)
- 看到紫色漸層的標題
- 歡迎訊息
- 「開始使用」按鈕
- 頁面底部顯示專案 ID

---

## 🧪 快速功能測試

1. **點擊「開始使用」** → 進入上傳頁面
2. **點擊「跳過上傳」** → 進入訪談頁面
3. **回答第一題**（輸入名字）→ 點擊「下一步」
4. **觀察進度條** → 應該從 0% 增加到約 3%
5. **繼續回答幾題** → 確認流程順暢

---

## 📊 系統資源監控

### 查看後端日誌
```bash
# 如果使用背景執行
tail -f backend.log

# 如果使用終端機
# 直接在後端終端機查看
```

### 查看系統資源
```bash
# CPU 和記憶體使用
top -pid $(lsof -ti:8000)
```

---

## 🛑 如何停止服務

### 方法 1: Ctrl+C
在各自的終端機按 `Ctrl+C`

### 方法 2: 關閉進程
```bash
# 後端
lsof -ti:8000 | xargs kill

# 前端
lsof -ti:5173 | xargs kill
```

### 方法 3: tmux
```bash
tmux kill-session -t houseiq
```

---

## 📝 啟動後可以做什麼

1. **完整測試**: 參考 `START_TESTING.md`
2. **查看 API 文件**: http://localhost:8000/docs
3. **開發調試**: 修改代碼後自動重載
4. **測試問卷**: 體驗 32 個問題的完整流程

---

## 🎉 準備好了！

現在您可以：
- ✅ 後端已正常運行
- ✅ 前端已正常運行
- ✅ 所有導入問題已修復
- ✅ 可以開始測試了

**祝測試順利！** 🚀

有任何問題請參考：
- `START_TESTING.md` - 完整測試指南
- `LOCAL_TESTING_GUIDE.md` - 詳細測試文件
- `UPDATES_SUMMARY.md` - 功能說明
