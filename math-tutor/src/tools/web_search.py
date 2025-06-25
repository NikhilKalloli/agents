from exa_py import Exa
import json
import os
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from agents import function_tool
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

# Initialize Exa API key
EXA_API_KEY = os.getenv("EXA_API_KEY")

async def exa_search_async(queries: List[str]) -> Dict:
    """Use Deep Exa search engine for getting latest information from the web.
    
    Args:
        queries (List[str]): A list of queries that need to be searched.
    
    Returns:
        Dict: A structured response with query results and metadata.
    """
    try:
        start_time = time.time()
        
        # Initialize Exa client
        exa = Exa(api_key=EXA_API_KEY)
        
        # Create a list to store all search tasks
        search_tasks = []
        
        # Create a ThreadPoolExecutor for parallel requests
        with ThreadPoolExecutor() as executor:
            # Create a future for each query
            loop = asyncio.get_event_loop()
            for query in queries:
                # Submit the search task to the executor
                task = loop.run_in_executor(
                    executor,
                    lambda q=query: exa.search_and_contents(
                        q,
                        text=True,
                        num_results=3,  # Top 3 results for each query
                        use_autoprompt=True
                    )
                )
                search_tasks.append((query, task))
            
            # Wait for all tasks to complete
            results = {}
            for query, task in search_tasks:
                try:
                    search_result = await task
                    
                    # Process the search results
                    content = []
                    citations = []
                    
                    if hasattr(search_result, 'results') and search_result.results:
                        for result in search_result.results:
                            if hasattr(result, 'title') and hasattr(result, 'url'):
                                content_text = result.text[:1500] if hasattr(result, 'text') and result.text else "No content available"
                                
                                content.append({
                                    "title": result.title,
                                    "content": content_text,
                                    "url": result.url
                                })
                                
                                citations.append({
                                    "title": result.title,
                                    "url": result.url
                                })
                    
                    # Store processed results for this query
                    results[query] = {
                        "summary": f"Found information about '{query}' from {len(content)} sources.",
                        "search_results": content,
                        "citations": citations,
                        "result_count": len(content)
                    }
                except Exception as e:
                    # Handle individual query failures
                    results[query] = {
                        "error": f"Search failed for query '{query}': {str(e)}",
                        "search_results": [],
                        "citations": [],
                        "result_count": 0
                    }
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Create a structured response
        response = {
            "status": "success",
            "metadata": {
                "query_count": len(queries),
                "execution_time_seconds": round(execution_time, 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "results": results
        }
        
        return response
        
    except Exception as e:
        error_response = {
            "status": "error",
            "error": f"Exa search failed: {str(e)}",
            "queries": queries,
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        return error_response

@function_tool
async def web_search(queries: List[str]) -> Dict:
    """
    Use Deep Exa search engine to find latest information from the web for JEE Integral Calculus problems.
    
    This tool is specifically designed to search for:
    - Advanced calculus concepts and techniques
    - JEE-level integral calculus problems and solutions
    - Mathematical theorems and their applications
    - Step-by-step solution methodologies
    - Related mathematical concepts and contexts
    
    Args:
        queries (List[str]): A list of search queries related to integral calculus, JEE problems, 
                           mathematical concepts, or solution techniques.
    
    Returns:
        Dict: A structured response containing search results, citations, and metadata.
    """
    if not queries:
        return {
            "status": "error",
            "error": "No search queries provided",
            "results": {}
        }
    
    # Add JEE and calculus context to queries for better results
    enhanced_queries = []
    for query in queries:
        if not any(keyword in query.lower() for keyword in ['jee', 'calculus', 'integral', 'mathematics']):
            enhanced_query = f"{query} JEE integral calculus mathematics"
        else:
            enhanced_query = query
        enhanced_queries.append(enhanced_query)
    
    return await exa_search_async(enhanced_queries)
