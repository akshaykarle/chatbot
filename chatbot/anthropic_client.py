import os
from typing import List, Dict, Optional, Any
import anthropic
from dotenv import load_dotenv

load_dotenv()

class AnthropicClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-opus-20240229"  # You can change this to other models

    def send_message(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        media: Optional[List[Dict[str, Any]]] = None
    ) -> Dict:
        """
        Send a message to Anthropic's Claude and get a response.

        Args:
            messages: List of message objects with role and content
            system_prompt: Optional system prompt to set context
            media: Optional list of media objects for image uploads

        Returns:
            The complete response from Claude
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4000,
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        if media:
            # Add media to the last user message
            for i in reversed(range(len(messages))):
                if messages[i]["role"] == "user":
                    # Create a copy of the message to avoid modifying the original
                    messages[i] = messages[i].copy()

                    # Convert content to list format if it's a string
                    if isinstance(messages[i].get("content", ""), str):
                        text_content = messages[i].get("content", "")
                        messages[i]["content"] = [
                            {
                                "type": "text",
                                "text": text_content
                            }
                        ]
                    # If it's already a list, make sure we don't modify it in place
                    elif isinstance(messages[i].get("content", []), list):
                        messages[i]["content"] = messages[i]["content"].copy()
                    else:
                        messages[i]["content"] = []

                    # Add the media content
                    for m in media:
                        messages[i]["content"].append(m)
                    break

        response = self.client.messages.create(**kwargs)
        return response
