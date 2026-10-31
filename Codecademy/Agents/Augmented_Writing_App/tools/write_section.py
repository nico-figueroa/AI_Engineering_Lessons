import os

def write_section(section_number, content):
    """Writes content to a training manual section file in the content folder."""
    try:
        # Create file path
        file_path = os.path.join(os.path.dirname(__file__), "..", "content", f"section_{section_number}.txt")
        
        # Create content directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return {
            "status": "success", 
            "message": f"Training section {section_number} saved successfully",
            "filename": f"section_{section_number}.txt",
            "length": len(content)
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to write section: {str(e)}"}

write_section_tool_definition = {
    "type": "function",
    "function": {
        "name": "write_section",
        "description": "Writes or revises the content of a training manual section. Use this to save new sections or update existing training documentation.",
        "parameters": {
            "type": "object",
            "properties": {
                "section_number": {
                    "type": "integer",
                    "description": "The section number (e.g., 1, 2, 3)"
                },
                "content": {
                    "type": "string",
                    "description": "The complete section content to write"
                }
            },
            "required": ["section_number", "content"],
            "additionalProperties": False
        }
    },
    "strict": True
} 