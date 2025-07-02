# Hierarchical Agent Teams

This project implements a hierarchical multi-agent system with LangGraph, converted from the original Jupyter notebook format. The system consists of:

- **Research Team**: Search agent and web scraper
- **Document Writing Team**: Document writer, note taker, and chart generator  
- **Top-level Supervisor**: Orchestrates between teams

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

You need to set your API keys:

```bash
export OPENAI_API_KEY="your_openai_api_key"
export TAVILY_API_KEY="your_tavily_api_key"
```

Or the application will prompt you for them when you run it.

### 3. Optional: Enable LangSmith Tracing

For better debugging and monitoring:

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY="your_langchain_api_key"
export LANGCHAIN_PROJECT="hierarchical-agent-teams"
```

## Usage

### Running with LangGraph Dev

To run with `langgraph dev`:

```bash
langgraph dev
```

This will start the LangGraph development server and you can interact with your agent system.

### Running Directly

You can also run the script directly:

```bash
python app.py
```

## Architecture

The system has three layers:

1. **Individual Agents**: Each with specialized tools (search, web scraping, document writing, etc.)
2. **Team Supervisors**: Manage and coordinate agents within each team
3. **Top-level Supervisor**: Routes work between the research and writing teams

## API Keys Required

- **OpenAI**: For the LLM functionality
- **Tavily**: For web search capabilities

Get your keys from:
- OpenAI: https://platform.openai.com/api-keys
- Tavily: https://tavily.com/

## File Structure

- `app.py` - Main application with all agent logic
- `requirements.txt` - Python dependencies
- `config.py` - Configuration documentation
- `README.md` - This file

## Example Usage

The system can handle requests like:
- "Research AI agents and write a brief report about them"
- "Find information about climate change and create a summary document" 
- "Search for recent tech news and write an analysis with charts"

The top-level supervisor will automatically route to the appropriate teams based on the request.

## File Management

Generated documents are saved to the `./generated_files/` directory. You can:
- **List files**: Ask "What files have been created?" or "List all files"
- **Read files**: Ask "Read the contents of filename.txt"
- **Access files**: Find them in the `generated_files` folder in your project directory

The writing team has access to tools for creating outlines, writing documents, editing files, and generating charts. 