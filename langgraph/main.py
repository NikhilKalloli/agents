from langgraph_sdk import get_sync_client

client = get_sync_client(url="http://127.0.0.1:2024")  # URL of your LangGraph Server

# 1️⃣ List assistants
assistants = client.assistants.search()
print("Assistants:")
for a in assistants:
    print(a["assistant_id"], a.get("name"), a["config"])  # type: ignore[index]
if not assistants:
    print("No assistants found. Create one via LangGraph Studio or SDK first.")

# 2️⃣ List threads
threads = client.threads.search()
print("\nThreads:")
for t in threads:
    print(t["thread_id"], t.get("metadata"))  # type: ignore[index]

# 3️⃣ List runs per thread
print("\nRuns (per thread):")
for t in threads:
    runs = client.runs.list(t["thread_id"])  # type: ignore[index]
    print(f"Thread {t['thread_id']} -> {len(runs)} runs")