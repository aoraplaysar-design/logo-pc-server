import os
import binascii
from urllib.parse import parse_qs

from flask import Flask, jsonify, request, Response

app = Flask(__name__)


def printable_preview(data):
    if not data:
        return ""

    return "".join(
        chr(b) if 32 <= b <= 126 else "."
        for b in data[:512]
    )


def log_request(path):
    body = request.get_data(cache=True)

    print("\n" + "=" * 70, flush=True)
    print("REQUEST", flush=True)
    print("=" * 70, flush=True)

    print("Method:", request.method, flush=True)
    print("Path:", "/" + path, flush=True)
    print("Remote:", request.remote_addr, flush=True)
    print("User-Agent:", request.headers.get("User-Agent"), flush=True)
    print("Content-Type:", request.headers.get("Content-Type"), flush=True)
    print("Content-Encoding:", request.headers.get("Content-Encoding"), flush=True)
    print("Content-Length:", len(body), flush=True)

    print("\n--- HEADERS ---", flush=True)
    for key, value in request.headers.items():
        print(f"{key}: {value}", flush=True)

    print("\n--- BODY LENGTH ---", flush=True)
    print(len(body), "bytes", flush=True)

    print("\n--- BODY HEX FULL ---", flush=True)
    print(body.hex(), flush=True)

    print("\n--- BODY HEX FIRST 256 ---", flush=True)
    print(body[:256].hex(), flush=True)

    print("\n--- BODY HEX LAST 256 ---", flush=True)
    print(body[-256:].hex() if body else "", flush=True)

    print("\n--- PRINTABLE PREVIEW ---", flush=True)
    print(printable_preview(body), flush=True)

    if request.content_type:
        try:
            parsed = parse_qs(
                body.decode("utf-8", errors="replace"),
                keep_blank_values=True
            )

            if parsed:
                print("\n--- FORM FIELDS ---", flush=True)

                for key, values in parsed.items():
                    print(
                        f"{key}: "
                        + " | ".join(
                            str(v)[:1000] for v in values
                        ),
                        flush=True
                    )
        except Exception as e:
            print("FORM PARSE ERROR:", repr(e), flush=True)

    print("\n--- BODY BYTE FREQUENCY ---", flush=True)

    frequency = {}

    for byte in body:
        frequency[byte] = frequency.get(byte, 0) + 1

    common = sorted(
        frequency.items(),
        key=lambda x: x[1],
        reverse=True
    )[:20]

    print(
        " ".join(
            f"{byte:02x}:{count}"
            for byte, count in common
        ),
        flush=True
    )

    print("=" * 70 + "\n", flush=True)


@app.route(
    "/",
    defaults={"path": ""},
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
        "HEAD"
    ]
)
@app.route(
    "/<path:path>",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
        "HEAD"
    ]
)
def catch_all(path):

    log_request(path)

    # -------------------------------------------------
    # Temporary response
    # We are still collecting the real protocol.
    # -------------------------------------------------

    response_data = {
        "status": "ok",
        "device": "pc",
        "deviceType": "pc",
        "platform": "windows",
        "logo": "pc"
    }

    response = jsonify(response_data)

    response.headers["X-Server"] = "logo-pc-server"
    response.headers["X-Device-Type"] = "pc"

    print("--- RESPONSE ---", flush=True)
    print("Status: 200", flush=True)
    print("Content-Type: application/json", flush=True)
    print("Body:", response_data, flush=True)
    print("=" * 70, flush=True)

    return response


@app.get("/health")
def health():
    return jsonify({
        "status": "online",
        "server": "logo-pc-server"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))

    print("========================================", flush=True)
    print("LOGO PC SERVER STARTING", flush=True)
    print("PORT:", port, flush=True)
    print("========================================", flush=True)

    app.run(
        host="0.0.0.0",
        port=port
    )