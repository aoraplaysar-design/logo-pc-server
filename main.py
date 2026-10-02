import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
def catch_all(path):
    body = request.get_data()
    preview = body[:128].hex()

    log = {
        "method": request.method,
        "path": "/" + path,
        "content_type": request.headers.get("Content-Type"),
        "content_length": len(body),
        "body_first_128_bytes_hex": preview
    }

    print("========== REQUEST ==========")
    print(json.dumps(log, ensure_ascii=False, indent=2))
    print("=============================")

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
