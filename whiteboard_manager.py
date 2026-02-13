import json
import os
from models import Stroke

class WhiteboardManager:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.boards = {}  # Cache of loaded boards: board_id -> list of strokes

    def _get_file_path(self, board_id):
        return os.path.join(self.data_dir, f"{board_id}_board.json")

    def _ensure_board_loaded(self, board_id):
        if board_id not in self.boards:
            self.load_from_file(board_id)

    def add_stroke(self, board_id, stroke_data):
        """Validates and stores a drawing stroke for a specific board."""
        self._ensure_board_loaded(board_id)
        stroke = Stroke.from_dict(stroke_data)
        if stroke.is_valid():
            self.boards[board_id].append(stroke.to_dict())
            self.save_to_file(board_id)
            return True
        return False

    def clear_board(self, board_id):
        """Clears the history for a specific board."""
        self.boards[board_id] = []
        self.save_to_file(board_id)

    def get_board_state(self, board_id):
        """Returns the full drawing history for a specific board."""
        self._ensure_board_loaded(board_id)
        return self.boards[board_id]

    def save_to_file(self, board_id):
        """Persists state of a specific board to disk."""
        if board_id in self.boards:
            try:
                with open(self._get_file_path(board_id), 'w') as f:
                    json.dump(self.boards[board_id], f)
            except IOError as e:
                print(f"Error saving whiteboard state for {board_id}: {e}")

    def load_from_file(self, board_id):
        """Loads state of a specific board from disk."""
        file_path = self._get_file_path(board_id)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    self.boards[board_id] = json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error loading whiteboard state for {board_id}: {e}")
                self.boards[board_id] = []
        else:
            self.boards[board_id] = []
