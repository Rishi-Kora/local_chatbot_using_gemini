import streamlit as st
import os
import uuid
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="SoloChat", layout="wide")

# Initialize session state for chat history
if "chats" not in st.session_state:
    # Structure: {chat_id: {"title": "Title", "messages": []}}
    st.session_state.chats = {} 
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# Helper to create new chat
def create_new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": []
    }
    st.session_state.current_chat_id = chat_id

# Ensure at least one chat exists
if not st.session_state.current_chat_id:
    create_new_chat()

# Load API Key
api_key = os.getenv("GOOGLE_API_KEY")

# Load API Key
api_key = os.getenv("GOOGLE_API_KEY")

# Custom CSS for sidebar styling
st.markdown("""
<style>
    section[data-testid="stSidebar"] div[data-testid="stButton"] button {
        background-color: transparent;
        border: none;
        text-align: left;
        color: #ececf1;
        width: 100%;
        padding: 0.5rem;
        transition: background-color 0.2s;
        justify-content: flex-start;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
        background-color: #2A2B32;
        color: #ffffff;
        border: none;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:focus {
        background-color: #2A2B32;
        color: #ffffff;
        border: none;
        outline: none;
    }
    
    /* Hide the chevron arrow in the popover button */
    [data-testid="stPopover"] > div > button svg {
        display: none !important;
    }
    /* Align the text (⋮) properly since arrow is gone */
    [data-testid="stPopover"] > div > button {
        justify-content: center;
        padding: 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    # "New Chat" button slightly distinct or just at top
    if st.button("New Chat", key="new_chat_btn", use_container_width=True):
        create_new_chat()
        st.rerun()
    
    st.markdown('<div style="margin-top: 20px; color: #666; font-size: 0.8rem; margin-bottom: 10px;">Your chats</div>', unsafe_allow_html=True)
    
    # List chats (reverse order to show newest first if we tracked time, but simple dict iteration for now)
    # To delete chats, we'd need more UI, but for now just switching.
    chat_ids = list(st.session_state.chats.keys())

    for chat_id in reversed(chat_ids):
        chat_data = st.session_state.chats[chat_id]
        
        # Skip empty chats (like the one currently being created) to avoid "New Chat" in the list
        if not chat_data["messages"]:
            continue
            
        # Truncate title
        title = chat_data["title"]
        if len(title) > 20:
            title = title[:17] + "..."
            
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
             if st.button(title, key=f"chat_{chat_id}", use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.rerun()
        
        with col2:
            # Three-dot menu for actions
            with st.popover("⋮", use_container_width=True):
                if st.button("Delete", key=f"del_{chat_id}", use_container_width=True):
                    # Delete logic
                    del st.session_state.chats[chat_id]
                    # If deleted chat was active, switch to another or none
                    if st.session_state.current_chat_id == chat_id:
                        st.session_state.current_chat_id = None
                        # Optionally create a new chat immediately if none left, 
                        # but our generic logic at start handles that.
                    st.rerun()



# Main chat interface
st.title("SoloChat")

# Get current chat messages
current_chat = st.session_state.chats[st.session_state.current_chat_id]
current_messages = current_chat["messages"]

# Ensure API Key is available
if not api_key:
    st.warning("GOOGLE_API_KEY not found in environment variables. Please set it in your .env file.")
else:
    # Initialize Gemini Client if key exists
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing Client: {e}")

# Display chat messages for current session
for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything"):
    if not api_key:
        st.warning("Please set your Google API Key in the .env file to chat.")
    else:
        # Update title if it's the first message
        if len(current_messages) == 0:
            # Simple title generation: first 30 chars
            current_chat["title"] = prompt[:30] + ("..." if len(prompt) > 30 else "")
            
            # To refresh the sidebar title immediately would require a rerun, 
            # but that disrupts the flow. We'll update the state and it will show next run.
            # Or we can force rerun but the streaming might be lost? 
            # Streamlit is tricky here. Let's just update state.

        # Add user message to state and display
        current_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Prepare chat history for the model
                chat_history = []
                for msg in current_messages[:-1]: 
                     role = "user" if msg["role"] == "user" else "model"
                     chat_history.append(genai.types.Content(parts=[genai.types.Part(text=msg["content"])], role=role))
                
                chat = client.chats.create(
                    model="gemma-3-12b-it",
                    history=chat_history
                )
                
                response_stream = chat.send_message_stream(prompt)
                
                # Wait for first chunk inside spinner to show "Thinking..."
                with st.spinner("Thinking.."):
                    try:
                        first_chunk = next(response_stream)
                    except StopIteration:
                        first_chunk = None

                if first_chunk and first_chunk.text:
                    full_response += first_chunk.text
                    message_placeholder.markdown(full_response + "▌")

                # Stream the rest
                for chunk in response_stream:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
                current_messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
