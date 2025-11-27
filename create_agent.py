#!/usr/bin/env python3
"""Create agent-lucy in Azure AI Foundry"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Load environment variables
load_dotenv()

# Project endpoint
endpoint = os.getenv("AZURE_EXISTING_AIPROJECT_ENDPOINT")

# Create client
print("Connecting to Azure AI Project...")
project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

# Create agent
print("Creating agent-lucy...")
agent = project_client.agents.create_agent(
    model="gpt-4o",  # Using GPT-4o model
    name="agent-lucy",
    instructions="You are Lucy, a helpful AI assistant. You help users with their questions and tasks in a friendly and professional manner.",
    description="Lucy - A helpful AI assistant"
)

print(f"\n✅ Agent created successfully!")
print(f"   Name: {agent.name}")
print(f"   ID: {agent.id}")
print(f"   Model: {agent.model}")
print(f"\n💡 You can now run 'python main.py' to interact with agent-lucy")
