# Streamlit Chatbot with Anthropic Integration

A simple chatbot application built with Streamlit that uses Anthropic's Claude AI. The app supports multiple chat threads and allows uploading images and files.

## Features

- Chat with Claude AI
- Multiple chat threads
- Upload and share images with Claude
- Upload and store other file types
- Persistent chat history

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   poetry install
   ```
3. Create a `.env` file with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
4. Run the app:
   ```
   poetry run python main.py
   ```

## Testing

Run tests with:
```
poetry run pytest
```

## Project Structure

- `chatbot/app.py` - Main Streamlit application
- `chatbot/chat_manager.py` - Manages chat threads and history
- `chatbot/anthropic_client.py` - Wrapper for Anthropic API
- `tests/` - Test files
