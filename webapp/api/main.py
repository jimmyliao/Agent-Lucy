#!/usr/bin/env python3
"""
FastAPI Backend for Agent Lucy Web App
Supports: Real-time chat, conversation history, file upload, multi-user
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import asyncio
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from parent .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Azure AI imports
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Azure OpenAI imports
try:
    from openai import AzureOpenAI, AsyncAzureOpenAI
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    AZURE_OPENAI_AVAILABLE = False
    AzureOpenAI = None
    AsyncAzureOpenAI = None

# Agent Framework imports
try:
    from agent_framework import MCPStdioTool
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    MCPStdioTool = None

# Optional: Agent Framework (for future use, not required for MCP tools)
try:
    from agent_framework import ChatAgent
    from agent_framework.azure import AzureAIAgentClient
    AGENT_FRAMEWORK_AVAILABLE = True
except ImportError:
    AGENT_FRAMEWORK_AVAILABLE = False
    ChatAgent = None
    AzureAIAgentClient = None

# Configuration
AZURE_ENDPOINT = os.getenv(
    "AZURE_ENDPOINT",
    os.getenv("AZURE_EXISTING_AIPROJECT_ENDPOINT", "https://<your-resource>.services.ai.azure.com/api/projects/<your-project>")
)

# Initialize FastAPI app
app = FastAPI(
    title="Agent Lucy Web App",
    description="Chat with Agent Lucy - Azure AI Foundry Agent",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For Cloudflare Pages
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default"
    thread_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    timestamp: str

# In-memory storage (for demo - replace with database in production)
conversations: Dict[str, List[ChatMessage]] = {}
active_connections: Dict[str, WebSocket] = {}
mcp_tools: Dict[str, any] = {}  # Store active MCP tool instances

# Azure AI Client (Legacy - for health check only)
credential = DefaultAzureCredential()
project_client = AIProjectClient(endpoint=AZURE_ENDPOINT, credential=credential)

# Azure OpenAI Client (Simplified approach)
azure_openai_client = None
if AZURE_OPENAI_AVAILABLE:
    azure_openai_client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-10-21",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

# Agent Framework - Global agent instance
_agent = None
_agent_lock = asyncio.Lock()

async def get_or_create_agent():
    """Get or create the ChatAgent instance using Microsoft Agent Framework"""
    global _agent

    if _agent is None:
        async with _agent_lock:
            if _agent is None:
                # Prepare MCP tools (if already initialized)
                tools = []
                for tool_name, tool_instance in mcp_tools.items():
                    if tool_instance:
                        try:
                            if hasattr(tool_instance, 'is_connected') and not tool_instance.is_connected:
                                await tool_instance.connect()
                            tools.append(tool_instance)
                        except Exception as e:
                            print(f"WARNING: Failed to connect MCP tool {tool_name}: {e}")

                # Get Azure OpenAI connection info
                azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
                azure_openai_key = os.getenv("AZURE_OPENAI_API_KEY")

                # Create ChatAgent using Microsoft Agent Framework
                # Use the connection_id from Azure AI Project
                _agent = ChatAgent(
                    chat_client=AzureAIAgentClient(
                        async_credential=credential,
                        project_endpoint=AZURE_ENDPOINT,
                        # Try to use connection_id instead of model_deployment_name
                        connection_id="Default_AzureOpenAI"  # Standard connection name
                    ),
                    model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4"),
                    instructions="""You are Lucy, a helpful AI assistant powered by Azure AI Foundry.
You can help with various tasks including:
- Accessing GitHub repositories
- Managing files in the uploads directory
- Remembering information across conversations
Always be friendly, helpful, and concise in your responses.""",
                    tools=tools if tools else None
                )
                print(f"INFO: ChatAgent created successfully with {len(tools)} MCP tools")

    return _agent

# Legacy function for health check compatibility
def get_agent():
    """Get the agent-lucy agent (legacy for health check)"""
    agents = list(project_client.agents.list_agents())
    if not agents:
        raise HTTPException(status_code=404, detail="No agents found")

    for agent in agents:
        if "lucy" in agent.name.lower():
            return agent

    return agents[0]  # Return first agent if no lucy found

# MCP Tools Initialization
async def init_mcp_tools():
    """Initialize MCP tools for agent-lucy"""
    if not MCP_AVAILABLE:
        return {"status": "unavailable", "message": "MCP not installed"}

    tools_status = {}

    # GitHub MCP Tool - Official Docker version
    try:
        # Try multiple environment variable names
        github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN") or os.getenv("GITHUB_API_KEN") or os.getenv("GITHUB_TOKEN")
        if github_token:
            github_tool = MCPStdioTool(
                name="github",
                command="docker",
                args=[
                    "run", "-i", "--rm",
                    "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",  # 傳遞環境變數到 Docker 容器
                    "ghcr.io/github/github-mcp-server"
                ],
                env={"GITHUB_PERSONAL_ACCESS_TOKEN": github_token},  # 官方版支持 GITHUB_PERSONAL_ACCESS_TOKEN
                description="Official GitHub MCP Server - Full GitHub API access with authentication",
            )
            mcp_tools["github"] = github_tool
            tools_status["github"] = "configured"
        else:
            tools_status["github"] = "missing_token"
    except Exception as e:
        tools_status["github"] = f"error: {str(e)}"

    # Filesystem MCP Tool (限制在 uploads 目錄)
    try:
        upload_dir = Path("/tmp/agent-lucy-uploads")
        upload_dir.mkdir(exist_ok=True)

        filesystem_tool = MCPStdioTool(
            name="filesystem",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", str(upload_dir)],
            description="File system operations for uploaded files",
        )
        mcp_tools["filesystem"] = filesystem_tool
        tools_status["filesystem"] = "configured"
    except Exception as e:
        tools_status["filesystem"] = f"error: {str(e)}"

    # Memory MCP Tool
    try:
        memory_tool = MCPStdioTool(
            name="memory",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-memory"],
            description="Knowledge graph-based persistent memory",
        )
        mcp_tools["memory"] = memory_tool
        tools_status["memory"] = "configured"
    except Exception as e:
        tools_status["memory"] = f"error: {str(e)}"

    return {
        "status": "initialized",
        "mcp_available": MCP_AVAILABLE,
        "tools": tools_status
    }

async def get_mcp_tools_list():
    """Get list of available MCP tools and their functions"""
    if not MCP_AVAILABLE or not mcp_tools:
        return []

    tools_info = []
    for tool_name, tool_instance in mcp_tools.items():
        try:
            # Connect to tool to get functions list
            if not tool_instance.is_connected:
                await tool_instance.connect()

            functions = [
                {
                    "name": func.name,
                    "description": func.description,
                }
                for func in tool_instance.functions
            ]

            tools_info.append({
                "tool": tool_name,
                "description": tool_instance.description,
                "functions": functions,
            })
        except Exception as e:
            tools_info.append({
                "tool": tool_name,
                "error": str(e)
            })

    return tools_info

async def convert_mcp_to_openai_functions():
    """Convert MCP tools to OpenAI function calling format"""
    if not MCP_AVAILABLE or not mcp_tools:
        # Initialize MCP tools if not already done
        await init_mcp_tools()

    if not mcp_tools:
        return []

    functions = []
    for tool_name, tool_instance in mcp_tools.items():
        if tool_instance and hasattr(tool_instance, 'is_connected'):
            try:
                if not tool_instance.is_connected:
                    await tool_instance.connect()

                # 將 MCP tool 的 functions 轉換為 OpenAI format
                for func in tool_instance.functions:
                    # Get parameters - might be a property or method
                    params = func.parameters if not callable(func.parameters) else func.parameters()
                    functions.append({
                        "type": "function",
                        "function": {
                            "name": f"{tool_name}_{func.name}",
                            "description": str(func.description) if func.description else "",
                            "parameters": params if params else {}
                        }
                    })
            except Exception as e:
                print(f"WARNING: Failed to convert MCP tool {tool_name}: {e}")

    return functions

# API Endpoints

@app.get("/")
async def root():
    """Serve the main HTML page"""
    html_file = Path(__file__).parent.parent / "public" / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return {"message": "Agent Lucy API is running", "docs": "/docs"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        agent = get_agent()
        return {
            "status": "healthy",
            "agent": agent.name,
            "model": agent.model,
            "mcp_available": MCP_AVAILABLE,
            "mcp_tools_count": len(mcp_tools)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.post("/api/mcp/init")
async def initialize_mcp_tools():
    """Initialize MCP tools"""
    result = await init_mcp_tools()
    return result

@app.get("/api/mcp/tools")
async def list_mcp_tools():
    """List available MCP tools and their functions"""
    tools = await get_mcp_tools_list()
    return {
        "mcp_available": MCP_AVAILABLE,
        "tools": tools
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to agent-lucy using Azure OpenAI"""
    try:
        if not AZURE_OPENAI_AVAILABLE or azure_openai_client is None:
            raise HTTPException(status_code=500, detail="Azure OpenAI not available")

        user_id = request.user_id

        # Initialize conversation if needed
        if user_id not in conversations:
            conversations[user_id] = []

        # Add user message to history
        user_msg = ChatMessage(
            role="user",
            content=request.message,
            timestamp=datetime.now().isoformat()
        )
        conversations[user_id].append(user_msg)

        print(f"INFO: Processing message: {request.message[:100]}...")

        # Prepare messages for Azure OpenAI
        messages = [
            {"role": "system", "content": """You are Lucy, a helpful AI assistant powered by Azure AI Foundry.

You can help with various tasks including:
- 🐙 **GitHub Operations**: Query user info, repositories, files, Issues, PRs via GitHub MCP tool
- 📁 **File Management**: Manage files in the uploads directory
- 💭 **Memory**: Remember information across conversations

**Response Formatting Guidelines**:
1. Use clear Markdown formatting with headers, lists, and emphasis
2. When showing GitHub user info, use this format:
   ```
   ## 👤 GitHub User Profile

   **Username**: [username]
   **Name**: [display name]
   **Email**: [email]
   **Company**: [company]
   **Location**: [location]

   ### 📊 Statistics
   - Public Repos: [count]
   - Private Repos: [count]
   - Followers: [count]
   - Following: [count]

   ### 🔗 Links
   - Profile: [github url]
   - Blog: [blog url]
   ```

3. When listing repositories, use numbered lists with key info:
   ```
   ## 📦 Repositories

   1. **[repo-name]** ⭐ [stars]
      - Description: [desc]
      - Language: [lang]
      - 🔗 [url]
   ```

4. Use emojis sparingly to enhance readability
5. Keep responses concise but well-structured

Always be friendly, helpful, and professional."""}
        ]

        # Add conversation history (last 10 messages)
        for msg in conversations[user_id][-10:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # 獲取 MCP 工具作為 OpenAI functions
        tools = await convert_mcp_to_openai_functions()

        # Call Azure OpenAI with tools
        response = await azure_openai_client.chat.completions.create(
            model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4"),
            messages=messages,
            tools=tools if tools else None,  # 添加工具支持
            temperature=0.7,
            max_tokens=800
        )

        # 處理工具調用
        response_message = response.choices[0].message

        if response_message.tool_calls:
            # 執行工具調用
            import json as json_module
            messages.append({
                "role": "assistant",
                "content": response_message.content or "",
                "tool_calls": [
                    {
                        "id": str(tc.id),
                        "type": str(tc.type) if tc.type else "function",
                        "function": {"name": str(tc.function.name), "arguments": str(tc.function.arguments)}
                    }
                    for tc in response_message.tool_calls
                ]
            })

            for tool_call in response_message.tool_calls:
                # 解析工具名稱 (format: "tool_name_function_name")
                tool_parts = tool_call.function.name.split("_", 1)
                tool_name = tool_parts[0]
                function_name = tool_parts[1] if len(tool_parts) > 1 else tool_call.function.name

                print(f"INFO: Calling MCP tool: {tool_name}.{function_name}")

                # 調用 MCP 工具
                tool_instance = mcp_tools.get(tool_name)
                if tool_instance:
                    import json
                    args = json.loads(tool_call.function.arguments)
                    result = await tool_instance.call_tool(function_name, **args)

                    # 處理結果：從 TextContent 提取文本
                    if result and len(result) > 0:
                        # result 是 list[Content]，提取文本
                        result_text = ""
                        for item in result:
                            if hasattr(item, 'text'):
                                result_text += str(item.text)
                            elif hasattr(item, 'content'):
                                result_text += str(item.content)
                            else:
                                result_text += str(item)
                    else:
                        result_text = "No result"

                    # 添加工具結果到消息歷史
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": result_text
                    })

            # 再次調用 LLM 處理工具結果
            second_response = await azure_openai_client.chat.completions.create(
                model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4"),
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )

            response_text = second_response.choices[0].message.content
        else:
            response_text = response_message.content

        thread_id = f"thread_{int(datetime.now().timestamp())}"

        print(f"INFO: Got response: {response_text[:100] if response_text else '(empty)'}...")

        # Add assistant response to history
        assistant_msg = ChatMessage(
            role="assistant",
            content=response_text,
            timestamp=datetime.now().isoformat()
        )
        conversations[user_id].append(assistant_msg)

        return ChatResponse(
            response=response_text,
            thread_id=thread_id,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        print(f"ERROR: Chat failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/api/conversations/{user_id}")
async def get_conversation_history(user_id: str):
    """Get conversation history for a user"""
    if user_id not in conversations:
        return {"user_id": user_id, "messages": []}

    return {
        "user_id": user_id,
        "messages": [msg.dict() for msg in conversations[user_id]]
    }

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), user_id: str = "default"):
    """Upload a file for the agent to analyze"""
    try:
        # Save file temporarily
        upload_dir = Path("/tmp/agent-lucy-uploads")
        upload_dir.mkdir(exist_ok=True)

        file_path = upload_dir / file.filename
        content = await file.read()

        with open(file_path, "wb") as f:
            f.write(content)

        return {
            "filename": file.filename,
            "size": len(content),
            "message": "File uploaded successfully. You can now ask questions about it."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    active_connections[user_id] = websocket

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Process message
            try:
                agent = get_agent()

                # Send typing indicator
                await websocket.send_json({"type": "typing", "typing": True})

                # Simulate processing (replace with actual agent call)
                await asyncio.sleep(1)
                response_text = f"[WebSocket] I received: {message_data.get('message')}"

                # Send response
                await websocket.send_json({
                    "type": "message",
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.now().isoformat()
                })

            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "error": str(e)
                })

    except WebSocketDisconnect:
        if user_id in active_connections:
            del active_connections[user_id]

# Mount static files
static_path = Path(__file__).parent.parent / "public"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
