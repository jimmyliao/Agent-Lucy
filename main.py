# Before running the sample:
#    pip install --pre azure-ai-projects>=2.0.0b1
#    pip install azure-identity

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Load environment variables
load_dotenv()

myEndpoint = os.getenv("AZURE_EXISTING_AIPROJECT_ENDPOINT")

project_client = AIProjectClient(
    endpoint=myEndpoint,
    credential=DefaultAzureCredential(),
)

# List all available agents
print("Listing available agents...")
agents_list = list(project_client.agents.list_agents())

if not agents_list:
    print("No agents found in the project.")
    exit(1)

print(f"Found {len(agents_list)} agent(s):")
myAgent = None
for agent in agents_list:
    print(f"  - Agent ID: {agent.id}, Name: {agent.name}")
    if myAgent is None and ("lucy" in agent.name.lower() or "lucy" in str(agent.id).lower()):
        myAgent = agent.id
        print(f"\n✓ Using agent: {agent.name} (ID: {agent.id})")

if myAgent is None:
    myAgent = agents_list[0].id
    print(f"\n⚠ No 'lucy' agent found. Using first agent: {agents_list[0].name} (ID: {myAgent})")

# Get the agent details
agent = project_client.agents.get_agent(agent_id=myAgent)
print(f"\n✓ Retrieved agent: {agent.name} (ID: {agent.id})")

# Send a message and get a response
print("\n📝 Sending message to agent...")
user_message = "Tell me what you can help with."
print(f"   User: {user_message}")

print(f"\n🤖 Running agent and waiting for response...")

# Use create_thread_and_process_run - this handles everything automatically
messages = project_client.agents.create_thread_and_process_run(
    agent_id=myAgent,
    thread={
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ]
    }
)

# Display the response
print("\n💬 Agent response:")
print("=" * 60)

# messages might be a list of messages or just the response content
if isinstance(messages, list):
    for message in messages:
        if hasattr(message, 'role') and message.role == "assistant":
            for content in message.content:
                if hasattr(content, 'text'):
                    print(f"{content.text.value}")
        elif isinstance(message, str):
            print(message)
else:
    print(messages)

print("=" * 60)
