# Agent Lucy 🤖

由 **Microsoft Agent Framework** 和 **Azure AI Foundry** 驅動的 AI 助理

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/jimmyliao/Agent-Lucy/releases/tag/v1.2.0)
[![Framework](https://img.shields.io/badge/framework-Microsoft%20Agent%20Framework-green.svg)](https://github.com/microsoft/agent-framework)
[![MCP](https://img.shields.io/badge/MCP-3%20tools-orange.svg)](https://modelcontextprotocol.io)

> **v1.2.0 重大更新**: 後端 API 認證 & 部署策略!

**語言**: [English](README.md) | 繁體中文

---

## ✨ v1.2.0 新功能

- **🔐 後端 API 認證** - 基於 token 的安全認證系統
- **🎯 彈性用戶管理** - 透過 `WEBAPP_AUTH_USERS` 環境變數配置用戶
- **🚀 部署策略** - Cloudflare Pages (前端) + Azure Container Apps (後端) 完整指南
- **📋 一鍵部署** - `make deploy` 腳本快速部署前端
- **💰 成本分析** - 透明定價：~$0 (前端) + ~$37/月 (後端)
- **📚 增強文檔** - 完整的 DEPLOYMENT.md 部署指南

### 先前更新 (v1.1.0)

- **Microsoft Agent Framework 整合** - 專業的 agent 編排
- **51.5% 程式碼減少** - 從 231 行減少到 56 行
- **Chat 函數簡化** - 180 行 → ~10 行使用 `agent.run()`
- **自動發現 MCP 工具** - GitHub、Filesystem、Memory 工具自動註冊
- **穩定認證** - 基於 Azure OpenAI API key 的認證

---

## 📋 目錄

- [功能特色](#-功能特色)
- [系統架構](#-系統架構)
- [快速開始](#-快速開始)
- [MCP 工具](#-mcp-工具)
  - [GitHub MCP Server](#1-github-mcp-server)
  - [Filesystem MCP Server](#2-filesystem-mcp-server)
  - [Memory MCP Server](#3-memory-mcp-server)
  - [新增自訂 MCP 工具](#新增自訂-mcp-工具)
- [配置設定](#-配置設定)
- [API 文檔](#-api-文檔)
- [疑難排解](#-疑難排解)

---

## 🎯 功能特色

### 核心功能

| 功能 | 說明 | 狀態 |
|------|------|------|
| **智能對話** | Azure OpenAI GPT-4.1 驅動的對話功能 | ✅ 啟用 |
| **GitHub 操作** | 透過 MCP 提供 50+ GitHub API 功能 | ✅ 啟用 |
| **檔案管理** | 隔離目錄中的安全檔案操作 | ✅ 啟用 |
| **記憶系統** | 基於知識圖譜的持久記憶 | ✅ 啟用 |
| **Markdown 渲染** | 美觀的格式化回應 | ✅ 啟用 |
| **多用戶支援** | 獨立的對話歷史記錄 | ✅ 啟用 |
| **即時對話** | WebSocket 和 HTTP API | ✅ 啟用 |
| **用戶認證** | 安全的後端 API 認證系統 | ✅ 啟用 |

### 程式碼簡化 (v1.1.0)

**之前** (v1.0.0):
```python
# 180 行手動呼叫 Azure OpenAI API
messages = [...]
tools = convert_mcp_to_openai_functions()
response = await azure_openai_client.chat.completions.create(...)
# 手動解析和執行工具呼叫
# 第二次 LLM 呼叫以聚合結果
```

**之後** (v1.1.0):
```python
# 使用 Microsoft Agent Framework 只需 ~10 行
agent = await get_or_create_agent()
response = await agent.run(request.message)
response_text = str(response)
```

---

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                   Agent Lucy Web App                         │
│                  (FastAPI + Vanilla JS)                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│            Microsoft Agent Framework (v1.1.0)                │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Agent Lucy (agent.run())                              │ │
│  │  • 自動發現 MCP 工具                                    │ │
│  │  • 根據用戶意圖選擇適當工具                             │ │
│  │  • 執行工具呼叫                                         │ │
│  │  • 聚合並格式化結果                                     │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  GitHub MCP     │ │ Filesystem MCP  │ │  Memory MCP     │
│  (Docker)       │ │ (npx/Node.js)   │ │ (npx/Node.js)   │
│                 │ │                 │ │                 │
│ • search_users  │ │ • read_file     │ │ • create_       │
│ • get_user      │ │ • write_file    │ │   entities      │
│ • list_repos    │ │ • list_dir      │ │ • create_       │
│ • get_repo      │ │ • delete_file   │ │   relations     │
│ • list_issues   │ │ • get_file_info │ │ • search_nodes  │
│ • create_issue  │ │                 │ │ • read_graph    │
│ • 40+ 更多...   │ │                 │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  Azure OpenAI    │
                  │    GPT-4.1       │
                  │  (模型後端)       │
                  └──────────────────┘
```

---

## 🔄 v1.0 vs v1.1 遷移

### 架構比較

**v1.0.0 - 手動 Azure OpenAI Function Calling**:
```
用戶請求
     ↓
┌─────────────────────────────────────────────────────┐
│  手動實作 (180 行)                                    │
│                                                       │
│  1. 準備訊息 + 對話歷史                              │
│  2. 將 MCP 工具轉換為 OpenAI 函數                    │
│  3. 呼叫 Azure OpenAI API                            │
│  4. 從回應中解析函數呼叫                             │
│  5. 手動執行 MCP 工具                                │
│  6. 聚合工具結果                                     │
│  7. 第二次 OpenAI API 呼叫以獲得最終回應             │
│  8. 每一步驟的手動錯誤處理                           │
└─────────────────────────────────────────────────────┘
```

**v1.1.0 - Microsoft Agent Framework**:
```
用戶請求
     ↓
┌─────────────────────────────────────────────────────┐
│  agent.run(message)  (~10 行)                        │
│                                                       │
│  ✅ 自動對話管理                                     │
│  ✅ 自動工具發現與註冊                               │
│  ✅ 自動函數呼叫循環                                 │
│  ✅ 自動錯誤重試機制                                 │
│  ✅ 自動結果聚合                                     │
└─────────────────────────────────────────────────────┘
```

### 主要優勢

| 面向 | v1.0.0 (手動) | v1.1.0 (Framework) | 改進 |
|------|---------------|-------------------|------|
| **程式碼行數** | 231 行 | 56 行 | **-51.5%** ⬇️ |
| **Chat 函數** | 180 行 | ~10 行 | **-94.4%** ⬇️ |
| **工具註冊** | 手動轉換 | 自動發現 | **100% 自動化** ✅ |
| **錯誤處理** | 分散各處 | 集中管理 | **更簡單** ✅ |
| **函數呼叫循環** | 手動迭代 | 自動處理 | **零維護** ✅ |
| **新增工具** | 30+ 行 | 5 行 | **83% 更快** ⬇️ |
| **對話管理** | 手動追蹤 | Framework 管理 | **自動化** ✅ |
| **測試複雜度** | 高 (許多邊緣案例) | 低 (framework 已測試) | **更容易** ✅ |

---

## 🚀 快速開始

### 環境需求

- **Python 3.11+**
- **Node.js 18+** (用於 MCP 工具)
- **Docker** (用於 GitHub MCP server)
- **Azure OpenAI API** 存取權限
- **GitHub Personal Access Token** (用於 GitHub MCP)

### 安裝步驟

```bash
# 1. 複製專案
git clone https://github.com/jimmyliao/Agent-Lucy.git
cd Agent-Lucy

# 2. 建立虛擬環境
uv venv
source .venv/bin/activate  # macOS/Linux
# 或: .venv\Scripts\activate  # Windows

# 3. 安裝 Python 依賴套件
uv sync

# 4. 安裝 MCP 工具
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-memory
docker pull ghcr.io/github/github-mcp-server

# 5. 配置環境變數
cp .env.example .env
# 編輯 .env 填入您的憑證

# 6. 啟動伺服器
cd webapp
make dev
```

### 快速測試

```bash
# 測試基本對話
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Lucy!", "user_id": "test"}'

# 測試 GitHub MCP
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "顯示 GitHub 用戶: torvalds", "user_id": "test"}'
```

---

## 🔧 MCP 工具

### 什麼是 MCP?

**MCP (Model Context Protocol)** 是一個標準化協議,用於將 AI agents 連接到外部工具和資料來源。

#### 主要優勢:
- **自動發現**: Agent Framework 自動找到並註冊 MCP 工具
- **型別安全**: 基於 JSON schema 的工具定義
- **標準介面**: 適用於任何符合 MCP 的工具
- **多種傳輸方式**: stdio、HTTP、Server-Sent Events

### 已註冊的 MCP 工具

| 工具 | 傳輸方式 | 說明 | 函數數量 |
|------|---------|------|---------|
| **GitHub** | Docker (stdio) | 官方 GitHub API 存取 | 50+ |
| **Filesystem** | npx (stdio) | 安全的檔案操作 | 6 |
| **Memory** | npx (stdio) | 知識圖譜儲存 | 5 |

---

### 1. GitHub MCP Server

#### 概述

官方 GitHub MCP Server 提供完整的 GitHub API 存取並支援認證。

#### 安裝

```bash
# 拉取官方 Docker image
docker pull ghcr.io/github/github-mcp-server

# 手動測試
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here \
  ghcr.io/github/github-mcp-server
```

#### 配置

**在 `.env` 中**:
```bash
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
```

#### 可用功能 (50+)

**用戶操作**:
- `search_users` - 搜尋 GitHub 用戶
- `get_user` - 取得用戶個人資料
- `list_user_repos` - 列出用戶的 repositories
- `get_user_gists` - 取得用戶的 gists

**Repository 操作**:
- `get_repo` - 取得 repository 詳情
- `list_repos` - 列出 repositories
- `fork_repo` - Fork repository
- `get_repo_readme` - 取得 repository README

**Issue 操作**:
- `list_issues` - 列出 repository issues
- `get_issue` - 取得特定 issue
- `create_issue` - 建立新 issue
- `update_issue` - 更新現有 issue

**Pull Request 操作**:
- `list_pulls` - 列出 pull requests
- `get_pull` - 取得特定 PR
- `create_pull` - 建立新 PR
- `merge_pull` - 合併 PR

**還有 30+ 個功能...**

#### 使用範例

**查詢用戶資訊**:
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "顯示 GitHub 用戶 jimmyliao 的資訊",
    "user_id": "test"
  }'
```

---

### 2. Filesystem MCP Server

#### 概述

受限於 `/tmp/agent-lucy-uploads` 目錄的安全檔案操作。

#### 可用功能

| 函數 | 說明 | 參數 |
|------|------|------|
| `read_file` | 讀取檔案內容 | `path: string` |
| `write_file` | 寫入內容到檔案 | `path: string, content: string` |
| `list_directory` | 列出目錄中的檔案 | `path: string` |
| `create_directory` | 建立新目錄 | `path: string` |
| `delete_file` | 刪除檔案 | `path: string` |
| `get_file_info` | 取得檔案中繼資料 | `path: string` |

#### 安全性

- **沙盒化**: 操作僅限於 `/tmp/agent-lucy-uploads`
- **無路徑遍歷**: 無法存取上傳目錄外的檔案
- **安全操作**: 所有檔案操作都有記錄

---

### 3. Memory MCP Server

#### 概述

基於知識圖譜的持久記憶系統,用於跨會話上下文。

#### 可用功能

| 函數 | 說明 | 參數 |
|------|------|------|
| `create_entities` | 儲存新知識 | `entities: Entity[]` |
| `create_relations` | 連結實體 | `relations: Relation[]` |
| `search_nodes` | 查詢知識圖譜 | `query: string` |
| `read_graph` | 讀取完整圖譜 | - |
| `delete_entities` | 移除知識 | `entity_names: string[]` |

#### 使用範例

**儲存用戶偏好**:
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "記住：我最喜歡的語言是 Python,而且我熱愛 AI",
    "user_id": "test"
  }'
```

**回憶資訊**:
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "我的程式語言偏好是什麼?",
    "user_id": "test"
  }'
```

---

### 新增自訂 MCP 工具

#### 步驟 1: 尋找或建立 MCP Server

瀏覽可用的 servers:
- [MCP Servers Registry](https://github.com/modelcontextprotocol/servers)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)

#### 步驟 2: 加入到 `init_mcp_tools()`

範例: 新增天氣 MCP server

```python
async def init_mcp_tools():
    # ... 現有工具 ...

    # 天氣 MCP 工具
    try:
        weather_api_key = os.getenv("WEATHER_API_KEY")
        if weather_api_key:
            weather_tool = MCPStdioTool(
                name="weather",
                command="npx",
                args=["-y", "@example/mcp-weather"],
                env={"WEATHER_API_KEY": weather_api_key},
                description="取得任何地點的天氣預報"
            )
            mcp_tools["weather"] = weather_tool
            tools_status["weather"] = "configured"
    except Exception as e:
        tools_status["weather"] = f"error: {str(e)}"

    return mcp_tools
```

---

## ⚙️ 配置設定

### 環境變數

```bash
# Azure OpenAI (必要)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4.1

# GitHub MCP (選用但建議)
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here

# Web App 認證 (正式環境必要)
# JSON 格式: {"username": "password", "user2": "pass2"}
WEBAPP_AUTH_USERS={"leap":"jimmy","jimmy":"jimmy"}
```

### 檔案結構

```
Agent-Lucy/
├── .env                    # 環境配置
├── .env.example           # .env 範本
├── webapp/
│   ├── api/
│   │   └── main.py        # FastAPI 後端 (Microsoft Agent Framework)
│   ├── public/
│   │   └── index.html     # Web UI
│   └── Makefile          # 開發指令
├── README.md             # 英文說明文件
├── README.zh-TW.md       # 繁體中文說明文件
└── pyproject.toml        # Python 依賴套件
```

---

## 📚 API 文檔

### 認證

```bash
POST /api/auth/login
```

**請求**:
```json
{
  "username": "jimmy",
  "password": "jimmy"
}
```

**回應 (成功)**:
```json
{
  "success": true,
  "message": "Login successful",
  "token": "FPyyE3zQaSpMNM8Qi4X_TyA6o3SPGBWQjWmmUn0D_eg"
}
```

**回應 (失敗)**:
```json
{
  "success": false,
  "message": "Invalid username or password",
  "token": null
}
```

**認證功能**:
- 後端 API 驗證 (前端無憑證)
- 透過 `.env` 配置用戶列表 (JSON 格式)
- 為會話產生安全 token
- 無需修改程式碼即可新增/移除用戶

### 健康檢查

```bash
GET /api/health
```

**回應**:
```json
{
  "status": "healthy",
  "agent": "agent-lucy",
  "model": "gpt-4.1",
  "mcp_available": true,
  "mcp_tools_count": 3
}
```

### 對話

```bash
POST /api/chat
Content-Type: application/json

{
  "message": "您的訊息",
  "user_id": "選用的用戶ID"
}
```

**回應**:
```json
{
  "response": "Agent 的回應",
  "thread_id": "thread_af_1234567890",
  "timestamp": "2025-11-27T22:00:00"
}
```

### 檔案上傳

```bash
POST /api/upload
Content-Type: multipart/form-data

file: <檔案>
user_id: test
```

### MCP 工具列表

```bash
GET /api/mcp/tools
```

**回應**:
```json
{
  "mcp_available": true,
  "tools": [
    {
      "tool": "github",
      "description": "官方 GitHub MCP Server",
      "functions": [...]
    }
  ]
}
```

---

## 🐛 疑難排解

### 401 未授權錯誤

**解決方案**: 使用 Azure OpenAI endpoint (不是 Azure AI Project endpoint)

```bash
# ✅ 正確
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=FmTg81A86QQ...

# ❌ 錯誤
AZURE_EXISTING_AIPROJECT_ENDPOINT=...
```

### GitHub MCP 無法運作

**解決方案**:
1. 確保 Docker 正在執行
2. 拉取最新 image: `docker pull ghcr.io/github/github-mcp-server`
3. 驗證 token: `GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...`

### MCP 工具未被發現

**解決方案**:
1. 檢查初始化: `curl http://localhost:8001/api/mcp/tools`
2. 驗證 Node.js 已安裝: `node --version`
3. 檢查伺服器日誌中的錯誤

---

## 🚀 部署指南

完整的部署指南請參考 [DEPLOYMENT.md](DEPLOYMENT.md)。

### 快速部署

**前端 (Cloudflare Pages)**:
```bash
cd webapp
make deploy
```

**後端 (Azure Container Apps)**:
```bash
# 參考 DEPLOYMENT.md 的完整步驟
```

### 部署成本

| 服務 | 方案 | 月費用 (USD) |
|------|------|-------------|
| **Cloudflare Pages** | Free Tier | $0 |
| **Azure Container Apps** | Consumption | ~$37 |
| **Azure OpenAI** | GPT-4.1 | ~$15-30 |
| **總計** | | **~$52-67** |

---

## 📝 授權

MIT License

---

## 🙏 致謝

- **Microsoft Agent Framework** - 簡化的 agent 編排
- **Model Context Protocol (MCP)** - 標準化工具整合
- **Azure OpenAI** - GPT-4.1 模型
- **GitHub MCP Server** - 官方 GitHub 整合

---

## 📊 變更日誌

### v1.2.0 (2025-11-27)

**重大更新**: 後端 API 認證 & 部署策略

- ✅ 基於 token 的後端 API 認證
- ✅ 透過 `WEBAPP_AUTH_USERS` 環境變數彈性管理用戶
- ✅ 安全憑證處理 (無硬編碼密碼)
- ✅ 完整部署指南 (DEPLOYMENT.md)
- ✅ 一鍵前端部署到 Cloudflare Pages
- ✅ Azure Container Apps 後端部署策略
- ✅ 完整成本分析 (~$0 前端 + ~$37/月 後端)
- ✅ 增強的 API 文檔

### v1.1.0 (2025-11-27)

**重大更新**: Microsoft Agent Framework 整合

- ✅ 遷移到 Microsoft Agent Framework
- ✅ 51.5% 程式碼減少 (231 → 56 行)
- ✅ 自動發現 MCP 工具
- ✅ GitHub MCP: 50+ 操作
- ✅ Memory MCP: 知識圖譜儲存
- ✅ Filesystem MCP: 安全檔案操作

### v1.0.0 (2025-11-26)

- 初始版本發布,包含 GitHub MCP 整合
- 手動 Azure OpenAI API 實作

---

**由 Jimmy Liao 用 ❤️ 打造**

[![GitHub](https://img.shields.io/badge/GitHub-jimmyliao-blue?logo=github)](https://github.com/jimmyliao)
