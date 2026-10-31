import os

def write_section(section_number, content):
    """Writes content to a training manual section file in the content folder."""
    try:
        # Create file path
        file_path = os.path.join(os.path.dirname(__file__), "..", "content", f"section_{section_number}.txt")
        
        # Create content directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content) # Task 4
            
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
        "description": """Writes or revises the content of a training manual section in the content folder. 
        Use this tool only when the user explicitly instructs you to create, update, revise, edit, rewrite, 
        expand, condense, or correct a training manual section. The tool expects the complete final content 
        of the section. For new sections, generate fully written training-manual content in a precise, professional, 
        instructional style. For revisions, rewrite the entire section and incorporate the requested changes while 
        preserving all content not affected by the revision. Keep all other sections and files exactly unchanged. 
        Never submit partial edits, diffs, commentary, explanations, placeholders, or summaries. Always provide 
        the complete final version of the section ready to be saved.""", # Task 8
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