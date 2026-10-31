"""
Tool handler for the Training Manual Creator.

To add a new tool:
1. Create a new Python file in the tools directory with your function
2. Define the function and its tool_definition dictionary (following OpenAI's schema)
3. Import the function and tool_definition in this file
4. Add the function to FUNCTION_REGISTRY
5. Add the tool_definition to TOOLS list
"""
import json
from .write_section import write_section, write_section_tool_definition # Task 12
from .read_section import read_section, read_section_tool_definition
from .delete_section import delete_section, delete_section_tool_definition
from .lookup_contact import lookup_contact, lookup_contact_tool_definition # Task 13

# Function registry - add new functions here
FUNCTION_REGISTRY = {
    "write_section": write_section, # Task 12
    "read_section": read_section,
    "delete_section": delete_section,
    "lookup_contact": lookup_contact # Task 13
}

# Tool definitions - add new tool definitions here
TOOLS = [
    write_section_tool_definition, # Task 12
    read_section_tool_definition,
    delete_section_tool_definition,
    lookup_contact_tool_definition # Task 13
]


def process_tool_calls(response):
    """
    Extract function call details from the API response.
    """
    message = response.choices[0].message
    
    if not hasattr(message, "tool_calls") or not message.tool_calls:
        return None
    
    # Get the first tool call
    tool_call = message.tool_calls[0]
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    return {
        "id": tool_call.id,
        "function_name": function_name,
        "function_args": function_args
    }


def execute_function(function_name, function_args):
    """
    Execute a function from the registry with the given arguments.
    """
    if function_name in FUNCTION_REGISTRY:
        return FUNCTION_REGISTRY[function_name](**function_args)
    else:
        return {"error": f"Unknown function: {function_name}"}


def get_completion_with_tools(client, messages):
    """
    Get a completion from the model, handling tool calls if necessary.
    
    Args:
        client: OpenAI client instance
        messages: List of message dictionaries with role and content
        
    Returns:
        tuple: (response_content, updated_messages, tool_call_info)
    """
    # Step 1: Initial request with tools
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        tools=TOOLS # Task 14
    )
    
    # Step 2: Check for function calls
    tool_call = process_tool_calls(response)
    tool_call_info = None
    if not tool_call:
        # No tool call, return regular response
        return response.choices[0].message.content, messages + [{"role": "assistant", "content": response.choices[0].message.content}], tool_call_info
    
    # Step 3: Execute function
    function_name = tool_call["function_name"]
    function_args = tool_call["function_args"]
    result = execute_function(function_name, function_args)
    tool_call_info = {
        "id": tool_call["id"],
        "function_name": function_name,
        "function_args": function_args,
        "result": result
    }
    
    # Step 4: Build updated messages with tool call and result
    updated_messages = messages.copy()
    
    # Add the assistant's message with tool call
    assistant_message = response.choices[0].message
    updated_messages.append({
        "role": "assistant",
        "content": assistant_message.content,
        "tool_calls": [{
            "id": tool_call["id"],
            "type": "function",
            "function": {
                "name": function_name,
                "arguments": json.dumps(function_args)
            }
        }]
    })
    
    # Add the tool result
    updated_messages.append({
        "role": "tool",
        "tool_call_id": tool_call["id"],
        "content": json.dumps(result)
    })
    
    # Step 5: Get final response
    final_response = client.chat.completions.create(
        model="gpt-4.1",
        messages=updated_messages
    )
    
    final_content = final_response.choices[0].message.content
    updated_messages.append({"role": "assistant", "content": final_content})
    
    return final_content, updated_messages, tool_call_info 