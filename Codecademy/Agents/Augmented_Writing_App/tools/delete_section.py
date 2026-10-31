import os

def delete_section(section_number):
    """Deletes a training manual section file from the content folder."""
    try:
        # Create file path
        file_path = os.path.join(os.path.dirname(__file__), "..", "content", f"section_{section_number}.txt")
        
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"Training section {section_number} not found"}
        
        # Delete the file
        os.remove(file_path)
            
        return {
            "status": "success", 
            "message": f"Training section {section_number} deleted successfully",
            "filename": f"section_{section_number}.txt"
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to delete section: {str(e)}"}

delete_section_tool_definition = {
    "type": "function",
    "function": {
        "name": "delete_section",
        "description": "Deletes a training manual section file. Use this to remove sections that are no longer needed.",
        "parameters": {
            "type": "object",
            "properties": {
                "section_number": {
                    "type": "integer",
                    "description": "The section number to delete (e.g., 1, 2, 3)"
                }
            },
            "required": ["section_number"],
            "additionalProperties": False
        }
    },
    "strict": True
} 