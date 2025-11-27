# 🔧 MCP Tools 整合指南

## 📖 什麼是 Model Context Protocol (MCP)?

Model Context Protocol (MCP) 是一個開放標準協議，讓 AI 助理能夠安全地連接到各種數據源和工具，就像 USB-C 埠一樣，為 AI 應用提供標準化的連接方式。

## 🛠️ Agent Lucy 已整合的 MCP Tools

### 1. **GitHub MCP Tool** 📦
**功能**: GitHub 倉庫操作和文件管理

**提供的能力**:
- 📝 創建、讀取、更新 GitHub 文件
- 🔍 搜索倉庫和代碼
- 🌿 分支管理
- 📋 Issues 和 Pull Requests 管理
- ⭐ 倉庫管理

**設置步驟**:
1. 前往 [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. 點擊 "Generate new token (classic)"
3. 選擇以下 scopes:
   - `repo` (完整倉庫訪問)
   - `read:org` (讀取組織資訊)
4. 生成 token 並複製
5. 將 token 添加到 `.env` 文件:
   ```bash
   GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
   ```

**使用範例**:
```
"幫我在我的倉庫中搜索所有 TODO 註釋"
"創建一個新的 issue 標題為 'Bug fix needed'"
"讀取 README.md 文件內容"
```

---

### 2. **Filesystem MCP Tool** 📁
**功能**: 文件系統操作（限定在上傳目錄）

**提供的能力**:
- 📂 列出目錄內容
- 📄 讀取文件
- ✏️ 寫入文件
- 🗂️ 創建/刪除目錄
- 🔍 搜索文件

**安全限制**:
- 僅限訪問 `/tmp/agent-lucy-uploads/` 目錄
- 無法訪問系統其他文件

**使用範例**:
```
"列出我上傳的所有文件"
"讀取我剛才上傳的 data.csv"
"分析上傳目錄中的所有 JSON 文件"
```

---

### 3. **Memory MCP Tool** 🧠
**功能**: 知識圖譜式持久化記憶系統

**提供的能力**:
- 💾 跨對話記憶資訊
- 🔗 建立知識關聯
- 📚 儲存用戶偏好和上下文
- 🎯 個性化回應

**使用範例**:
```
"記住我喜歡用 TypeScript 開發"
"我之前問過關於 FastAPI 的問題嗎?"
"根據我的偏好推薦一個框架"
```

---

## 🚀 快速開始

### 1. 安裝依賴

```bash
cd /Users/jimmyliao/workspace/agent-lucy/webapp

# 安裝 Python 依賴 (agent_framework 已包含 MCP 支援)
make install

# 確保已安裝 Node.js 和 npm (用於 MCP servers)
node --version  # 應該 >= 18.0.0
npm --version
```

### 2. 配置環境變數

```bash
# 複製範例配置
cp ../.env.example ../.env

# 編輯 .env 文件，添加 GitHub token
# GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
```

### 3. 初始化 MCP Tools

```bash
# 啟動服務器
make dev

# 在另一個終端，初始化 MCP tools
curl -X POST http://localhost:8001/api/mcp/init
```

### 4. 檢查 MCP Tools 狀態

```bash
# 查看可用的 MCP tools
curl http://localhost:8001/api/mcp/tools | jq .
```

---

## 📡 API 端點

### `POST /api/mcp/init`
初始化所有 MCP tools

**Response**:
```json
{
  "status": "initialized",
  "mcp_available": true,
  "tools": {
    "github": "configured",
    "filesystem": "configured",
    "memory": "configured"
  }
}
```

### `GET /api/mcp/tools`
列出所有可用的 MCP tools 和它們的函數

**Response**:
```json
{
  "mcp_available": true,
  "tools": [
    {
      "tool": "github",
      "description": "GitHub repository operations and file management",
      "functions": [
        {
          "name": "create_or_update_file",
          "description": "Create or update a file in a GitHub repository"
        },
        ...
      ]
    },
    ...
  ]
}
```

### `GET /api/health`
健康檢查（已更新包含 MCP 資訊）

**Response**:
```json
{
  "status": "healthy",
  "agent": "agent-lucy",
  "model": "gpt-4.1",
  "mcp_available": true,
  "mcp_tools_count": 3
}
```

---

## 🧪 測試 MCP Tools

### 測試 GitHub Tool

```bash
# 1. 初始化 tools
curl -X POST http://localhost:8001/api/mcp/init

# 2. 發送測試訊息
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "幫我列出 anthropics/anthropic-sdk-python 倉庫的 README.md 文件內容",
    "user_id": "test_user"
  }'
```

### 測試 Filesystem Tool

```bash
# 1. 上傳文件
curl -X POST http://localhost:8001/api/upload \
  -F "file=@test.txt" \
  -F "user_id=test_user"

# 2. 要求 Lucy 讀取文件
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "讀取我剛上傳的 test.txt 文件",
    "user_id": "test_user"
  }'
```

### 測試 Memory Tool

```bash
# 1. 儲存資訊
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "記住我的名字是 Jimmy，我喜歡用 Python 和 TypeScript",
    "user_id": "test_user"
  }'

# 2. 測試記憶
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你記得我喜歡哪些程式語言嗎？",
    "user_id": "test_user"
  }'
```

---

## 🔧 進階配置

### 自訂 MCP Tool 設置

編輯 `webapp/api/main.py` 中的 `init_mcp_tools()` 函數：

```python
# 範例：添加自訂環境變數
github_tool = MCPStdioTool(
    name="github",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-github"],
    env={
        "GITHUB_PERSONAL_ACCESS_TOKEN": github_token,
        "GITHUB_API_URL": "https://api.github.com",  # 自訂
    },
    description="GitHub repository operations",
    approval_mode="never_require",  # 或 "always_require"
)
```

### 限制特定工具函數

```python
# 只允許某些 GitHub 函數
github_tool = MCPStdioTool(
    name="github",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-github"],
    env={"GITHUB_PERSONAL_ACCESS_TOKEN": github_token},
    allowed_tools=["search_repositories", "get_file_contents"],  # 限制
)
```

---

## 🐛 常見問題排解

### Q: MCP tools 初始化失敗

**檢查**:
1. Node.js 是否已安裝: `node --version`
2. npm 是否可用: `npm --version`
3. 網路連接是否正常（需要下載 npm packages）

**解決方法**:
```bash
# 手動安裝 MCP servers
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-memory
```

### Q: GitHub tool 顯示 "missing_token"

**檢查**:
1. `.env` 文件是否存在
2. `GITHUB_PERSONAL_ACCESS_TOKEN` 是否設置
3. Token 是否有正確的 scopes

**解決方法**:
```bash
# 檢查環境變數
echo $GITHUB_PERSONAL_ACCESS_TOKEN

# 如果為空，編輯 .env 文件
vim /Users/jimmyliao/workspace/agent-lucy/.env

# 重啟服務器
make stop
make dev
```

### Q: Filesystem tool 無法訪問文件

**檢查**:
1. 文件是否上傳到 `/tmp/agent-lucy-uploads/`
2. 權限是否正確

**解決方法**:
```bash
# 確保目錄存在並有權限
mkdir -p /tmp/agent-lucy-uploads
chmod 755 /tmp/agent-lucy-uploads

# 查看目錄內容
ls -la /tmp/agent-lucy-uploads/
```

---

## 📚 相關資源

### 官方文檔
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Azure AI Foundry MCP Integration](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/model-context-protocol)
- [MCP Servers GitHub](https://github.com/modelcontextprotocol/servers)

### NPM Packages
- [@modelcontextprotocol/server-github](https://www.npmjs.com/package/@modelcontextprotocol/server-github)
- [@modelcontextprotocol/server-filesystem](https://www.npmjs.com/package/@modelcontextprotocol/server-filesystem)
- [@modelcontextprotocol/server-memory](https://github.com/modelcontextprotocol/servers/tree/main/src/memory)

### Python SDK
- [agent_framework MCP Documentation](https://learn.microsoft.com/en-us/agent-framework/user-guide/model-context-protocol/)

---

## 🎯 下一步

1. **測試所有 MCP tools**: 使用上面的測試命令驗證每個工具
2. **添加自訂 MCP server**: 參考 [MCP Server 開發指南](https://modelcontextprotocol.io/docs/building-servers)
3. **整合到前端**: 更新 `public/index.html` 顯示 MCP 功能
4. **監控和日誌**: 添加 MCP tool 使用的日誌記錄

---

**版本**: 1.0.0
**最後更新**: 2025-11-27
**作者**: Agent-JimmyLiao
