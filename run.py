from app import app, socketio

if __name__ == '__main__':
    print("Starting Whiteboard Application...")
    print("Navigate to http://127.0.0.1:5000")
    socketio.run(app, debug=True)
