#!/usr/bin/env python3
"""Chat with agent-lucy using Microsoft Agent Framework"""

import os
from dotenv import load_dotenv
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential
import asyncio

async def main():
    print("🔌 Connecting to Azure AI...")

    # Load environment variables
    load_dotenv()

    # Create the Azure AI client with endpoint and deployment name
    endpoint = os.getenv("AZURE_EXISTING_AIPROJECT_ENDPOINT")
    client = AzureOpenAIResponsesClient(
        credential=DefaultAzureCredential(),
        endpoint=endpoint,
        deployment_name="gpt-4.1"  # The model we deployed
    )

    # Get existing agent by referencing it
    agent_name = "agent-lucy"
    print(f"🤖 Using agent: {agent_name}")

    # Create an agent reference (or create new one if needed)
    try:
        agent = client.create_agent(
            name=agent_name,
            instructions="You are Lucy, a helpful AI assistant. You help users with their questions and tasks in a friendly and professional manner."
        )
    except Exception as e:
        print(f"Note: {e}")
        print("Using existing agent...")
        agent = client.get_agent(agent_name)

    # Send a message
    user_message = "Tell me what you can help with."
    print(f"\n💬 You: {user_message}\n")
    print("⏳ Lucy is thinking...\n")

    # Get response
    response = await agent.run(user_message)

    print("🤖 Lucy:")
    print("=" * 60)
    print(response)
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
