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
    from agent_framework import ChatAgent, MCPStdioTool
    from agent_framework.azure import AzureAIAgentClient
    AGENT_FRAMEWORK_AVAILABLE = True
    MCP_AVAILABLE = True
except ImportError:
    AGENT_FRAMEWORK_AVAILABLE = False
    MCP_AVAILABLE = False
    ChatAgent = None
    AzureAIAgentClient = None
    MCPStdioTool = None

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

    # GitHub MCP Tool
    try:
        # Try multiple environment variable names
        github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN") or os.getenv("GITHUB_API_KEN") or os.getenv("GITHUB_TOKEN")
        if github_token:
            github_tool = MCPStdioTool(
                name="github",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={"GITHUB_PERSONAL_ACCESS_TOKEN": github_token},
                description="GitHub repository operations and file management",
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
- Accessing GitHub repositories
- Managing files in the uploads directory
- Remembering information across conversations
Always be friendly, helpful, and concise in your responses."""}
        ]

        # Add conversation history (last 10 messages)
        for msg in conversations[user_id][-10:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Call Azure OpenAI
        response = await azure_openai_client.chat.completions.create(
            model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4"),
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )

        response_text = response.choices[0].message.content
        thread_id = f"thread_{int(datetime.now().timestamp())}"

        print(f"INFO: Got response: {response_text[:100]}...")

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
