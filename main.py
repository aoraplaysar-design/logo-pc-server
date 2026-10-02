import os
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route(
    "/",
    defaults={"path": ""},
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
)
@app.route(
    "/<path:path>",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
)
def catch_all(path):
    print("========== REQUEST ==========", flush=True)
    print("Method:", request.method, flush=True)
    print("Path:", "/" + path, flush=True)
    print("User-Agent:", request.headers.get("User-Agent"), flush=True)
    print("Content-Type:", request.headers.get("Content-Type"), flush=True)
    print("Content-Length:", request.headers.get("Content-Length"), flush=True)
    print("Remote:", request.remote_addr, flush=True)
    print("=============================", flush=True)

    return jsonify({
        "status": "ok",
        "device": "pc",
        "deviceType": "pc",
        "platform": "windows",
        "logo": "pc"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)