import os
import json
from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Ligtas na pag-initialize ng Firebase mula sa Environment Variable
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
    return "Server is running smoothly!", 200

@app.route('/api/clients', methods=['GET'])
def get_clients():
    try:
        if not db:
            return jsonify({"error": "Database not initialized or config missing"}), 500
        
        clients_ref = db.collection('clients')
        docs = clients_ref.stream()
        clients = [{**doc.to_dict(), "id": doc.id} for doc in docs]
        return jsonify(clients), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    try:
        data = request.get_json(silent=True) or {}
        # Ilagay ang logic para sa heartbeat dito
        return jsonify({"status": "success", "message": "Heartbeat received"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/target-action', methods=['POST'])
def target_action():
    try:
        data = request.get_json(silent=True) or {}
        # Ilagay ang logic para sa target action dito
        return jsonify({"status": "success", "message": "Action processed"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)