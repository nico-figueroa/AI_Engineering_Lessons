from openai import OpenAI
import streamlit as st
from tools.handler import get_completion_with_tools
import json

st.title("The Oracle")
st.subheader("Ask me anything and I will provide answers or perform actions using my tools.")

# Initialize client - the API key and base URL are automatically configured
client = OpenAI()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize tool call storage separately
## YOUR SOLUTION HERE ##
if "tool_calls" not in st.session_state:
    st.session_state.tool_calls = {}

# Display chat history
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Check if there's tool info for this message index
        if i in st.session_state.tool_calls:
            ## YOUR SOLUTION HERE ##
            tool_call_info = st.session_state.tool_calls[i]
            st.info(f"""
🔧 **Tool Executed:** `{tool_call_info['function_name']}`

**Input:**
```json
{json.dumps(tool_call_info['function_args'], indent=2)}
```

**Output:**
```json
{json.dumps(tool_call_info['result'], indent=2)}
```
""")

# Handle user input
if prompt := st.chat_input("Ask to roll a dice?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        try:
            # Get completion with tool support
            ## YOUR SOLUTION HERE ##
            assistant_reply, updated_messages, tool_call_info = get_completion_with_tools(client=client, messages=st.session_state.messages)
            if tool_call_info:
                st.info(f"""
🔧 **Tool Executed:** `{tool_call_info['function_name']}`

**Input:**
```json
{json.dumps(tool_call_info['function_args'], indent=2)}
```

**Output:**
```json
{json.dumps(tool_call_info['result'], indent=2)}
```
""")
                
            # Display the reply
            st.markdown(assistant_reply)
            
            # Update chat history with the complete interaction
            # (This includes tool calls if any were made)
            st.session_state.messages = updated_messages
            
            # If there was a tool call, store it separately indexed by message position
            if tool_call_info:
                # Find the assistant message that corresponds to this tool call
                # It should be the last assistant message in updated_messages
                for idx in range(len(st.session_state.messages) - 1, -1, -1):
                    if st.session_state.messages[idx]["role"] == "assistant":
                        st.session_state.tool_calls[idx] = tool_call_info
                        break
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            # Try to provide more details about the error
            response = getattr(e, 'response', None)
            if response is not None:
                st.write("Response details:", response)