from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from whiteboard_manager import WhiteboardManager
from chat_manager import ChatManager
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Initialize managers
whiteboard_manager = WhiteboardManager()
chat_manager = ChatManager()

@app.route('/')
def index():
    # Redirect to a random board
    return redirect(url_for('board', board_id=uuid.uuid4()))

@app.route('/board/<board_id>')
def board(board_id):
    return render_template('index.html', board_id=board_id)

@socketio.on('join')
def on_join(data):
    board_id = data['board_id']
    join_room(board_id)
    
    # Send existing board state to the user joining the room
    board_state = whiteboard_manager.get_board_state(board_id)
    for stroke in board_state:
        emit('draw_event', stroke)
        
    # Send chat history
    chat_history = chat_manager.get_recent_messages(board_id)
    for msg in chat_history:
        emit('chat_message', msg)

@socketio.on('draw_event')
def handle_draw_event(json):
    board_id = json.get('board_id')
    if board_id and whiteboard_manager.add_stroke(board_id, json):
        emit('draw_event', json, room=board_id, include_self=False)

@socketio.on('clear_board')
def handle_clear_board(data):
    board_id = data.get('board_id')
    if board_id:
        whiteboard_manager.clear_board(board_id)
        emit('clear_board', room=board_id)

@socketio.on('chat_message')
def handle_chat_message(json):
    board_id = json.get('board_id')
    user = json.get('user')
    message = json.get('message')
    
    if board_id:
        saved_msg = chat_manager.add_message(board_id, user, message)
        if saved_msg:
            emit('chat_message', saved_msg, room=board_id)

if __name__ == '__main__':
    socketio.run(app, debug=True)
