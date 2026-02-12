import json
import os
from models import ChatMessage

class ChatManager:
    def __init__(self, storage_file='chat_history.json', history_limit=50):
        self.storage_file = storage_file
        self.history_limit = history_limit
        self.messages = []
        self.load_from_file()

    def add_message(self, user, message):
        """Stores a message with a timestamp."""
        chat_msg = ChatMessage(user, message)
        
        if not chat_msg.is_valid():
            return False
            
        msg_data = chat_msg.to_dict()
        self.messages.append(msg_data)
        
        # Trim history if it exceeds the limit
        if len(self.messages) > self.history_limit:
            self.messages = self.messages[-self.history_limit:]
            
        self.save_to_file()
        return msg_data

    def get_recent_messages(self):
        """Returns chat history."""
        return self.messages

    def clear_chat(self):
        """Clears chat history."""
        self.messages = []
        self.save_to_file()

    def save_to_file(self):
        """Persists chat history to disk."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.messages, f)
        except IOError as e:
            print(f"Error saving chat history: {e}")

    def load_from_file(self):
        """Loads chat history from disk."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    self.messages = json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error loading chat history: {e}")
                self.messages = []
