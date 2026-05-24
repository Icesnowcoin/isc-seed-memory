from flask import Flask, request, jsonify
import json, os, urllib.request
from datetime import datetime

app = Flask(__name__)
MEMORY_FILE = "/opt/isc-memory/memory.json"
SEED_URL = "https://raw.githubusercontent.com/icesnowcoin/isc-seed-memory/main/seed.json"
SEED_KEY = "isc_global_seed"

def load_memory():
    if not os.path.exists(MEMORY_FILE): return {}
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return {}

def save_memory(data):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def ensure_seed():
    memory = load_memory()
    try:
        req = urllib.request.Request(SEED_URL, headers={'User-Agent':'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=15)
        seed_data = json.loads(resp.read().decode())
        memory[SEED_KEY] = {"value": seed_data, "updated_at": datetime.now().isoformat()}
        save_memory(memory)
        print("[SEED] Loaded OK")
        return True
    except Exception as e:
        print(f"[SEED] Fetch failed: {e}")
        return False

@app.route('/set', methods=['POST'])
def set_memory():
    data = request.get_json(force=True)
    key = data.get('key')
    value = data.get('value')
    if not key: return jsonify({"error": "key required"}), 400
    if key == SEED_KEY: return jsonify({"error": "seed read-only"}), 403
    memory = load_memory()
    memory[key] = {"value": value, "updated_at": datetime.now().isoformat()}
    save_memory(memory)
    return jsonify({"status": "ok", "key": key})

@app.route('/get', methods=['POST'])
def get_memory():
    data = request.get_json(force=True)
    key = data.get('key')
    memory = load_memory()
    if key in memory:
        return jsonify({"status": "ok", "key": key, "value": memory[key]["value"]})
    return jsonify({"status": "not_found", "key": key, "value": None}), 404

@app.route('/list', methods=['GET'])
def list_keys():
    memory = load_memory()
    return jsonify({"keys": list(memory.keys())})

if __name__ == '__main__':
    ensure_seed()
    app.run(host='0.0.0.0', port=5002)
