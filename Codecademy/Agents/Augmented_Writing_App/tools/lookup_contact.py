import json
import os

def lookup_contact(contact_name):
    """Looks up team member or contact information from the team directory."""
    try:
        # Create file path for team directory
        file_path = os.path.join(os.path.dirname(__file__), "..", "content", "team_directory.json") # Task 7 (from here to line 37)
        
        if not os.path.exists(file_path):
            return {"status": "error", "message": "Team directory not found"}
        
        # Load team data
        with open(file_path, 'r') as f:
            contacts = json.load(f)
        
        # Search for contact (case-insensitive)
        contact_info = None
        for name, description in contacts.items():
            if name.lower() == contact_name.lower():
                contact_info = description
                break
        
        if contact_info:
            return {
                "status": "success",
                "contact": contact_name,
                "description": contact_info
            }
        else:
            # Show available contacts if not found
            available = list(contacts.keys())
            return {
                "status": "not_found",
                "message": f"Contact '{contact_name}' not found",
                "available_contacts": available
            }
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to lookup contact: {str(e)}"}

lookup_contact_tool_definition = {
    "type": "function",
    "function": {
        "name": "lookup_contact",
        "description": """Looks up information about team members, department contacts, 
        and organizational roles from the company directory. Use this tool whenever a 
        section being created, revised, or reviewed depends on knowledge of a specific 
        person, team, title, department, or role. Pass the referenced person's name or 
        role as the argument. If the user mentions a company employee, contact, team, 
        or position that is unknown, ambiguous, or not explicitly provided in the current 
        context, use this tool to retrieve accurate information before proceeding. Do not 
        guess contact details, responsibilities, reporting relationships, or role information 
        when this tool can provide authoritative data.""", # Task 10
        "parameters": {
            "type": "object",
            "properties": {
                "contact_name": {
                    "type": "string",
                    "description": "The name of the person to look up (e.g., 'Sarah Chen', 'IT Support', 'HR Director')"
                }
            },
            "required": ["contact_name"],
            "additionalProperties": False
        }
    },
    "strict": True
} 