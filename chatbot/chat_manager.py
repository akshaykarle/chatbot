from typing import Dict, List, Optional, Any
import uuid
import json
import os
from datetime import datetime

class ChatThread:
    def __init__(self, thread_id: Optional[str] = None, title: Optional[str] = None, model: Optional[str] = None):
        self.thread_id = thread_id or str(uuid.uuid4())
        self.title = title or f"New Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        self.model = model or "claude-3-opus-20240229"
        self.messages: List[Dict[str, Any]] = []
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def add_message(self, role: str, content: str, media: Optional[List[Dict[str, Any]]] = None):
        """Add a message to the thread"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        if media:
            message["media"] = media

        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()
        return message

    def to_dict(self) -> Dict:
        """Convert thread to dictionary for serialization"""
        return {
            "thread_id": self.thread_id,
            "title": self.title,
            "model": self.model,
            "messages": self.messages,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ChatThread':
        """Create a thread from dictionary"""
        thread = cls(
            thread_id=data.get("thread_id"),
            title=data.get("title"),
            model=data.get("model")
        )
        thread.messages = data.get("messages", [])
        thread.created_at = data.get("created_at", thread.created_at)
        thread.updated_at = data.get("updated_at", thread.updated_at)
        return thread


class ChatManager:
    def __init__(self, storage_path: str = "chat_history.json"):
        self.storage_path = storage_path
        self.threads: Dict[str, ChatThread] = {}
        self.load_threads()

    def create_thread(self, title: Optional[str] = None, model: Optional[str] = None) -> ChatThread:
        """Create a new chat thread"""
        thread = ChatThread(title=title, model=model)
        self.threads[thread.thread_id] = thread
        self.save_threads()
        return thread

    def get_thread(self, thread_id: str) -> Optional[ChatThread]:
        """Get a thread by ID"""
        return self.threads.get(thread_id)

    def get_all_threads(self) -> List[ChatThread]:
        """Get all threads sorted by updated_at (newest first)"""
        return sorted(
            self.threads.values(),
            key=lambda t: t.updated_at,
            reverse=True
        )

    def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread by ID"""
        if thread_id in self.threads:
            del self.threads[thread_id]
            self.save_threads()
            return True
        return False

    def save_threads(self):
        """Save threads to storage"""
        data = {
            thread_id: thread.to_dict()
            for thread_id, thread in self.threads.items()
        }

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.storage_path) or ".", exist_ok=True)

        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def load_threads(self):
        """Load threads from storage"""
        if not os.path.exists(self.storage_path):
            return

        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)

            self.threads = {
                thread_id: ChatThread.from_dict(thread_data)
                for thread_id, thread_data in data.items()
            }
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading chat history: {e}")
