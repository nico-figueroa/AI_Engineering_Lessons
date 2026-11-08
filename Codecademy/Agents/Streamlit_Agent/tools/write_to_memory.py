import json
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

def write_to_memory(memory):
    """Stores a memory string with timestamp in memories.json file."""
    try:
        file_path = "data/memories.json"
        # Load existing memories
        memories = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    ## YOUR SOLUTION HERE ##
                    memories = json.load(f)
                except json.JSONDecodeError:
                    # If file is empty or invalid JSON, start with empty list
                    memories = []
        
        # Create new memory entry
        memory_entry = {
            "time": datetime.now().isoformat(),
            "memory": memory
        }
        
        # Append new memory
        ## YOUR SOLUTION HERE ##
        memories.append(memory_entry)
        
        # Write back to file
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(memories, f, indent=2)
            
        return {"status": "success", "message": "Memory stored successfully"}
        
    except Exception:
        logger.error("Memory write failed; exception details omitted.")
        return {"status": "error", "message": "Failed to store memory. Please try again later."}

write_to_memory_tool_definition = {
    "type": "function",
    "function": {
        "name": "write_to_memory",
        "description": "Stores important information that should be remembered for future reference. Call this function if the user prompts you to rememmber something, or if you hear something that sounds like it will be useful for you as a helpful AI agent.",
        "parameters": {
            "type": "object",
            "properties": {
                "memory": {
                    "type": "string",
                    "description": "1-3 sentences describing the information to remember"
                }
            },
            "required": ["memory"],
            "additionalProperties": False
        }
    },
    "strict": True
}
