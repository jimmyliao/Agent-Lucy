#!/usr/bin/env python3
"""Simple chat with agent-lucy"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import time

# Load environment variables
load_dotenv()

# Project endpoint
endpoint = os.getenv("AZURE_EXISTING_AIPROJECT_ENDPOINT")

# Create client
print("🔌 Connecting to Azure AI Project...")
project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

# Get agent
print("🤖 Getting agent-lucy...")
agents_list = list(project_client.agents.list_agents())
if not agents_list:
    print("❌ No agents found. Please run 'python recreate_agent.py' first.")
    exit(1)

agent = agents_list[0]
print(f"✓ Found: {agent.name} (ID: {agent.id}, Model: {agent.model})")

# Create thread and run
user_message = "Tell me what you can help with."
print(f"\n💬 User: {user_message}")
print(f"⏳ Waiting for response...")

run = project_client.agents.create_thread_and_run(
    agent_id=agent.id,
    thread={
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ]
    }
)

print(f"   Thread: {run.thread_id}")
print(f"   Run: {run.id}")

# Poll for completion
while run.status in ["queued", "in_progress", "requires_action"]:
    time.sleep(1)
    # Get run status
    try:
        run_response = project_client.agents._client.runs.get(
            thread_id=run.thread_id,
            run_id=run.id
        )
        run = run_response
        print(f"   Status: {run.status}")
    except Exception as e:
        print(f"   Error checking status: {e}")
        break

print(f"✓ Status: {run.status}")

if run.status == "completed":
    # Get messages
    messages_response = project_client.agents._client.messages.list(thread_id=run.thread_id)
    messages_list = list(messages_response)

    print(f"\n🤖 Lucy:")
    print("-" * 60)
    for msg in reversed(messages_list):
        if msg.role == "assistant":
            for content in msg.content:
                if hasattr(content, 'text') and hasattr(content.text, 'value'):
                    print(content.text.value)
            break
    print("-" * 60)
else:
    print(f"❌ Run failed: {run.last_error if hasattr(run, 'last_error') else 'Unknown error'}")
