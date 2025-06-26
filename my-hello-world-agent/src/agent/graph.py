from typing import Annotated
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

# Define the state of our graph
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Create a simple hello world node
def hello_world_node(state: State):
    """A simple node that responds with Hello World"""
    messages = state["messages"]
    
    # Get the last human message
    last_message = messages[-1] if messages else None
    
    if isinstance(last_message, HumanMessage):
        # Create a simple hello world response
        response = AIMessage(content=f"Hello World! You said: '{last_message.content}'")
    else:
        response = AIMessage(content="Hello World! How can I help you today?")
    
    return {"messages": [response]}

# Build the graph
def create_graph():
    graph_builder = StateGraph(State)
    
    # Add our hello world node
    graph_builder.add_node("hello_world", hello_world_node)
    
    # Set the entry point and edges
    graph_builder.add_edge(START, "hello_world")
    graph_builder.add_edge("hello_world", END)
    
    return graph_builder.compile()

# Create the compiled graph
graph = create_graph()
