import pytest
import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chatbot.chat_manager import ChatManager, ChatThread

@pytest.fixture
def temp_storage_path(tmp_path):
    return str(tmp_path / "test_chat_history.json")

def test_create_thread(temp_storage_path):
    manager = ChatManager(storage_path=temp_storage_path)
    thread = manager.create_thread(title="Test Thread")
    
    assert thread.thread_id in manager.threads
    assert thread.title == "Test Thread"
    assert os.path.exists(temp_storage_path)
    
    # Check if the thread was saved to storage
    with open(temp_storage_path, "r") as f:
        data = json.load(f)
        assert thread.thread_id in data
        assert data[thread.thread_id]["title"] == "Test Thread"

def test_add_message_to_thread():
    thread = ChatThread(title="Test Thread")
    
    # Add user message
    thread.add_message("user", "Hello, Claude!")
    assert len(thread.messages) == 1
    assert thread.messages[0]["role"] == "user"
    assert thread.messages[0]["content"] == "Hello, Claude!"
    
    # Add assistant message
    thread.add_message("assistant", "Hello! How can I help you today?")
    assert len(thread.messages) == 2
    assert thread.messages[1]["role"] == "assistant"

def test_delete_thread(temp_storage_path):
    manager = ChatManager(storage_path=temp_storage_path)
    thread = manager.create_thread(title="Test Thread")
    
    # Delete the thread
    result = manager.delete_thread(thread.thread_id)
    assert result is True
    assert thread.thread_id not in manager.threads
    
    # Try to delete a non-existent thread
    result = manager.delete_thread("non-existent-id")
    assert result is False

def test_thread_serialization():
    thread = ChatThread(title="Test Thread")
    thread.add_message("user", "Hello")
    thread.add_message("assistant", "Hi there")
    
    # Convert to dict
    thread_dict = thread.to_dict()
    
    # Create a new thread from the dict
    new_thread = ChatThread.from_dict(thread_dict)
    
    assert new_thread.thread_id == thread.thread_id
    assert new_thread.title == thread.title
    assert len(new_thread.messages) == 2
    assert new_thread.messages[0]["content"] == "Hello"
    assert new_thread.messages[1]["content"] == "Hi there"
