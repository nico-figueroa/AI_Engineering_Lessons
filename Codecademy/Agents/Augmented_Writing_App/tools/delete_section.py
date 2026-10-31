import os

def delete_section(section_number):
    """Deletes a training manual section file from the content folder."""
    try:
        # Create file path
        file_path = os.path.join(os.path.dirname(__file__), "..", "content", f"section_{section_number}.txt")
        
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"Training section {section_number} not found"}
        
        # Delete the file
        os.remove(file_path) # Task 6
            
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
        "description": """Deletes a training manual section file. This is a destructive 
        action and should only be performed when the user explicitly and clearly requests 
        that a section be deleted, removed, discarded, or permanently eliminated. Never 
        infer deletion intent from comments that a section is outdated, incorrect, redundant, 
        unnecessary, or should be changed. If it appears that deletion may be appropriate but 
        the user has not directly instructed you to delete the section, ask for clarification 
        instead of calling the tool. Only invoke this tool when there is clear, unambiguous 
        user authorization to permanently remove the specified section.""", # Task 9
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