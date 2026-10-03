import os
import hashlib
import requests
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

PORT = int(os.environ.get("PORT", "8080"))
UPSTREAM = "https://loginbp.ggblueshark.com"

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

PC_INFO = {
    "deviceType": "pc",
    "platform": "windows",
    "logo": "pc"
}


@app.get("/")
def home():
    return jsonify({
        "status": "online",
        "service": "OB55 relay",
        "device": PC_INFO
    })


@app.get("/device")
def device():
    return jsonify(PC_INFO)


@app.get("/pc")
def pc():
    return jsonify({
        "status": "ok",
        "pc": True,
        **PC_INFO
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


def forward(path):
    body = request.get_data(cache=False)

    headers = {}

    for name, value in request.headers.items():
        if name.lower() not in HOP_BY_HOP:
            headers[name] = value

    print("\n========== RELAY ==========")
    print("PATH:", path)
    print("BODY:", len(body), "bytes")
    print("SHA256:", hashlib.sha256(body).hexdigest())

    try:
        r = requests.request(
            method=request.method,
            url=UPSTREAM + path,
            headers=headers,
            data=body,
            timeout=30,
            allow_redirects=False
        )

        print("UPSTREAM:", r.status_code)
        print("RESPONSE:", len(r.content), "bytes")
        print("===========================\n")

        response_headers = {}

        for name, value in r.headers.items():
            if name.lower() not in HOP_BY_HOP:
                response_headers[name] = value

        return Response(
            r.content,
            status=r.status_code,
            headers=response_headers
        )

    except requests.RequestException as e:
        print("ERROR:", repr(e))

        return Response(
            b"",
            status=502,
            content_type="application/octet-stream"
        )


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


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=PORT,
        threaded=True
        )
