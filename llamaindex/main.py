import asyncio
import os
from dotenv import load_dotenv
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Define a simple calculator tool
def multiply(a: float, b: float) -> float:
    """Useful for multiplying two numbers."""
    return a * b


async def main():
    # Check if OpenAI API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set your OpenAI API key in a .env file:")
        print("OPENAI_API_KEY=your-api-key-here")
        print("Or set it as an environment variable:")
        print("export OPENAI_API_KEY='your-api-key-here'  # On Linux/Mac")
        print("set OPENAI_API_KEY=your-api-key-here       # On Windows CMD")
        print("$env:OPENAI_API_KEY='your-api-key-here'    # On Windows PowerShell")
        return

    # Create an agent workflow with our calculator tool
    agent = FunctionAgent(
        tools=[multiply],
        llm=OpenAI(model="gpt-4o-mini", api_key=api_key),
        system_prompt="You are a helpful assistant that can multiply two numbers.",
    )

    try:
        # Run the agent
        response = await agent.run("What is 1234 * 4567?")
        print(str(response))
    except Exception as e:
        print(f"Error running agent: {e}")
        print("Please check your OpenAI API key and internet connection.")


# Run the agent
if __name__ == "__main__":
    asyncio.run(main())