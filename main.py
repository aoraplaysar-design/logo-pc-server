import os
from flask import Flask, jsonify, request

app = Flask(__name__)

PORT = int(os.environ.get("PORT", "8080"))


# =========================================================
# PC DEVICE INFORMATION
# =========================================================

PC_INFO = {
    "deviceType": "pc",
    "device_type": "pc",
    "platform": "windows",
    "platformType": "pc",
    "platform_type": "pc",
    "logo": "pc",
    "device": "pc"
}


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return jsonify({
        "status": "online",
        "service": "logo-pc-server",
        **PC_INFO
    })


# =========================================================
# DEVICE
# =========================================================

@app.get("/device")
def device():
    return jsonify(PC_INFO)


# =========================================================
# DEVICE INFO
# =========================================================

@app.get("/device/info")
def device_info():
    return jsonify({
        "status": "ok",
        **PC_INFO
    })


# =========================================================
# PC
# =========================================================

@app.get("/pc")
def pc():
    return jsonify({
        "status": "ok",
        "pc": True,
        **PC_INFO
    })


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "online": True
    })


# =========================================================
# CONFIG
# =========================================================

@app.get("/config")
def config():
    return jsonify({
        "device": PC_INFO,
        "deviceType": "pc",
        "platform": "windows",
        "logo": "pc"
    })


# =========================================================
# UNKNOWN REQUESTS
# =========================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "not_found"
    }), 404


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=PORT,
        threaded=True
    )
