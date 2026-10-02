import os
import hashlib
import requests
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

PORT = int(os.environ.get("PORT", "8080"))

# Official upstream used by public Free Fire protocol implementations.
UPSTREAM = "https://loginbp.ggblueshark.com"

TIMEOUT = 30

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
    "host",
}

def upstream_headers():
    headers = {}

    for key, value in request.headers.items():
        if key.lower() in HOP_BY_HOP:
            continue

        # Never invent or modify authentication data.
        headers[key] = value

    return headers


def forward(path):
    body = request.get_data(cache=False)

    url = UPSTREAM + path

    print()
    print("========== RELAY ==========")
    print("METHOD :", request.method)
    print("PATH   :", path)
    print("UPSTREAM:", url)
    print("BYTES  :", len(body))
    print("SHA256 :", hashlib.sha256(body).hexdigest())

    try:
        r = requests.request(
            method=request.method,
            url=url,
            headers=upstream_headers(),
            data=body,
            timeout=TIMEOUT,
            allow_redirects=False,
            verify=True,
        )

        print("STATUS :", r.status_code)
        print("REPLY  :", len(r.content), "bytes")
        print("============================")

        response_headers = {}

        for key, value in r.headers.items():
            if key.lower() in HOP_BY_HOP:
                continue

            response_headers[key] = value

        return Response(
            r.content,
            status=r.status_code,
            headers=response_headers,
        )

    except requests.RequestException as e:
        print("UPSTREAM ERROR:", repr(e))

        return Response(
            b"",
            status=502,
            headers={
                "Content-Type": "application/octet-stream"
            },
        )


@app.get("/")
def index():
    return jsonify({
        "status": "online",
        "service": "Free Fire OB55 relay",
        "upstream": UPSTREAM
    })


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "ob55-relay"
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
def relay(path):
    return forward("/" + path)


@app.errorhandler(404)
def not_found(_):
    return forward(request.path)


@app.errorhandler(405)
def method_not_allowed(_):
    return forward(request.path)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=PORT,
        threaded=True
    )