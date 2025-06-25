"""LangGraph chatbot with configurable LLM model.

A simple chatbot that can be configured with different LLM providers.
"""

from __future__ import annotations

from typing import Any, Dict, TypedDict, Annotated
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages


class Configuration(TypedDict):
    """Configurable parameters for the chatbot.

    Set these when creating assistants OR when invoking the graph.
    See: https://langchain-ai.github.io/langgraph/cloud/how-tos/configuration_cloud/
    """

    model_name: str  # e.g., "openai", "anthropic", "ollama"


class State(TypedDict):
    """The state of the chatbot conversation.

    Messages have the type "list". The `add_messages` function
    in the annotation defines how this state key should be updated
    (in this case, it appends messages to the list, rather than overwriting them)
    """

    messages: Annotated[list[BaseMessage], add_messages]


def _get_model(model_name: str):
    """Get the appropriate model based on configuration."""
    if model_name == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini")
    elif model_name == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model="claude-3-haiku-20240307")
    elif model_name == "ollama":
        from langchain_community.llms import Ollama
        return Ollama(model="llama2")
    else:
        # Default fallback
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model="gpt-4o-mini")
        except ImportError:
            raise ValueError(f"Unsupported model: {model_name}")


def chatbot(state: State, config: RunnableConfig) -> Dict[str, Any]:
    """Main chatbot node that processes messages and generates responses."""
    configuration = config["configurable"]
    model_name = configuration.get("model_name", "openai")
    
    # Get the configured model
    model = _get_model(model_name)
    
    # Get the current messages
    messages = state["messages"]
    
    # Generate response
    response = model.invoke(messages)
    
    # Return the response (will be added to messages list)
    return {"messages": [response]}


# Define the graph
graph = (
    StateGraph(State, config_schema=Configuration)
    .add_node("chatbot", chatbot)
    .add_edge(START, "chatbot")
    .compile(name="Chatbot")
)
