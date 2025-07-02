import os
import getpass
from typing import Annotated, List, Dict, Optional, Literal
from pathlib import Path

from langchain_community.document_loaders import WebBaseLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_experimental.utilities import PythonREPL
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent


def _set_if_undefined(var: str):
    """Set environment variable if not already defined."""
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"Please provide your {var}")


# Set up environment variables
_set_if_undefined("OPENAI_API_KEY")
_set_if_undefined("TAVILY_API_KEY")


# State definition
class State(MessagesState):
    next: str


# Global working directory for file operations  
# Create a persistent directory for generated files
WORKING_DIRECTORY = Path("./generated_files")
WORKING_DIRECTORY.mkdir(exist_ok=True)


# ================== TOOLS ==================

# Research team tools
tavily_tool = TavilySearchResults(max_results=5)


@tool
def scrape_webpages(urls: List[str]) -> str:
    """Use requests and bs4 to scrape the provided web pages for detailed information."""
    loader = WebBaseLoader(urls)
    docs = loader.load()
    return "\n\n".join(
        [
            f'<Document name="{doc.metadata.get("title", "")}">\n{doc.page_content}\n</Document>'
            for doc in docs
        ]
    )


# Document writing team tools
@tool
def create_outline(
    points: Annotated[List[str], "List of main points or sections."],
    file_name: Annotated[str, "File path to save the outline."],
) -> Annotated[str, "Path of the saved outline file."]:
    """Create and save an outline."""
    with (WORKING_DIRECTORY / file_name).open("w") as file:
        for i, point in enumerate(points):
            file.write(f"{i + 1}. {point}\n")
    return f"Outline saved to {file_name}"


@tool
def list_files() -> str:
    """List all files in the working directory."""
    files = list(WORKING_DIRECTORY.glob("*"))
    if not files:
        return "No files found in the working directory."
    
    file_list = []
    for file in files:
        if file.is_file():
            size = file.stat().st_size
            file_list.append(f"📄 {file.name} ({size} bytes)")
    
    return "Generated files:\n" + "\n".join(file_list)


@tool
def read_document(
    file_name: Annotated[str, "File path to read the document from."],
    start: Annotated[Optional[int], "The start line. Default is 0"] = None,
    end: Annotated[Optional[int], "The end line. Default is None"] = None,
) -> str:
    """Read the specified document."""
    with (WORKING_DIRECTORY / file_name).open("r") as file:
        lines = file.readlines()
    if start is None:
        start = 0
    return "\n".join(lines[start:end])


@tool
def write_document(
    content: Annotated[str, "Text content to be written into the document."],
    file_name: Annotated[str, "File path to save the document."],
) -> Annotated[str, "Path of the saved document file."]:
    """Create and save a text document."""
    with (WORKING_DIRECTORY / file_name).open("w") as file:
        file.write(content)
    return f"Document saved to {file_name}"


@tool
def edit_document(
    file_name: Annotated[str, "Path of the document to be edited."],
    inserts: Annotated[
        Dict[int, str],
        "Dictionary where key is the line number (1-indexed) and value is the text to be inserted at that line.",
    ],
) -> Annotated[str, "Path of the edited document file."]:
    """Edit a document by inserting text at specific line numbers."""
    with (WORKING_DIRECTORY / file_name).open("r") as file:
        lines = file.readlines()

    sorted_inserts = sorted(inserts.items())

    for line_number, text in sorted_inserts:
        if 1 <= line_number <= len(lines) + 1:
            lines.insert(line_number - 1, text + "\n")
        else:
            return f"Error: Line number {line_number} is out of range."

    with (WORKING_DIRECTORY / file_name).open("w") as file:
        file.writelines(lines)

    return f"Document edited and saved to {file_name}"


# Warning: This executes code locally, which can be unsafe when not sandboxed
repl = PythonREPL()


@tool
def python_repl_tool(
    code: Annotated[str, "The python code to execute to generate your chart."],
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    return f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"


# ================== HELPER UTILITIES ==================

def make_supervisor_node(llm: BaseChatModel, members: list[str]):
    """Create a supervisor node for managing team members."""
    options = ["FINISH"] + members
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        f" following workers: {members}. Given the following user request,"
        " respond with the worker to act next. Each worker will perform a"
        " task and respond with their results and status. When finished,"
        " respond with FINISH."
    )

    class Router(TypedDict):
        """Worker to route to next. If no workers needed, route to FINISH."""
        next: str

    def supervisor_node(state: State):
        """An LLM-based router."""
        # Ensure we have messages to work with
        if not state.get("messages"):
            return Command(goto=END, update={"next": "FINISH"})
            
        messages = [
            {"role": "system", "content": system_prompt},
        ] + state["messages"]
        response = llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]
        if goto == "FINISH":
            goto = END

        return Command(goto=goto, update={"next": goto})

    return supervisor_node





# ================== HIERARCHICAL GRAPH BUILDER ==================

def create_hierarchical_agent_teams():
    """Create and return the main hierarchical agent teams graph."""
    llm = ChatOpenAI(model="gpt-4o")

    # Create all individual agents
    search_agent = create_react_agent(llm, tools=[tavily_tool])
    web_scraper_agent = create_react_agent(llm, tools=[scrape_webpages])
    
    doc_writer_agent = create_react_agent(
        llm,
        tools=[write_document, edit_document, read_document, list_files],
        prompt=(
            "You can read, write and edit documents based on note-taker's outlines. "
            "Don't ask follow-up questions."
        ),
    )
    
    note_taking_agent = create_react_agent(
        llm,
        tools=[create_outline, read_document, list_files],
        prompt=(
            "You can read documents and create outlines for the document writer. "
            "Don't ask follow-up questions."
        ),
    )
    
    chart_generating_agent = create_react_agent(
        llm, tools=[read_document, python_repl_tool, list_files]
    )

    # Create research team nodes
    def search_node(state: State):
        if not state.get("messages"):
            return Command(goto="research_supervisor", update={})
        
        result = search_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="search")
                ]
            },
            goto="research_supervisor",
        )

    def web_scraper_node(state: State):
        if not state.get("messages"):
            return Command(goto="research_supervisor", update={})
            
        result = web_scraper_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="web_scraper")
                ]
            },
            goto="research_supervisor",
        )

    # Create writing team nodes
    def doc_writing_node(state: State):
        if not state.get("messages"):
            return Command(goto="writing_supervisor", update={})
            
        result = doc_writer_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="doc_writer")
                ]
            },
            goto="writing_supervisor",
        )

    def note_taking_node(state: State):
        if not state.get("messages"):
            return Command(goto="writing_supervisor", update={})
            
        result = note_taking_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result["messages"][-1].content, name="note_taker")
                ]
            },
            goto="writing_supervisor",
        )

    def chart_generating_node(state: State):
        if not state.get("messages"):
            return Command(goto="writing_supervisor", update={})
            
        result = chart_generating_agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content=result["messages"][-1].content, name="chart_generator"
                    )
                ]
            },
            goto="writing_supervisor",
        )

    # Create custom supervisor for research team
    def research_supervisor_node(state: State):
        options = ["FINISH", "search", "web_scraper"]
        system_prompt = (
            "You are a research team supervisor managing search and web_scraper workers. "
            "Given the user request, decide which worker should act next. "
            "When the research is complete, respond with FINISH."
        )
        
        class Router(TypedDict):
            next: str
        
        # Ensure we have messages to work with
        if not state.get("messages"):
            return Command(goto="supervisor", update={"next": "FINISH"})
            
        messages = [{"role": "system", "content": system_prompt}] + state["messages"]
        response = llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]
        
        if goto == "FINISH":
            goto = "supervisor"  # Return to main supervisor
            
        return Command(goto=goto, update={"next": goto})

    # Create custom supervisor for writing team  
    def writing_supervisor_node(state: State):
        options = ["FINISH", "doc_writer", "note_taker", "chart_generator"]
        system_prompt = (
            "You are a writing team supervisor managing doc_writer, note_taker, and chart_generator workers. "
            "Given the user request, decide which worker should act next. "
            "When the writing work is complete, respond with FINISH."
        )
        
        class Router(TypedDict):
            next: str
        
        # Ensure we have messages to work with
        if not state.get("messages"):
            return Command(goto="supervisor", update={"next": "FINISH"})
            
        messages = [{"role": "system", "content": system_prompt}] + state["messages"]
        response = llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]
        
        if goto == "FINISH":
            goto = "supervisor"  # Return to main supervisor
            
        return Command(goto=goto, update={"next": goto})
    
    # Create main supervisor
    main_supervisor_node = make_supervisor_node(llm, ["research_team", "writing_team"])

    # Team routing functions
    def route_to_research_team(state: State):
        return Command(goto="research_supervisor", update={})
    
    def route_to_writing_team(state: State):
        return Command(goto="writing_supervisor", update={})

    # Build the complete hierarchical graph
    builder = StateGraph(State)
    
    # Add main supervisor
    builder.add_node("supervisor", main_supervisor_node)
    
    # Add team routers
    builder.add_node("research_team", route_to_research_team)
    builder.add_node("writing_team", route_to_writing_team)
    
    # Add team supervisors
    builder.add_node("research_supervisor", research_supervisor_node)
    builder.add_node("writing_supervisor", writing_supervisor_node)
    
    # Add individual workers
    builder.add_node("search", search_node)
    builder.add_node("web_scraper", web_scraper_node)
    builder.add_node("doc_writer", doc_writing_node)
    builder.add_node("note_taker", note_taking_node)
    builder.add_node("chart_generator", chart_generating_node)
    
    # Add edges
    builder.add_edge(START, "supervisor")
    
    return builder.compile()


# Create the main graph instance
graph = create_hierarchical_agent_teams()


# ================== FOR LANGGRAPH DEV ==================

def main():
    """Main function for testing the hierarchical agent teams."""
    # Example usage
    result = graph.invoke({
        "messages": [("user", "Research AI agents and write a brief report about them.")]
    })
    return result


if __name__ == "__main__":
    main() 