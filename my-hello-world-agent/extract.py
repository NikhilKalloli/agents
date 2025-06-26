import json
import csv
import sys

# Increase the recursion limit to handle deep schemas
sys.setrecursionlimit(2000)

def resolve_ref(data, ref):
    """
    Resolves a JSON reference string against the given data structure.
    Example: resolve_ref(data, '#/components/schemas/MySchema')
    """
    parts = ref.strip('#/').split('/')
    current = data
    for part in parts:
        if part in current:
            current = current[part]
        else:
            return {}  # Return empty object if ref is not found
    return current

def resolve_all_refs(node, data, visited_refs=None):
    """
    Recursively finds and resolves all '$ref' values in a JSON object,
    handling circular references.
    """
    if visited_refs is None:
        visited_refs = set()

    if isinstance(node, dict):
        if '$ref' in node:
            ref_path = node['$ref']
            if ref_path in visited_refs:
                return {"$ref": ref_path}  # Avoid circular recursion
            
            visited_refs.add(ref_path)
            resolved = resolve_ref(data, ref_path)
            result = resolve_all_refs(resolved, data, visited_refs)
            visited_refs.remove(ref_path)
            return result
        else:
            return {key: resolve_all_refs(value, data, visited_refs) for key, value in node.items()}
    elif isinstance(node, list):
        return [resolve_all_refs(item, data, visited_refs) for item in node]
    else:
        return node

def has_ref(node):
    """
    Recursively checks if a JSON object contains any '$ref' keys.
    """
    if isinstance(node, dict):
        if '$ref' in node:
            return True
        return any(has_ref(value) for value in node.values())
    elif isinstance(node, list):
        return any(has_ref(item) for item in node)
    else:
        return False

def extract_api_to_csv(json_file_path, csv_file_path):
    """
    Extracts API endpoint information from an OpenAPI JSON file and writes it to a CSV file.

    Args:
        json_file_path (str): The path to the input JSON file.
        csv_file_path (str): The path to the output CSV file.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error reading JSON file: {e}")
        return

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header. I've included the HTTP method as well for clarity.
        writer.writerow(['path', 'method', 'summary', 'tags', 'response_schema'])

        paths = data.get('paths', {})
        for path, path_item in paths.items():
            # Iterate over HTTP methods
            for method, operation in path_item.items():
                if isinstance(operation, dict):
                    summary = operation.get('summary', '')
                    # Tags is a list, join it into a string
                    tags = ', '.join(operation.get('tags', []))
                    
                    response_output = ''
                    # Check for success responses (200-299)
                    for status_code, response in operation.get('responses', {}).items():
                        if status_code.startswith('2'):
                            schema = None
                            content = response.get('content')
                            if content and 'application/json' in content:
                                schema = content['application/json'].get('schema')

                            # If schema exists and has a ref, resolve it
                            if schema and has_ref(schema):
                                try:
                                    resolved_schema = resolve_all_refs(schema, data)
                                    response_output = json.dumps(resolved_schema)
                                except RecursionError:
                                    response_output = json.dumps({"error": "Circular reference detected"})
                            # Otherwise, use the description of the response
                            else:
                                response_output = response.get('description', '')
                            
                            break  # Found a success response with a schema/description
                    
                    writer.writerow([path, method, summary, tags, response_output])

if __name__ == '__main__':
    extract_api_to_csv('api.json', 'api_endpoints.csv')
    print("Successfully extracted data to api_endpoints.csv") 