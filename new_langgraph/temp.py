from langgraph.cloud import Client

client = Client(api_key="YOUR_KEY")

run = client.runs.get(run_id, expand="messages")
system_prompts = [m for m in run.messages if m.role == "system"]

for msg in system_prompts:
    print(msg.content)