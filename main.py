import os
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
def test_pc(path):
    print("REQUEST:", request.method, "/" + path, flush=True)

    return jsonify({
        "status": "ok",
        "deviceType": "pc",
        "platform": "windows",
        "device": "pc",
        "logo": "pc"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)