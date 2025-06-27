"""LangGraph chatbot with configurable LLM model.

A simple chatbot that can be configured with different LLM providers.
"""

from __future__ import annotations

from typing import Any, Dict, TypedDict, Annotated
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from agent.tools import api_tools


class Configuration(TypedDict):
    """Configurable parameters for the chatbot.

    Set these when creating assistants OR when invoking the graph.
    See: https://langchain-ai.github.io/langgraph/cloud/how-tos/configuration_cloud/
    """

    model_name: str  # e.g., "openai", "anthropic", "ollama"


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# Initialize the tool node with the API tools
tool_node = ToolNode(api_tools)

# Initialize the model
# We'll use OpenAI's function-calling capabilities
model = ChatOpenAI(model="gpt-4o-mini")

# Bind the tools to the model
model = model.bind_tools(api_tools)


# Define the function that determines whether to continue or not
def should_continue(state: AgentState) -> str:
    messages = state['messages']
    last_message = messages[-1]
    # If there are no tool calls, then we finish
    if not last_message.tool_calls:
        return "end"
    # Otherwise if there are tool calls, we call the tool node
    else:
        return "continue"


# Define the function that calls the model
def call_model(state: AgentState):
    messages = state['messages']
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


# Define a new graph
workflow = StateGraph(AgentState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these edges will take effect after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    # Finally we define a mapping.
    # The keys are strings, and the values are other nodes.
    # END is a special node marking that the graph should finish.
    # What will happen is we will call `should_continue`, and then the output of that
    # will be matched against the keys in this mapping.
    # Based on which one it is, that node will then be called.
    {
        # If `tools`, then we call the tool node.
        "continue": "action",
        # Otherwise we finish.
        "end": "__end__",
    },
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` will be called next.
workflow.add_edge("action", "__end__")

# Finally, we compile it!
# This workflow is now runnable
graph = workflow.compile()
