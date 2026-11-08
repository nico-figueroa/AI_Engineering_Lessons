from openai import OpenAI
import streamlit as st
from tools.handler import get_completion_with_tools
import logging

logger = logging.getLogger(__name__)

st.title("The Oracle")
st.subheader("Ask me anything and I will provide answers or perform actions using my tools.")

# Initialize client - the API key and base URL are automatically configured
try:
    client = OpenAI()
except Exception:
    logger.error("Chat client initialization failed; exception details omitted.")
    st.error("The assistant is unavailable. Please contact the application operator.")
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Discard diagnostics retained by earlier versions of the app.
st.session_state.pop("tool_calls", None)

# Display chat history
for message in st.session_state.messages:
    if message["role"] not in ("user", "assistant") or message.get("tool_calls"):
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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
            assistant_reply, updated_messages, _ = get_completion_with_tools(client=client, messages=st.session_state.messages)
                
            # Display the reply
            st.markdown(assistant_reply)
            
            # Update chat history with the complete interaction
            # (This includes tool calls if any were made)
            st.session_state.messages = updated_messages
            
        except Exception:
            logger.error("Chat request failed; exception details omitted.")
            st.error("Unable to complete your request. Please try again later.")