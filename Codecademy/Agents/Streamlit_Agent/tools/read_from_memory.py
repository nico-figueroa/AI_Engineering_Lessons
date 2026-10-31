import json
import os

def read_from_memory():
    """Returns all stored memories as a concatenated string."""
    try:
        file_path = "data/memories.json"
        
        # Load existing memories
        memories = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    memories = json.load(f)
                except json.JSONDecodeError:
                    return {"status": "error", "message": "Failed to parse memories file"}
        
        # If no memories exist
        if not memories:
            return {"status": "success", "memories": "No memories stored yet."}
            
        # Concatenate all memories with timestamps
        memory_strings = []
        for entry in memories:
            memory_strings.append(f"{entry['time']}: {entry['memory']}")
            
        all_memories = "\n".join(memory_strings)
        return {"status": "success", "memories": all_memories}
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to retrieve memories: {str(e)}"}

read_from_memory_tool_definition = {
    "type": "function",
    "function": {
        "name": "read_from_memory",
        "description": "Retrieves all stored memories and returns them as a concatenated string with timestamps.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "strict": True
}
