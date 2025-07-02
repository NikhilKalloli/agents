import os
import uuid
from typing import Annotated, Literal

from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, MemorySaver

# Load environment variables
load_dotenv()

# 1. Define the state for our graph
from typing import TypedDict


class State(TypedDict):
    messages: Annotated[list, add_messages]
    # thread_id is managed by the checkpointer
    metadata: dict


# 2. Define the tools for our agent
tavily_tool = TavilySearchResults(max_results=2)
tools = [tavily_tool]


# 3. Define the agent node and graph creation in a factory function
def create_assistant(model, system_prompt, tools, checkpointer):
    """
    Creates a new assistant with a given model, system_prompt, tools and a checkpointer.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    agent_model = model.bind_tools(tools)
    agent_runnable = prompt | agent_model

    def agent_node(state: State):
        """
        Invokes the agent with the current state to decide on the next action.
        """
        response = agent_runnable.invoke(state)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    def should_continue(state: State) -> Literal["tools", "__end__"]:
        """
        Determines the next step based on the last message.
        """
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "tools"
        return "__end__"

    # Define the graph
    workflow = StateGraph(State)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")

    return workflow.compile(checkpointer=checkpointer)


# 4. Create two different assistants with a memory saver
llm = ChatOpenAI(temperature=0, streaming=True)
checkpointer = MemorySaver()

# Assistant v1: Default assistant
assistant_v1 = create_assistant(
    llm,
    "You are a helpful assistant.",
    [tavily_tool],
    checkpointer,
)

# Assistant v2: Specialized assistant with a different personality
assistant_v2 = create_assistant(
    llm,
    "You are a sarcastic assistant who loves finding financial information but hates giving it away.",
    [tavily_tool],
    checkpointer,
) 