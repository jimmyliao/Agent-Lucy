# Agent Lucy Web App

與 Agent Lucy 互動的 Web 應用程式，支援即時聊天、對話歷史、檔案上傳和多使用者。

## 功能特色

- ✅ **即時聊天**: 與 agent-lucy 進行自然對話
- ✅ **對話歷史**: 自動儲存和顯示對話記錄
- ✅ **檔案上傳**: 上傳檔案讓 agent 分析
- ✅ **多使用者支援**: 每個使用者獨立的對話空間
- ✅ **響應式設計**: 支援桌面和行動裝置
- ✅ **WebSocket 支援**: 可選的即時通訊

## 技術堆棧

### 後端
- **FastAPI**: Python 非同步 Web 框架
- **Azure AI Projects SDK**: Azure AI Foundry 整合
- **WebSocket**: 即時通訊支援

### 前端
- **純 HTML/CSS/JavaScript**: 無需 build 步驟
- **現代化 UI**: 漸層色彩、動畫效果
- **響應式設計**: 自適應各種螢幕尺寸

### 部署
- **Cloudflare Pages**: 前端靜態檔案
- **Cloudflare Workers** (可選): API 後端

## 快速開始

### 1. 本地開發

#### 啟動後端
```bash
cd webapp
python -m pip install fastapi uvicorn python-multipart
python api/main.py
```

後端將運行在 `http://localhost:8000`

#### 開啟前端
直接在瀏覽器中開啟 `webapp/public/index.html`

或使用 Python HTTP 伺服器：
```bash
cd webapp/public
python -m http.server 8080
```

然後訪問 `http://localhost:8080`

### 2. 部署到 Cloudflare Pages

#### 準備工作
```bash
# 安裝 Wrangler CLI
npm install -g wrangler

# 登入 Cloudflare
wrangler login
```

#### 部署前端到 Pages
```bash
cd webapp
wrangler pages deploy public --project-name agent-lucy-webapp
```

#### 配置環境變數
在 Cloudflare Pages 儀表板中設定：
- `AZURE_ENDPOINT`: Azure AI Project 端點
- 其他必要的 Azure 認證變數

### 3. 使用 Docker

```bash
cd webapp
docker build -t agent-lucy-webapp .
docker run -p 8000:8000 agent-lucy-webapp
```

## 專案結構

```
webapp/
├── api/
│   └── main.py                 # FastAPI 後端
├── public/
│   ├── index.html             # 主頁面
│   ├── css/                   # 樣式表（可選）
│   └── js/                    # JavaScript（可選）
├── wrangler.toml              # Cloudflare 配置
├── Dockerfile                 # Docker 配置
├── requirements.txt           # Python 依賴
└── README.md                  # 本檔案
```

## API 端點

### REST API

#### `GET /`
返回主頁面

#### `GET /api/health`
健康檢查
```json
{
  "status": "healthy",
  "agent": "agent-lucy",
  "model": "gpt-4.1"
}
```

#### `POST /api/chat`
發送訊息給 agent
```json
// Request
{
  "message": "Hello!",
  "user_id": "user_123",
  "thread_id": "optional"
}

// Response
{
  "response": "Hello! How can I help you?",
  "thread_id": "thread_xxx",
  "timestamp": "2025-11-27T10:00:00"
}
```

#### `GET /api/conversations/{user_id}`
取得對話歷史
```json
{
  "user_id": "user_123",
  "messages": [
    {
      "role": "user",
      "content": "Hello!",
      "timestamp": "2025-11-27T10:00:00"
    }
  ]
}
```

#### `POST /api/upload`
上傳檔案
```
Form data:
- file: 檔案
- user_id: 使用者 ID
```

### WebSocket

#### `WS /ws/{user_id}`
WebSocket 連接用於即時聊天

## 環境變數

### 必要
- `AZURE_ENDPOINT`: Azure AI Project 端點 URL

### 可選
- `AZURE_TENANT_ID`: Azure Tenant ID（用於認證）
- `AZURE_CLIENT_ID`: Azure Client ID（用於服務主體）
- `AZURE_CLIENT_SECRET`: Azure Client Secret（用於服務主體）

## 開發

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 運行測試
```bash
pytest tests/
```

### 代碼格式化
```bash
black api/
ruff check api/
```

## 故障排除

### 無法連接到後端
- 確認後端正在運行
- 檢查 `API_URL` 配置
- 查看瀏覽器控制台的錯誤訊息

### Agent 無回應
- 確認 Azure 認證正確
- 檢查 agent-lucy 是否存在
- 查看後端日誌

### WebSocket 連接失敗
- 確認防火牆設定
- 檢查 WebSocket 是否被代理阻擋
- 可以改用 HTTP API

## 下一步開發

- [ ] 整合 GitHub MCP tool
- [ ] 新增更多 MCP tools (filesystem, memory, etc.)
- [ ] 實作用戶認證
- [ ] 新增對話分支管理
- [ ] 支援 Markdown 渲染
- [ ] 新增程式碼高亮
- [ ] 整合語音輸入
- [ ] 支援多語言

## 授權

MIT License

## 作者

Agent-JimmyLiao <jimmy@leapdesign.ai>
