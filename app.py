from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = '91aa5812fd08373d673c4b383fdfd487507f5c3b1a69056fe495c423a7749133'

# ✅ Important for Render (async support)
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="eventlet"
)

# Store latest scan
latest_scan = None


@app.route('/')
def scanner():
    return render_template('scanner.html')


@app.route('/display')
def display():
    return render_template('display.html')


# ✅ When client connects
@socketio.on('connect')
def on_connect():
    global latest_scan
    if latest_scan:
        emit('qr_result', latest_scan)


# ✅ When QR is scanned
@socketio.on('qr_scanned')
def on_qr_scanned(data):
    global latest_scan

    # Ensure timestamp exists
    payload = {
        "data": data.get("data"),
        "type": data.get("type"),
        "ts": data.get("ts") or int(time.time() * 1000)
    }

    latest_scan = payload

    # Broadcast to all clients
    emit('qr_result', payload, broadcast=True)


# ✅ Render-compatible run
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)