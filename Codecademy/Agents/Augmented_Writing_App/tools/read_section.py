import os

def read_section(section_number):
    """Reads a training manual section file from the content folder."""
    try:
        # Create file path
        file_path = os.path.join(os.path.dirname(__file__), "..", "content", f"section_{section_number}.txt")
        
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"Training section {section_number} not found"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return { # Task 5
            "status": "success", 
            "section_number": section_number,
            "content": content,
            "length": len(content)
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to read section: {str(e)}"}

read_section_tool_definition = {
    "type": "function",
    "function": {
        "name": "read_section",
        "description": """Reads the content of an existing training manual section. 
        Use this tool whenever you need to know what a section currently contains 
        before answering a question, making revisions, expanding content, summarizing 
        information, or determining whether changes are needed. Also use it when the 
        user asks to read, review, summarize, explain, or retrieve the contents of a 
        handbook section. When information about a section is required and its contents 
        are not already known, read the section rather than making assumptions about 
        what it contains.""", # Task 11
        "parameters": {
            "type": "object",
            "properties": {
                "section_number": {
                    "type": "integer",
                    "description": "The section number to read (e.g., 1, 2, 3)"
                }
            },
            "required": ["section_number"],
            "additionalProperties": False
        }
    },
    "strict": True
} 