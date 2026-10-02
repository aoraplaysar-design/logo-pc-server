import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
def catch_all(path):
    body = request.get_data(as_text=True)

    log = {
        "method": request.method,
        "path": "/" + path,
        "query": request.args.to_dict(flat=False),
        "headers": dict(request.headers),
        "body": body
    }

    print("========== REQUEST ==========")
    print(json.dumps(log, ensure_ascii=False, indent=2))
    print("=============================")

    return jsonify({
        "status": "ok"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
