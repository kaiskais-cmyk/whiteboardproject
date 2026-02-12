import unittest
from models import Stroke, ChatMessage

class TestStroke(unittest.TestCase):
    def test_valid_stroke(self):
        stroke = Stroke(0, 0, 100, 100, '#000', 5)
        self.assertTrue(stroke.is_valid())
        self.assertEqual(stroke.to_dict()['color'], '#000')

    def test_invalid_stroke(self):
        stroke = Stroke(0, 0, None, 100, '#000', 5)
        self.assertFalse(stroke.is_valid())

    def test_from_dict(self):
        data = {'x0': 10, 'y0': 20, 'x1': 30, 'y1': 40, 'color': 'red', 'size': 2}
        stroke = Stroke.from_dict(data)
        self.assertEqual(stroke.x0, 10)
        self.assertTrue(stroke.is_valid())

class TestChatMessage(unittest.TestCase):
    def test_valid_message(self):
        msg = ChatMessage('user', 'hello')
        self.assertTrue(msg.is_valid())
        self.assertIsNotNone(msg.timestamp)

    def test_invalid_message(self):
        msg = ChatMessage('user', '')
        self.assertFalse(msg.is_valid())
        
        msg2 = ChatMessage('user', '   ')
        self.assertFalse(msg2.is_valid())

    def test_from_dict(self):
        data = {'user': 'u', 'message': 'm', 'timestamp': 't'}
        msg = ChatMessage.from_dict(data)
        self.assertEqual(msg.message, 'm')
        self.assertEqual(msg.timestamp, 't')

if __name__ == '__main__':
    unittest.main()
