import os
import hashlib
import requests
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

PORT = int(os.environ.get("PORT", "8080"))

# خادم اللعبة الذي سيستقبل الطلبات كما هي
UPSTREAM = os.environ.get(
    "UPSTREAM",
    "https://loginbp.ggblueshark.com"
)

HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "content-length",
    "host"
}


def copy_request_headers():
    headers = {}

    for name, value in request.headers.items():
        if name.lower() in HOP_BY_HOP:
            continue

        headers[name] = value

    return headers


def relay(path):
    body = request.get_data(cache=False)

    print("\n==============================")
    print("FREE FIRE 1.56.1 RELAY")
    print("PATH   :", path)
    print("METHOD :", request.method)
    print("BYTES  :", len(body))
    print(
        "SHA256 :",
        hashlib.sha256(body).hexdigest()
    )

    try:
        upstream = requests.request(
            method=request.method,
            url=UPSTREAM + path,
            headers=copy_request_headers(),
            data=body,
            timeout=30,
            allow_redirects=False
        )

    except requests.RequestException as error:
        print("UPSTREAM ERROR:", repr(error))
        print("==============================")

        return Response(
            b"",
            status=502,
            content_type="application/octet-stream"
        )

    print("STATUS :", upstream.status_code)
    print("REPLY  :", len(upstream.content), "bytes")
    print("==============================")

    response_headers = {}

    for name, value in upstream.headers.items():
        if name.lower() in HOP_BY_HOP:
            continue

        response_headers[name] = value

    return Response(
        upstream.content,
        status=upstream.status_code,
        headers=response_headers
    )


@app.get("/")
def index():
    return jsonify({
        "status": "online",
        "service": "Free Fire 1.56.1 relay",
        "upstream": UPSTREAM
    })


@app.get("/health")
def health():
    return jsonify({
        "status": "ok"
    })


@app.route(
    "/<path:path>",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS"
    ]
)
def all_routes(path):
    return relay("/" + path)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=PORT,
        threaded=True
    )
