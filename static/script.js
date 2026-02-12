const socket = io();

// Canvas setup
const canvas = document.getElementById('whiteboard');
const ctx = canvas.getContext('2d');
const controls = document.querySelector('.controls');

// Resize canvas to fill the container
function resizeCanvas() {
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight - controls.clientHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas(); // Initial resize

let drawing = false;
let currentX = 0;
let currentY = 0;

// Drawing function
function draw(x0, y0, x1, y1, color, size, emitEvent) {
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.strokeStyle = color;
    ctx.lineWidth = size;
    ctx.lineCap = 'round';
    ctx.stroke();
    ctx.closePath();

    if (!emitEvent) return;

    socket.emit('draw_event', {
        x0: x0 / canvas.width,
        y0: y0 / canvas.height,
        x1: x1 / canvas.width,
        y1: y1 / canvas.height,
        color: color,
        size: size
    });
}

// Mouse events
canvas.addEventListener('mousedown', (e) => {
    drawing = true;
    currentX = e.offsetX;
    currentY = e.offsetY;
});

canvas.addEventListener('mousemove', (e) => {
    if (!drawing) return;
    const color = document.getElementById('color-picker').value;
    const size = document.getElementById('brush-size').value;
    draw(currentX, currentY, e.offsetX, e.offsetY, color, size, true);
    currentX = e.offsetX;
    currentY = e.offsetY;
});

canvas.addEventListener('mouseup', () => drawing = false);
canvas.addEventListener('mouseout', () => drawing = false);

// Socket events for drawing
socket.on('draw_event', (data) => {
    draw(
        data.x0 * canvas.width,
        data.y0 * canvas.height,
        data.x1 * canvas.width,
        data.y1 * canvas.height,
        data.color,
        data.size,
        false
    );
});

socket.on('clear_board', () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
});

// Clear board button
document.getElementById('clear-btn').addEventListener('click', () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    socket.emit('clear_board');
});

// Chat functionality
const messageInput = document.getElementById('message-input');
const usernameInput = document.getElementById('username');
const sendBtn = document.getElementById('send-btn');
const messagesList = document.getElementById('messages');

function sendMessage() {
    const msg = messageInput.value;
    const user = usernameInput.value || 'Anonymous';
    if (msg.trim()) {
        socket.emit('chat_message', { user: user, message: msg });
        messageInput.value = '';
    }
}

sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

socket.on('chat_message', (data) => {
    const li = document.createElement('li');
    li.textContent = `${data.user}: ${data.message}`;
    messagesList.appendChild(li);
    // Auto-scroll to bottom
    const chatWindow = document.getElementById('chat-window');
    chatWindow.scrollTop = chatWindow.scrollHeight;
});
