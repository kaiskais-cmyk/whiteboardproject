import json
import os
import time
import threading
from models import ChatMessage

class ChatManager:
    def __init__(self, data_dir='data', history_limit=50, save_interval=5):
        self.data_dir = data_dir
        self.history_limit = history_limit
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.chats = {} # Cache of loaded chats: board_id -> list of messages
        self.dirty_chats = set()
        self.lock = threading.Lock()
        
        # Background saver
        self.save_interval = save_interval
        self.running = True
        self.saver_thread = threading.Thread(target=self._background_saver, daemon=True)
        self.saver_thread.start()

    def _background_saver(self):
        """Periodically saves dirty chats to disk."""
        while self.running:
            time.sleep(self.save_interval)
            self._save_dirty_chats()

    def _save_dirty_chats(self):
        """Saves all chats currently marked as dirty."""
        with self.lock:
            if not self.dirty_chats:
                return
            chats_to_save = list(self.dirty_chats)
            self.dirty_chats.clear()

        for board_id in chats_to_save:
            self.save_to_file(board_id)

    def _get_file_path(self, board_id):
        return os.path.join(self.data_dir, f"{board_id}_chat.json")

    def _ensure_chat_loaded(self, board_id):
        # Optimistic
        if board_id in self.chats:
            return
            
        with self.lock:
            if board_id not in self.chats:
                self.load_from_file(board_id)

    def add_message(self, board_id, user, message):
        """Stores a message with a timestamp for a specific board."""
        self._ensure_chat_loaded(board_id)
        chat_msg = ChatMessage(user, message)
        
        if not chat_msg.is_valid():
            return False
            
        msg_data = chat_msg.to_dict()
        
        with self.lock:
            self.chats[board_id].append(msg_data)
            
            # Trim history if it exceeds the limit
            if len(self.chats[board_id]) > self.history_limit:
                self.chats[board_id] = self.chats[board_id][-self.history_limit:]
            
            self.dirty_chats.add(board_id)
            
        return msg_data

    def get_recent_messages(self, board_id):
        """Returns chat history for a specific board."""
        self._ensure_chat_loaded(board_id)
        with self.lock:
            return list(self.chats[board_id])

    def clear_chat(self, board_id):
        """Clears chat history for a specific board."""
        with self.lock:
            self.chats[board_id] = []
            self.dirty_chats.add(board_id)

    def save_to_file(self, board_id):
        """Persists chat history of a specific board to disk."""
        data_to_save = None
        with self.lock:
            if board_id in self.chats:
                 data_to_save = list(self.chats[board_id])
        
        if data_to_save is not None:
            try:
                with open(self._get_file_path(board_id), 'w') as f:
                    json.dump(data_to_save, f)
            except IOError as e:
                print(f"Error saving chat history for {board_id}: {e}")

    def load_from_file(self, board_id):
        """Loads chat history of a specific board from disk."""
        file_path = self._get_file_path(board_id)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    self.chats[board_id] = json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error loading chat history for {board_id}: {e}")
                self.chats[board_id] = []
        else:
            self.chats[board_id] = []
