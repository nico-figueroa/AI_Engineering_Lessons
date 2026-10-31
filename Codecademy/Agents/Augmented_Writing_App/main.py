from openai import OpenAI
import streamlit as st
from tools.handler import get_completion_with_tools
import json

st.title("Training Manual Creator")

# Initialize client
client = OpenAI()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize tool call storage separately
if "tool_calls" not in st.session_state:
    st.session_state.tool_calls = {}

# Display chat history
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Check if there's tool info for this message index
        if i in st.session_state.tool_calls:
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
if prompt := st.chat_input("Help me create training documentation..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        try:
            # Get completion with tool support
            assistant_reply, updated_messages, tool_call_info = get_completion_with_tools(
                client=client,
                messages=st.session_state.messages
            )
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
            
            # Filter updated_messages to only include user messages and final assistant responses
            # Exclude tool call messages and tool result messages
            filtered_messages = []
            for msg in updated_messages:
                if msg["role"] == "user":
                    filtered_messages.append(msg)
                elif msg["role"] == "assistant" and not msg.get("tool_calls"):
                    filtered_messages.append(msg)
                # Skip tool messages and assistant messages with tool_calls
            
            # Update chat history with filtered messages
            st.session_state.messages = filtered_messages
            
            # If there was a tool call, store it separately indexed by message position
            if tool_call_info:
                # Find the assistant message that corresponds to this tool call
                # It should be the last assistant message in filtered_messages
                for idx in range(len(st.session_state.messages) - 1, -1, -1):
                    if st.session_state.messages[idx]["role"] == "assistant":
                        st.session_state.tool_calls[idx] = tool_call_info
                        break
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            # Try to provide more details about the error
            if hasattr(e, 'response'):
                st.write("Response details:", e.response) 