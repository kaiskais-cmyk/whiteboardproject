import json
import os
from models import Stroke

class WhiteboardManager:
    def __init__(self, storage_file='board_state.json'):
        self.storage_file = storage_file
        self.history = []
        self.load_from_file()

    def add_stroke(self, stroke_data):
        """Validates and stores a drawing stroke."""
        stroke = Stroke.from_dict(stroke_data)
        if stroke.is_valid():
            self.history.append(stroke.to_dict())
            self.save_to_file()
            return True
        return False

    def clear_board(self):
        """Clears the whiteboard history."""
        self.history = []
        self.save_to_file()

    def get_board_state(self):
        """Returns the full drawing history."""
        return self.history

    def save_to_file(self):
        """Persists state to disk."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.history, f)
        except IOError as e:
            print(f"Error saving whiteboard state: {e}")

    def load_from_file(self):
        """Loads state from disk on startup."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    self.history = json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error loading whiteboard state: {e}")
                self.history = []
