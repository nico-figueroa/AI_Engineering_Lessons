import json
import os

def lookup_contact(contact_name):
    """Looks up team member or contact information from the team directory."""
    try:
        # Create file path for team directory
        file_path = os.path.join(os.path.dirname(__file__), "..", "content", "team_directory.json")
        
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
        "description": "Looks up information about team members and key contacts from the team directory. Use this to get contact details and role information.",
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