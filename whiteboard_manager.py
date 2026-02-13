import json
import os
import time
import threading
from models import Stroke

class WhiteboardManager:
    def __init__(self, data_dir='data', save_interval=5):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.boards = {}  # Cache of loaded boards: board_id -> list of strokes
        self.dirty_boards = set()
        self.lock = threading.Lock()
        
        # Background saver
        self.save_interval = save_interval
        self.running = True
        self.saver_thread = threading.Thread(target=self._background_saver, daemon=True)
        self.saver_thread.start()

    def _background_saver(self):
        """Periodically saves dirty boards to disk."""
        while self.running:
            time.sleep(self.save_interval)
            self._save_dirty_boards()

    def _save_dirty_boards(self):
        """Saves all boards currently marked as dirty."""
        with self.lock:
            if not self.dirty_boards:
                return
            boards_to_save = list(self.dirty_boards)
            self.dirty_boards.clear()

        for board_id in boards_to_save:
            self.save_to_file(board_id)

    def _get_file_path(self, board_id):
        return os.path.join(self.data_dir, f"{board_id}_board.json")

    def _ensure_board_loaded(self, board_id):
        # Optimistic check (unlocked)
        if board_id in self.boards:
            return
            
        with self.lock:
            # Double check inside lock
            if board_id not in self.boards:
                self.load_from_file(board_id)

    def add_stroke(self, board_id, stroke_data):
        """Validates and stores a drawing stroke for a specific board."""
        self._ensure_board_loaded(board_id)
        stroke = Stroke.from_dict(stroke_data)
        if stroke.is_valid():
            with self.lock:
                self.boards[board_id].append(stroke.to_dict())
                self.dirty_boards.add(board_id)
            return True
        return False

    def clear_board(self, board_id):
        """Clears the history for a specific board."""
        with self.lock:
            self.boards[board_id] = []
            self.dirty_boards.add(board_id)

    def get_board_state(self, board_id):
        """Returns the full drawing history for a specific board."""
        self._ensure_board_loaded(board_id)
        with self.lock:
            # Return a copy to avoid race conditions during iteration
            return list(self.boards[board_id])

    def save_to_file(self, board_id):
        """Persists state of a specific board to disk."""
        # Note: calling this directly might skip the dirty check, but that's fine.
        # When called from background saver, we are already outside the main lock 
        # (mostly, except we shouldn't hold self.lock while doing I/O)
        
        data_to_save = None
        with self.lock:
            if board_id in self.boards:
                data_to_save = list(self.boards[board_id])
        
        if data_to_save is not None:
            try:
                with open(self._get_file_path(board_id), 'w') as f:
                    json.dump(data_to_save, f)
            except IOError as e:
                print(f"Error saving whiteboard state for {board_id}: {e}")

    def load_from_file(self, board_id):
        """Loads state of a specific board from disk."""
        file_path = self._get_file_path(board_id)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    # No lock needed here as it's called from _ensure_board_loaded which holds lock
                    # BUT strictly speaking we should be careful. 
                    # _ensure_board_loaded logic above holds lock.
                    self.boards[board_id] = json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error loading whiteboard state for {board_id}: {e}")
                self.boards[board_id] = []
        else:
            self.boards[board_id] = []
