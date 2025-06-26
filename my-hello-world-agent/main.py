from langgraph_sdk import get_sync_client

# Connect to your local server
client = get_sync_client(url="http://localhost:2024")

# Send a message to your hello world agent
for chunk in client.runs.stream(
    None,  # Threadless run
    "agent",  # Name defined in langgraph.json
    input={
        "messages": [{
            "role": "human", 
            "content": "what is the capital of France?"
        }]
    },
    stream_mode="messages-tuple"
):
    print(f"Receiving new event of type: {chunk.event}...")
    print(chunk.data)
    print("\n")
