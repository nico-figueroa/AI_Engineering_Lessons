import json

def search_help_center(query):
    """
    Search the company help center for FAQs.
    """
    ## YOUR SOLUTION HERE ##
    with open("data/help_center_faq.json", "r") as f:
        faq_data = json.load(f)
    
    if query in faq_data:
        return faq_data[query]
    else:
        return f"Sorry, I don't have information about '{query}' in our help center yet. Please contact support for assistance."

# Tool definition with explicit FAQ topics listed
retrieval_tool_definition = {
    "type": "function",
    "function": {
        "name": "search_help_center",
      ## YOUR SOLUTION HERE ##
        "description": "Search the company help center FAQ database for customer support information. Use this function by passing a single search topic as a string to the query parameter, for example search_help_center('refund policy'). Available topics include refund policy, shipping time, reset password, cancel subscription, track order, contact support, product warranty, and size guide. The function returns the corresponding FAQ answer for the selected topic. If a customer's question is not covered by one of these FAQ topics, do not call this function with an unsupported value; instead, inform the customer that the information is not available in the help center and recommend contacting support for further assistance.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search terms related to one of the available topics",
                    "enum": [
                        "refund policy",
                        "shipping time", 
                        "reset password",
                        "cancel subscription",
                        "track order",
                        "contact support",
                        "product warranty",
                        "size guide"
                    ]
                }
            },
            "required": ["query"]
        }
    }
}