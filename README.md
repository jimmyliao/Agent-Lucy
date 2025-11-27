# Agent Lucy - Azure AI Foundry Agent Integration

與 Azure AI Foundry 的 agent-lucy 代理互動的 Python 專案。

## 功能特性

- 與 Azure AI Projects 的整合
- 使用 DefaultAzureCredential 進行認證
- 簡潔的專案結構，易於擴展
- 使用 uv 進行快速套件管理

## 先決條件

- Python 3.11 或更高版本
- Azure 訂閱和 AI Foundry 專案
- uv 套件管理工具

## 安裝

### 1. 建立虛擬環境

```bash
cd agent-lucy
uv venv .venv
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows
```

### 2. 安裝依賴

```bash
uv sync
```

### 3. 配置環境變數

```bash
cp .env.example .env
# 編輯 .env 填入您的 Azure 認證
```

## 配置

在 `.env` 檔案中設定以下變數：

```env
AZURE_EXISTING_AGENT_ID=agent-lucy:2
AZURE_ENV_NAME=agents-playground-2758
AZURE_LOCATION=australiaeast
AZURE_SUBSCRIPTION_ID=<your-subscription-id>
AZURE_EXISTING_AIPROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
AZURE_EXISTING_AIPROJECT_RESOURCE_ID=/subscriptions/<sub-id>/resourceGroups/<rg>/...
```

## 使用方式

執行主程式：

```bash
python main.py
```

預期輸出：

```
Retrieved agent: agent-lucy
Response output: [Agent Lucy 的回應]
```

## 專案結構

```
agent-lucy/
├── .env                          # 環境變數（不納入版控）
├── .env.example                  # 環境變數範本
├── .gitignore                    # Git 忽略設定
├── pyproject.toml               # 專案配置與依賴管理
├── README.md                    # 本檔案
├── main.py                      # 主程式
├── src/
│   └── agent_lucy/
│       ├── __init__.py          # 套件初始化
│       └── __version__.py       # 版本資訊
└── .venv/                       # 虛擬環境
```

## 開發指南

### 安裝開發依賴

```bash
uv sync --all-extras
```

### 執行測試

```bash
uv run pytest
```

### 程式碼格式化

```bash
uv run ruff check .
```

## Azure 認證

此專案使用 `DefaultAzureCredential`，它會按以下順序嘗試認證：

1. 環境變數
2. Managed Identity
3. Azure CLI
4. Azure PowerShell
5. Interactive browser

建議在本地開發時使用 `az login` 進行認證。

## 故障排除

### 認證失敗

確保您已經透過 Azure CLI 登入：

```bash
az login
az account set --subscription <your-subscription-id>
```

### 找不到 Agent

確認 `.env` 中的 `AZURE_EXISTING_AGENT_ID` 和 `AZURE_EXISTING_AIPROJECT_ENDPOINT` 正確無誤。

## 參考資源

- [Azure AI Projects Python SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme)
- [Azure AI Foundry 文件](https://learn.microsoft.com/en-us/azure/ai-studio/)
- [DefaultAzureCredential](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential)

## 授權

MIT License

## 作者

Jimmy Liao <jimmy@leapdesign.ai>
