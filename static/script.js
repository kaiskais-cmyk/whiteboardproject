const socket = io();

// Canvas setup
const canvas = document.getElementById('whiteboard');
const ctx = canvas.getContext('2d');
const controls = document.querySelector('.controls');

// Get Board ID from URL
const boardId = window.location.pathname.split('/').pop();

// Join the board room
socket.on('connect', () => {
    console.log('Connected to server');
    socket.emit('join', { board_id: boardId });
});

// Resize canvas to fill the container
function resizeCanvas() {
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight - controls.clientHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas(); // Initial resize

let drawing = false;
let startX = 0;
let startY = 0;
let currentTool = 'line';
let snapshot;

// Tool Selection
document.getElementById('tool-pen').addEventListener('click', () => setTool('line', 'tool-pen'));
document.getElementById('tool-rect').addEventListener('click', () => setTool('rect', 'tool-rect'));
document.getElementById('tool-circle').addEventListener('click', () => setTool('circle', 'tool-circle'));

function setTool(tool, btnId) {
    currentTool = tool;
    document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(btnId).classList.add('active');
}

// Drawing function
function drawStroke(data) {
    const w = canvas.width;
    const h = canvas.height;
    const x0 = data.x0 * w;
    const y0 = data.y0 * h;
    const x1 = data.x1 * w;
    const y1 = data.y1 * h;

    ctx.beginPath();
    ctx.strokeStyle = data.color;
    ctx.lineWidth = data.size;
    ctx.lineCap = 'round';

    if (data.type === 'line') {
        ctx.moveTo(x0, y0);
        ctx.lineTo(x1, y1);
        ctx.stroke();
    } else if (data.type === 'rect') {
        ctx.rect(x0, y0, x1 - x0, y1 - y0);
        ctx.stroke();
    } else if (data.type === 'circle') {
        const radius = Math.sqrt(Math.pow(x1 - x0, 2) + Math.pow(y1 - y0, 2));
        ctx.arc(x0, y0, radius, 0, 2 * Math.PI);
        ctx.stroke();
    }
    ctx.closePath();
}

function emitEvent(x0, y0, x1, y1) {
    const color = document.getElementById('color-picker').value;
    const size = document.getElementById('brush-size').value;

    const data = {
        board_id: boardId,
        x0: x0 / canvas.width,
        y0: y0 / canvas.height,
        x1: x1 / canvas.width,
        y1: y1 / canvas.height,
        color: color,
        size: size,
        type: currentTool
    };

    socket.emit('draw_event', data);

    // Draw locally immediately if it's a line (shapes are drawn on mouseup)
    // Actually shapes need to be drawn locally to persist them after preview
    // But drawStroke takes normalized coords, so let's use it for consistency
    drawStroke(data);
}


// Mouse events
canvas.addEventListener('mousedown', (e) => {
    drawing = true;
    startX = e.offsetX;
    startY = e.offsetY;
    ctx.beginPath(); // Start new path
    snapshot = ctx.getImageData(0, 0, canvas.width, canvas.height);
});

canvas.addEventListener('mousemove', (e) => {
    if (!drawing) return;
    const currentX = e.offsetX;
    const currentY = e.offsetY;

    if (currentTool === 'line') {
        const color = document.getElementById('color-picker').value;
        const size = document.getElementById('brush-size').value;

        ctx.lineWidth = size;
        ctx.lineCap = 'round';
        ctx.strokeStyle = color;

        ctx.lineTo(currentX, currentY);
        ctx.stroke();

        // For 'line', we emit continuous segments
        // We need to re-implement line emitting to match previous 'draw' logic 
        // which emitted segments. The previous logic was: draw(x0, y0, x1, y1)
        // Here we are using ctx.lineTo which connects to last point in path.
        // To be compatible with 'segment' based storage, we should track prevX/prevY

        // Let's stick to the segment model for lines for now, but optimize?
        // Actually, the previous model emitted EVERY mousemove.

        const data = {
            board_id: boardId,
            x0: startX / canvas.width,
            y0: startY / canvas.height,
            x1: currentX / canvas.width,
            y1: currentY / canvas.height,
            color: color,
            size: size,
            type: 'line'
        };
        socket.emit('draw_event', data);

        startX = currentX;
        startY = currentY;

    } else {
        // Shapes: restore snapshot and draw preview
        ctx.putImageData(snapshot, 0, 0);
        const color = document.getElementById('color-picker').value;
        const size = document.getElementById('brush-size').value;
        ctx.strokeStyle = color;
        ctx.lineWidth = size;

        ctx.beginPath();
        if (currentTool === 'rect') {
            ctx.rect(startX, startY, currentX - startX, currentY - startY);
        } else if (currentTool === 'circle') {
            const radius = Math.sqrt(Math.pow(currentX - startX, 2) + Math.pow(currentY - startY, 2));
            ctx.arc(startX, startY, radius, 0, 2 * Math.PI);
        }
        ctx.stroke();
    }
});

canvas.addEventListener('mouseup', (e) => {
    if (!drawing) return;
    const currentX = e.offsetX;
    const currentY = e.offsetY;

    if (currentTool !== 'line') {
        // Finalize shape
        emitEvent(startX, startY, currentX, currentY);
    }
    drawing = false;
    ctx.beginPath(); // Reset path
});

canvas.addEventListener('mouseout', () => drawing = false);

// Socket events for drawing
socket.on('draw_event', (data) => {
    drawStroke(data);
});

socket.on('clear_board', () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
});

// Clear board button
document.getElementById('clear-btn').addEventListener('click', () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    socket.emit('clear_board', { board_id: boardId });
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
        socket.emit('chat_message', {
            board_id: boardId,
            user: user,
            message: msg
        });
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
