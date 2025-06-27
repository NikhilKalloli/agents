import csv
import json
from typing import List
from langchain_core.tools import Tool
import requests
from urllib.parse import urljoin
import re

# Base URL for the API. This should be configured more dynamically in a real-world scenario,
# for example, using environment variables.
BASE_URL = "http://localhost:2024" # A placeholder, the user should configure this.

def parse_api_endpoints(file_path: str) -> List[dict]:
    """Parses the API endpoints from a CSV file."""
    endpoints = []
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            endpoints.append(row)
    return endpoints

def make_api_call(path: str, method: str, path_params: dict = None, query_params: dict = None, body: dict = None) -> dict:
    """Makes an API call to the specified endpoint."""
    url = urljoin(BASE_URL, path.format(**(path_params or {})))
    
    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            params=query_params,
            json=body,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        if response.status_code == 204: # No content
             return {"status": "success", "message": "Operation successful."}
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def create_api_tools_from_csv(file_path: str) -> List[Tool]:
    """Dynamically creates LangChain tools from a CSV file of API endpoints."""
    endpoints = parse_api_endpoints(file_path)
    tools = []

    for endpoint in endpoints:
        path = endpoint["path"]
        method = endpoint["method"].lower()
        summary = endpoint["summary"]
        
        # Sanitize summary to create a valid function name
        tool_name = re.sub(r'[^a-zA-Z0-9_]', '', summary.replace(' ', '_')).lower()

        path_params = re.findall(r'\{(\w+)\}', path)

        def create_tool_func(p_path, p_method, p_path_params):
            def tool_func(*args, **kwargs):
                """The actual function that gets called when the tool is used."""
                # Separate path params from other args
                current_path_params = {p: kwargs.pop(p) for p in p_path_params if p in kwargs}
                
                # Remaining kwargs can be considered as body for post/patch/put or query for get/delete
                if p_method in ['post', 'patch', 'put']:
                    body = kwargs
                    query_params = None
                else:
                    body = None
                    query_params = kwargs

                return make_api_call(
                    path=p_path,
                    method=p_method,
                    path_params=current_path_params,
                    query_params=query_params,
                    body=body
                )
            return tool_func

        tool_function = create_tool_func(path, method, path_params)
        
        # Construct a docstring that the LLM can understand
        docstring = f"{summary}. "
        if path_params:
            docstring += f"Requires path parameters: {', '.join(path_params)}. "
        # We need a better way to describe the body/query params. 
        # For now, this is a placeholder.
        docstring += "Other arguments will be passed as the request body for POST/PATCH, or as query parameters for GET/DELETE."

        tool_function.__doc__ = docstring

        # Create the LangChain Tool
        new_tool = Tool(
            name=tool_name,
            func=tool_function,
            description=docstring
        )
        tools.append(new_tool)

    return tools

# Create tools from the provided CSV file
api_tools = create_api_tools_from_csv('api_endpoints.csv')

__all__ = ["api_tools"] 