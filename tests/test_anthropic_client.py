import pytest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chatbot.anthropic_client import AnthropicClient

@pytest.fixture
def mock_anthropic_response():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="This is a test response from Claude.")]
    return mock_response

def test_anthropic_client_initialization():
    # Test with explicit API key
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': ''}):
        client = AnthropicClient(api_key="test_key")
        assert client.api_key == "test_key"
    
    # Test with environment variable
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'env_key'}):
        client = AnthropicClient()
        assert client.api_key == "env_key"
    
    # Test with missing API key
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': ''}):
        with pytest.raises(ValueError):
            AnthropicClient()

def test_send_message(mock_anthropic_response):
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
        client = AnthropicClient()
        
        # Mock the Anthropic client's create method
        client.client.messages.create = MagicMock(return_value=mock_anthropic_response)
        
        # Test sending a simple message
        messages = [{"role": "user", "content": "Hello, Claude!"}]
        response = client.send_message(messages)
        
        # Verify the response
        assert response.content[0].text == "This is a test response from Claude."
        
        # Verify the client was called with correct parameters
        client.client.messages.create.assert_called_once()
        call_args = client.client.messages.create.call_args[1]
        assert call_args["model"] == client.model
        assert call_args["messages"] == messages
        assert call_args["max_tokens"] == 4000

def test_send_message_with_system_prompt(mock_anthropic_response):
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'}):
        client = AnthropicClient()
        client.client.messages.create = MagicMock(return_value=mock_anthropic_response)
        
        messages = [{"role": "user", "content": "Hello"}]
        system_prompt = "You are a helpful assistant."
        
        response = client.send_message(messages, system_prompt=system_prompt)
        
        call_args = client.client.messages.create.call_args[1]
        assert call_args["system"] == system_prompt
