#!/usr/bin/env python3
"""Direct test of agent interaction"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import time

# Load environment variables
load_dotenv()

endpoint = os.getenv("AZURE_EXISTING_AIPROJECT_ENDPOINT")

print("Connecting...")
client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Get agent
agents = list(client.agents.list_agents())
agent_id = agents[0].id
print(f"Using agent: {agents[0].name} ({agent_id})")

# Create thread and run
print("\nCreating thread and sending message...")
run = client.agents.create_thread_and_run(
    agent_id=agent_id,
    thread={"messages": [{"role": "user", "content": "Hello! Who are you?"}]}
)

print(f"Thread ID: {run.thread_id}")
print(f"Run ID: {run.id}")
print(f"Initial status: {run.status}")

# Simple wait (since we can't poll easily)
print("\nWaiting 5 seconds for completion...")
time.sleep(5)

# Try to list messages directly using the internal client
print("\nTrying to get messages...")
try:
    # Access the internal OpenAI-compatible client
    messages_result = client.agents._client.messages.list(thread_id=run.thread_id)
    messages = list(messages_result)

    print(f"\nFound {len(messages)} messages:")
    for msg in reversed(messages):
        print(f"\n[{msg.role.upper()}]")
        for content in msg.content:
            if hasattr(content, 'text'):
                print(content.text.value)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
