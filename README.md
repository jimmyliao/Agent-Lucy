# Agent Lucy 🤖

Your AI Assistant powered by **Microsoft Agent Framework** and **Azure AI Foundry**

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/jimmyliao/Agent-Lucy/releases/tag/v1.1.0)
[![Framework](https://img.shields.io/badge/framework-Microsoft%20Agent%20Framework-green.svg)](https://github.com/microsoft/agent-framework)
[![MCP](https://img.shields.io/badge/MCP-3%20tools-orange.svg)](https://modelcontextprotocol.io)

> **v1.1.0 Major Update**: Migrated to Microsoft Agent Framework with 51.5% code reduction!

---

## ✨ What's New in v1.1.0

- **Microsoft Agent Framework Integration** - Professional agent orchestration
- **51.5% Code Reduction** - From 231 lines to 56 lines
- **Chat Function Simplified** - 180 lines → ~10 lines using `agent.run()`
- **Auto-discovery MCP Tools** - GitHub, Filesystem, Memory tools automatically registered
- **Stable Authentication** - Azure OpenAI API key-based authentication

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [MCP Tools](#-mcp-tools)
  - [GitHub MCP Server](#1-github-mcp-server)
  - [Filesystem MCP Server](#2-filesystem-mcp-server)
  - [Memory MCP Server](#3-memory-mcp-server)
  - [Adding Custom MCP Tools](#adding-custom-mcp-tools)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Features

### Core Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| **Intelligent Chat** | Azure OpenAI GPT-4.1 powered conversations | ✅ Active |
| **GitHub Operations** | 50+ GitHub API functions via MCP | ✅ Active |
| **File Management** | Secure file operations in isolated directory | ✅ Active |
| **Memory System** | Knowledge graph-based persistent memory | ✅ Active |
| **Markdown Rendering** | Beautiful formatted responses | ✅ Active |
| **Multi-user Support** | Separate conversation histories | ✅ Active |
| **Real-time Chat** | WebSocket and HTTP APIs | ✅ Active |

### Code Simplification (v1.1.0)

**Before** (v1.0.0):
```python
# 180 lines of manual Azure OpenAI API calls
messages = [...]
tools = convert_mcp_to_openai_functions()
response = await azure_openai_client.chat.completions.create(...)
# Manual tool call parsing and execution
# Second LLM call to aggregate results
```

**After** (v1.1.0):
```python
# ~10 lines with Microsoft Agent Framework
agent = await get_or_create_agent()
response = await agent.run(request.message)
response_text = str(response)
```

---

## 🏗️ Architecture

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
│  │  • Auto-discovers MCP tools                            │ │
│  │  • Selects appropriate tool based on user intent      │ │
│  │  • Executes tool calls                                 │ │
│  │  • Aggregates and formats results                      │ │
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
│ • 40+ more...   │ │                 │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  Azure OpenAI    │
                  │    GPT-4.1       │
                  │ (Model Backend)  │
                  └──────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** (for MCP tools)
- **Docker** (for GitHub MCP server)
- **Azure OpenAI API** access
- **GitHub Personal Access Token** (for GitHub MCP)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/jimmyliao/Agent-Lucy.git
cd Agent-Lucy

# 2. Create virtual environment
uv venv
source .venv/bin/activate  # macOS/Linux
# or: .venv\Scripts\activate  # Windows

# 3. Install Python dependencies
uv sync

# 4. Install MCP tools
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-memory
docker pull ghcr.io/github/github-mcp-server

# 5. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 6. Start server
cd webapp
make dev
```

### Quick Test

```bash
# Test basic chat
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Lucy!", "user_id": "test"}'

# Test GitHub MCP
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show GitHub user: torvalds", "user_id": "test"}'
```

---

## 🔧 MCP Tools

### What is MCP?

**MCP (Model Context Protocol)** is a standardized protocol for connecting AI agents to external tools and data sources.

#### Key Benefits:
- **Auto-discovery**: Agent Framework automatically finds and registers MCP tools
- **Type-safe**: JSON schema-based tool definitions
- **Standard interface**: Works with any MCP-compliant tool
- **Multiple transports**: stdio, HTTP, Server-Sent Events

### Registered MCP Tools

| Tool | Transport | Description | Functions Count |
|------|-----------|-------------|-----------------|
| **GitHub** | Docker (stdio) | Official GitHub API access | 50+ |
| **Filesystem** | npx (stdio) | Secure file operations | 6 |
| **Memory** | npx (stdio) | Knowledge graph storage | 5 |

---

### 1. GitHub MCP Server

#### Overview

Official GitHub MCP Server providing full GitHub API access with authentication.

#### Installation

```bash
# Pull official Docker image
docker pull ghcr.io/github/github-mcp-server

# Test it manually
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here \
  ghcr.io/github/github-mcp-server
```

#### Configuration

**In `.env`**:
```bash
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
```

**In `webapp/api/main.py`**:
```python
async def init_mcp_tools():
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

    github_tool = MCPStdioTool(
        name="github",
        command="docker",
        args=[
            "run", "-i", "--rm",
            "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
            "ghcr.io/github/github-mcp-server"
        ],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": github_token},
        description="Official GitHub MCP Server - Full GitHub API access"
    )

    mcp_tools["github"] = github_tool
    return mcp_tools
```

#### Available Functions (50+)

**User Operations**:
- `search_users` - Search GitHub users
- `get_user` - Get user profile information
- `list_user_repos` - List user's repositories
- `get_user_gists` - Get user's gists

**Repository Operations**:
- `get_repo` - Get repository details
- `list_repos` - List repositories
- `fork_repo` - Fork a repository
- `get_repo_readme` - Get repository README

**Issue Operations**:
- `list_issues` - List repository issues
- `get_issue` - Get specific issue
- `create_issue` - Create new issue
- `update_issue` - Update existing issue

**Pull Request Operations**:
- `list_pulls` - List pull requests
- `get_pull` - Get specific PR
- `create_pull` - Create new PR
- `merge_pull` - Merge a PR

**File Operations**:
- `get_file_contents` - Read file from repository
- `create_or_update_file` - Write file to repository
- `delete_file` - Delete file from repository

**And 30+ more functions...**

#### Usage Examples

**Query User Information**:
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me GitHub user info for jimmyliao",
    "user_id": "test"
  }'
```

**Response**:
```json
{
  "response": "Here is the GitHub user info for **jimmyliao**:\n\n- **Username:** jimmyliao\n- **Profile:** https://github.com/jimmyliao\n- **Public Repositories:** 22\n- **Followers:** 13\n- **Following:** 10\n- **Account Created:** Feb 22, 2011"
}
```

**List Repositories**:
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "List repositories for user torvalds",
    "user_id": "test"
  }'
```

**Search Users**:
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Search GitHub users working on AI",
    "user_id": "test"
  }'
```

#### GitHub Token Setup

1. **Create Personal Access Token**:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes:
     - `read:user` - Read user profile
     - `repo` - Full repository access
     - `read:org` - Read organization data

2. **Add to `.env`**:
   ```bash
   GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
   ```

3. **Restart server**:
   ```bash
   make dev
   ```

---

### 2. Filesystem MCP Server

#### Overview

Secure file operations restricted to `/tmp/agent-lucy-uploads` directory.

#### Installation

```bash
# Install via npx
npm install -g @modelcontextprotocol/server-filesystem

# Test it manually
npx -y @modelcontextprotocol/server-filesystem /tmp/agent-lucy-uploads
```

#### Configuration

**In `webapp/api/main.py`**:
```python
async def init_mcp_tools():
    upload_dir = Path("/tmp/agent-lucy-uploads")
    upload_dir.mkdir(exist_ok=True)

    filesystem_tool = MCPStdioTool(
        name="filesystem",
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-filesystem",
            str(upload_dir)
        ],
        description="File system operations for uploaded files"
    )

    mcp_tools["filesystem"] = filesystem_tool
    return mcp_tools
```

#### Available Functions

| Function | Description | Parameters |
|----------|-------------|------------|
| `read_file` | Read file contents | `path: string` |
| `write_file` | Write content to file | `path: string, content: string` |
| `list_directory` | List files in directory | `path: string` |
| `create_directory` | Create new directory | `path: string` |
| `delete_file` | Delete file | `path: string` |
| `get_file_info` | Get file metadata | `path: string` |

#### Usage Examples

**Upload and Analyze File**:
```bash
# 1. Upload file
curl -X POST http://localhost:8001/api/upload \
  -F "file=@document.txt" \
  -F "user_id=test"

# 2. Ask Lucy to analyze it
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is in document.txt?",
    "user_id": "test"
  }'
```

**List Uploaded Files**:
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "List all uploaded files",
    "user_id": "test"
  }'
```

#### Security

- **Sandboxed**: Operations restricted to `/tmp/agent-lucy-uploads` only
- **No path traversal**: Cannot access files outside upload directory
- **Safe operations**: All file operations are logged

---

### 3. Memory MCP Server

#### Overview

Knowledge graph-based persistent memory system for cross-session context.

#### Installation

```bash
# Install via npx
npm install -g @modelcontextprotocol/server-memory

# Test it manually
npx -y @modelcontextprotocol/server-memory
```

#### Configuration

**In `webapp/api/main.py`**:
```python
async def init_mcp_tools():
    memory_tool = MCPStdioTool(
        name="memory",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-memory"],
        description="Knowledge graph-based persistent memory"
    )

    mcp_tools["memory"] = memory_tool
    return mcp_tools
```

#### Available Functions

| Function | Description | Parameters |
|----------|-------------|------------|
| `create_entities` | Store new knowledge | `entities: Entity[]` |
| `create_relations` | Link entities | `relations: Relation[]` |
| `search_nodes` | Query knowledge graph | `query: string` |
| `read_graph` | Read full graph | - |
| `delete_entities` | Remove knowledge | `entity_names: string[]` |

#### Usage Examples

**Store User Preferences**:
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Remember: My favorite language is Python and I love AI",
    "user_id": "test"
  }'
```

**Response**:
```json
{
  "response": "Got it! I'll remember that your favorite programming language is **Python** and you love working on **AI projects**."
}
```

**Recall Information**:
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are my programming preferences?",
    "user_id": "test"
  }'
```

**Response**:
```json
{
  "response": "Based on what you told me, your favorite programming language is **Python** and you love working on **AI projects**!"
}
```

#### Use Cases

- **User Preferences**: Remember favorite languages, frameworks, tools
- **Project Context**: Store project details across sessions
- **Knowledge Base**: Build a knowledge graph of related concepts
- **Conversation History**: Maintain long-term context

---

### Adding Custom MCP Tools

#### Step 1: Find or Create MCP Server

Browse available servers:
- [MCP Servers Registry](https://github.com/modelcontextprotocol/servers)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)

Or create your own (see [MCP Development](#mcp-development)).

#### Step 2: Add to `init_mcp_tools()`

Example: Adding a Weather MCP server

```python
async def init_mcp_tools():
    # ... existing tools ...

    # Weather MCP Tool
    try:
        weather_api_key = os.getenv("WEATHER_API_KEY")
        if weather_api_key:
            weather_tool = MCPStdioTool(
                name="weather",
                command="npx",
                args=["-y", "@example/mcp-weather"],
                env={"WEATHER_API_KEY": weather_api_key},
                description="Get weather forecasts for any location"
            )
            mcp_tools["weather"] = weather_tool
            tools_status["weather"] = "configured"
    except Exception as e:
        tools_status["weather"] = f"error: {str(e)}"

    return mcp_tools
```

#### Step 3: Add Environment Variables

```bash
# In .env
WEATHER_API_KEY=your_api_key_here
```

#### Step 4: Update Agent Instructions

```python
agent = client.create_agent(
    name="agent-lucy",
    instructions="""You are Lucy, a helpful AI assistant.

You can help with:
- 🐙 GitHub Operations
- 📁 File Management
- 💭 Memory Management
- 🌤️ Weather Forecasts  # NEW!
"""
)
```

#### Step 5: Test

```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather in Tokyo?", "user_id": "test"}'
```

**That's it!** The Agent Framework automatically discovers and uses the new tool.

---

### MCP Development

Want to create your own MCP server?

#### Simple Python MCP Server

```python
#!/usr/bin/env python3
from mcp.server import Server, stdio_server
from mcp.types import Tool, TextContent

server = Server("my-custom-tool")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="greet",
            description="Greet a user by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "User's name"}
                },
                "required": ["name"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "greet":
        user_name = arguments.get("name", "friend")
        return [TextContent(
            type="text",
            text=f"Hello, {user_name}! Welcome to Agent Lucy."
        )]

if __name__ == "__main__":
    stdio_server(server)
```

#### Register in Agent Lucy

```python
custom_tool = MCPStdioTool(
    name="greeter",
    command="python3",
    args=["path/to/greeter_server.py"],
    description="Custom greeting tool"
)
mcp_tools["greeter"] = custom_tool
```

#### Resources

- **Documentation**: https://modelcontextprotocol.io
- **Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **TypeScript SDK**: https://github.com/modelcontextprotocol/typescript-sdk
- **Examples**: https://github.com/modelcontextprotocol/servers

---

## ⚙️ Configuration

### Environment Variables

```bash
# Azure OpenAI (Required)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4.1

# GitHub MCP (Optional but recommended)
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here

# Azure AI Project (Legacy - for health check only)
AZURE_EXISTING_AIPROJECT_ENDPOINT=https://your-project.services.ai.azure.com/...
```

### File Structure

```
Agent-Lucy/
├── .env                    # Environment configuration
├── .env.example           # Template for .env
├── webapp/
│   ├── api/
│   │   └── main.py        # FastAPI backend (Microsoft Agent Framework)
│   ├── public/
│   │   └── index.html     # Web UI
│   └── Makefile          # Development commands
├── README.md             # This file
└── pyproject.toml        # Python dependencies
```

---

## 📚 API Documentation

### Health Check

```bash
GET /api/health
```

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

### Chat

```bash
POST /api/chat
Content-Type: application/json

{
  "message": "Your message here",
  "user_id": "optional_user_id"
}
```

**Response**:
```json
{
  "response": "Agent's response",
  "thread_id": "thread_af_1234567890",
  "timestamp": "2025-11-27T22:00:00"
}
```

### File Upload

```bash
POST /api/upload
Content-Type: multipart/form-data

file: <file>
user_id: test
```

### MCP Tools List

```bash
GET /api/mcp/tools
```

**Response**:
```json
{
  "mcp_available": true,
  "tools": [
    {
      "tool": "github",
      "description": "Official GitHub MCP Server",
      "functions": [...]
    }
  ]
}
```

---

## 🐛 Troubleshooting

### 401 Unauthorized Error

**Solution**: Use Azure OpenAI endpoint (not Azure AI Project endpoint)

```bash
# ✅ Correct
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=FmTg81A86QQ...

# ❌ Wrong
AZURE_EXISTING_AIPROJECT_ENDPOINT=...
```

### GitHub MCP Not Working

**Solution**:
1. Ensure Docker is running
2. Pull latest image: `docker pull ghcr.io/github/github-mcp-server`
3. Verify token: `GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...`

### MCP Tools Not Discovered

**Solution**:
1. Check initialization: `curl http://localhost:8001/api/mcp/tools`
2. Verify Node.js installed: `node --version`
3. Check server logs for errors

---

## 📝 License

MIT License

---

## 🙏 Acknowledgments

- **Microsoft Agent Framework** - Simplified agent orchestration
- **Model Context Protocol (MCP)** - Standardized tool integration
- **Azure OpenAI** - GPT-4.1 model
- **GitHub MCP Server** - Official GitHub integration

---

## 📊 Changelog

### v1.1.0 (2025-11-27)

**Major Update**: Microsoft Agent Framework Integration

- ✅ Migrated to Microsoft Agent Framework
- ✅ 51.5% code reduction (231 → 56 lines)
- ✅ Auto-discovery of MCP tools
- ✅ GitHub MCP: 50+ operations
- ✅ Memory MCP: Knowledge graph storage
- ✅ Filesystem MCP: Secure file operations

### v1.0.0 (2025-11-26)

- Initial release with GitHub MCP integration
- Manual Azure OpenAI API implementation

---

**Built with ❤️ by Jimmy Liao**

[![GitHub](https://img.shields.io/badge/GitHub-jimmyliao-blue?logo=github)](https://github.com/jimmyliao)
