import unittest
import os
import json
from whiteboard_manager import WhiteboardManager
from chat_manager import ChatManager

class TestWhiteboardManager(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test_board_state.json'
        self.manager = WhiteboardManager(storage_file=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_stroke_valid(self):
        stroke = {'x0': 0, 'y0': 0, 'x1': 1, 'y1': 1, 'color': '#000', 'size': 5}
        self.assertTrue(self.manager.add_stroke(stroke))
        self.assertEqual(len(self.manager.get_board_state()), 1)

    def test_add_stroke_invalid(self):
        stroke = {'x0': 0} # Missing keys
        self.assertFalse(self.manager.add_stroke(stroke))
        self.assertEqual(len(self.manager.get_board_state()), 0)

    def test_persistence(self):
        stroke = {'x0': 0, 'y0': 0, 'x1': 1, 'y1': 1, 'color': '#000', 'size': 5}
        self.manager.add_stroke(stroke)
        
        # New instance should load from file
        new_manager = WhiteboardManager(storage_file=self.test_file)
        self.assertEqual(len(new_manager.get_board_state()), 1)
        self.assertEqual(new_manager.get_board_state()[0], stroke)

class TestChatManager(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test_chat_history.json'
        self.manager = ChatManager(storage_file=self.test_file, history_limit=5)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_message(self):
        msg = self.manager.add_message('user1', 'hello')
        self.assertIsNotNone(msg)
        self.assertEqual(msg['user'], 'user1')
        self.assertEqual(msg['message'], 'hello')
        self.assertIn('timestamp', msg)

    def test_history_limit(self):
        for i in range(10):
            self.manager.add_message('user1', f'msg {i}')
        
        history = self.manager.get_recent_messages()
        self.assertEqual(len(history), 5)
        self.assertEqual(history[-1]['message'], 'msg 9')
        self.assertEqual(history[0]['message'], 'msg 5')

if __name__ == '__main__':
    unittest.main()
