from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from whiteboard_manager import WhiteboardManager
from chat_manager import ChatManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Initialize managers
whiteboard_manager = WhiteboardManager()
chat_manager = ChatManager()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    # Send existing board state to the new user
    board_state = whiteboard_manager.get_board_state()
    for stroke in board_state:
        # Emit each stroke individually to the new user so they can replay the drawing
        # Alternatively, we could send the whole list and handle it in JS
        emit('draw_event', stroke)
        
    # Send chat history
    chat_history = chat_manager.get_recent_messages()
    for msg in chat_history:
        emit('chat_message', msg)

@socketio.on('draw_event')
def handle_draw_event(json):
    if whiteboard_manager.add_stroke(json):
        emit('draw_event', json, broadcast=True, include_self=False)

@socketio.on('clear_board')
def handle_clear_board():
    whiteboard_manager.clear_board()
    emit('clear_board', broadcast=True)

@socketio.on('chat_message')
def handle_chat_message(json):
    saved_msg = chat_manager.add_message(json.get('user'), json.get('message'))
    if saved_msg:
        emit('chat_message', saved_msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
