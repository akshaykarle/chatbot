import streamlit as st
import os
import base64
from io import BytesIO
from typing import Dict, List, Optional, Any
import tempfile

# Use relative imports since we're inside the chatbot package
from chat_manager import ChatManager
from anthropic_client import AnthropicClient

# Initialize session state
if "chat_manager" not in st.session_state:
    st.session_state.chat_manager = ChatManager()

if "current_thread_id" not in st.session_state:
    # Get the first thread or create a new one
    threads = st.session_state.chat_manager.get_all_threads()
    if threads:
        st.session_state.current_thread_id = threads[0].thread_id
    else:
        thread = st.session_state.chat_manager.create_thread()
        st.session_state.current_thread_id = thread.thread_id

if "anthropic_client" not in st.session_state:
    st.session_state.anthropic_client = AnthropicClient()

# App title and description
st.title("Claude Chatbot")
st.subheader("Chat with Anthropic's Claude AI")

# Sidebar for thread management
with st.sidebar:
    st.header("Chat Threads")

    # Create new thread button
    if st.button("New Chat"):
        thread = st.session_state.chat_manager.create_thread()
        st.session_state.current_thread_id = thread.thread_id
        st.rerun()

    # List all threads
    threads = st.session_state.chat_manager.get_all_threads()
    for thread in threads:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(thread.title, key=f"thread_{thread.thread_id}", use_container_width=True):
                st.session_state.current_thread_id = thread.thread_id
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"delete_{thread.thread_id}"):
                st.session_state.chat_manager.delete_thread(thread.thread_id)
                if st.session_state.current_thread_id == thread.thread_id:
                    remaining_threads = st.session_state.chat_manager.get_all_threads()
                    if remaining_threads:
                        st.session_state.current_thread_id = remaining_threads[0].thread_id
                    else:
                        new_thread = st.session_state.chat_manager.create_thread()
                        st.session_state.current_thread_id = new_thread.thread_id
                st.rerun()

# Main chat area
current_thread = st.session_state.chat_manager.get_thread(st.session_state.current_thread_id)
if not current_thread:
    current_thread = st.session_state.chat_manager.create_thread()
    st.session_state.current_thread_id = current_thread.thread_id

# Display chat messages
for message in current_thread.messages:
    role = message["role"]
    content = message["content"]

    with st.chat_message(role):
        st.write(content)

        # Display any media if present
        if "media" in message:
            for media_item in message["media"]:
                if media_item.get("type") == "image":
                    st.image(media_item.get("data"))
                elif media_item.get("type") == "file":
                    st.download_button(
                        label=f"Download {media_item.get('filename')}",
                        data=media_item.get("data"),
                        file_name=media_item.get("filename")
                    )

# File uploader
uploaded_file = st.file_uploader("Upload an image or file", type=["jpg", "jpeg", "png", "pdf", "txt"])
uploaded_media = None

if uploaded_file:
    file_type = uploaded_file.type
    file_name = uploaded_file.name

    # Read file content
    file_bytes = uploaded_file.getvalue()

    if file_type.startswith("image/"):
        # Display the uploaded image
        st.image(file_bytes, caption=file_name)

        # Prepare media for Claude
        uploaded_media = [{
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": file_type,
                "data": base64.b64encode(file_bytes).decode("utf-8")
            }
        }]
    else:
        # For non-image files, just store the data
        st.write(f"File uploaded: {file_name}")
        uploaded_media = [{
            "type": "file",
            "filename": file_name,
            "data": file_bytes
        }]

# Input for new messages
prompt = st.chat_input("Type your message here...")

if prompt:
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
        if uploaded_media and uploaded_media[0].get("type") == "image":
            st.image(uploaded_file)

    # Add message to thread
    current_thread.add_message("user", prompt, uploaded_media)

    # Prepare messages for Anthropic API
    anthropic_messages = []
    for msg in current_thread.messages:
        if msg["role"] == "assistant":
            anthropic_messages.append({"role": "assistant", "content": msg["content"]})
        else:
            anthropic_messages.append({"role": "user", "content": msg["content"]})

    # Get media for the last message if it exists
    media_for_anthropic = None
    if uploaded_media and uploaded_media[0].get("type") == "image":
        media_for_anthropic = [uploaded_media[0]]  # Only send image media to Anthropic

    # Get response from Claude
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        try:
            response = st.session_state.anthropic_client.send_message(
                anthropic_messages,
                system_prompt="You are a helpful AI assistant. Respond thoughtfully to the user's questions and comments.",
                media=media_for_anthropic
            )

            assistant_response = response.content[0].text
            message_placeholder.write(assistant_response)

            # Add assistant response to thread
            current_thread.add_message("assistant", assistant_response)

            # Save updated thread
            st.session_state.chat_manager.save_threads()

        except Exception as e:
            message_placeholder.error(f"Error: {str(e)}")

# Save the chat history
st.session_state.chat_manager.save_threads()
