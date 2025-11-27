#!/usr/bin/env python3
"""Simplest way to chat with agent-lucy"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

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
print("🤖 Getting agent...")
agents_list = list(project_client.agents.list_agents())
if not agents_list:
    print("❌ No agents found. Run 'python recreate_agent.py' first.")
    exit(1)

agent = agents_list[0]
print(f"✓ Agent: {agent.name} ({agent.model})\n")

# Chat
user_message = "Tell me what you can help with."
print(f"💬 You: {user_message}\n")
print("⏳ Lucy is thinking...\n")

# Use the process_run method which handles everything
try:
    # The simplest way - just use the OpenAI-compatible client
    with project_client.agents.get_agent_client() as agent_client:
        # Create thread
        thread = agent_client.beta.threads.create()

        # Send message
        agent_client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )

        # Run
        run = agent_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=agent.id
        )

        # Wait for completion
        import time
        while run.status in ["queued", "in_progress"]:
            time.sleep(1)
            run = agent_client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

        # Get response
        if run.status == "completed":
            messages = agent_client.beta.threads.messages.list(thread_id=thread.id)

            print("🤖 Lucy:")
            print("=" * 60)
            for message in reversed(list(messages)):
                if message.role == "assistant":
                    for content in message.content:
                        if content.type == "text":
                            print(content.text.value)
                    break
            print("=" * 60)
        else:
            print(f"❌ Failed: {run.status}")
            if hasattr(run, 'last_error') and run.last_error:
                print(f"   Error: {run.last_error}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
