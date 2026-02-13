from datetime import datetime

class Stroke:
    def __init__(self, x0, y0, x1, y1, color, size, stroke_type='line'):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.color = color
        self.size = size
        self.stroke_type = stroke_type

    def to_dict(self):
        return {
            'x0': self.x0,
            'y0': self.y0,
            'x1': self.x1,
            'y1': self.y1,
            'color': self.color,
            'size': self.size,
            'type': self.stroke_type
        }

    @staticmethod
    def from_dict(data):
        return Stroke(
            x0=data.get('x0'),
            y0=data.get('y0'),
            x1=data.get('x1'),
            y1=data.get('y1'),
            color=data.get('color'),
            size=data.get('size'),
            stroke_type=data.get('type', 'line')
        )

    def is_valid(self):
        return all(v is not None for v in [self.x0, self.y0, self.x1, self.y1, self.color, self.size])


class ChatMessage:
    def __init__(self, user, message, timestamp=None):
        self.user = user
        self.message = message
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self):
        return {
            'user': self.user,
            'message': self.message,
            'timestamp': self.timestamp
        }

    @staticmethod
    def from_dict(data):
        return ChatMessage(
            user=data.get('user'),
            message=data.get('message'),
            timestamp=data.get('timestamp')
        )

    def is_valid(self):
        return bool(self.user and self.message and self.message.strip())
