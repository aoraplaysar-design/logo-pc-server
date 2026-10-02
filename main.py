import os
import time
import json
import hashlib
from datetime import datetime, timezone

from flask import Flask, request, jsonify, Response

app = Flask(__name__)

PORT = int(os.environ.get("PORT", "8080"))

SERVER_NAME = "logo-pc-ob55-http"
RELEASE = "OB55"

MAX_BODY_PREVIEW = 512


# ============================================================
# HELPERS
# ============================================================

def now():
    return datetime.now(timezone.utc).isoformat()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def hex_preview(data):
    return data[:MAX_BODY_PREVIEW].hex()


def printable_preview(data):
    result = []

    for b in data[:MAX_BODY_PREVIEW]:
        if 32 <= b <= 126:
            result.append(chr(b))
        else:
            result.append(".")

    return "".join(result)


def safe_headers():
    result = {}

    for key, value in request.headers.items():

        # Don't log authorization tokens.
        if key.lower() == "authorization":
            result[key] = "[redacted]"
        else:
            result[key] = str(value)[:1000]

    return result


# ============================================================
# REQUEST LOGGER
# ============================================================

def log_request(path):

    started = time.time()

    body = request.get_data(
        cache=True
    )

    print()
    print("=" * 80)
    print("HTTP COMPATIBILITY REQUEST")
    print("=" * 80)

    print("Time:", now())
    print("Method:", request.method)
    print("Path:", "/" + path)

    print(
        "Releaseversion:",
        request.headers.get(
            "Releaseversion",
            ""
        )
    )

    print(
        "Unity:",
        request.headers.get(
            "X-Unity-Version",
            ""
        )
    )

    print(
        "Content-Type:",
        request.headers.get(
            "Content-Type",
            ""
        )
    )

    print(
        "Content-Encoding:",
        request.headers.get(
            "Content-Encoding",
            ""
        )
    )

    print(
        "Body length:",
        len(body),
        "bytes"
    )

    print(
        "SHA256:",
        sha256(body)
    )

    print()
    print("--- BODY HEX PREVIEW ---")
    print(hex_preview(body))

    print()
    print("--- PRINTABLE PREVIEW ---")
    print(printable_preview(body))

    print()
    print("--- HEADERS ---")

    for key, value in safe_headers().items():
        print(
            f"{key}: {value}"
        )

    elapsed = (
        time.time() - started
    ) * 1000

    print()
    print(
        "Processing:",
        round(elapsed, 2),
        "ms"
    )

    print("=" * 80)
    print()

    return body


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return jsonify({
        "status": "online",
        "server": SERVER_NAME,
        "release": RELEASE,
        "time": now()
    })


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return jsonify({
        "status": "online",
        "server": SERVER_NAME,
        "release": RELEASE,
        "mode": "http-compatibility"
    })


# ============================================================
# OPTIONS
# ============================================================

@app.route(
    "/<path:path>",
    methods=["OPTIONS"]
)
def options_request(path):

    response = Response(
        "",
        status=204
    )

    response.headers[
        "Access-Control-Allow-Origin"
    ] = "*"

    response.headers[
        "Access-Control-Allow-Methods"
    ] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    
    response.headers[
        "Access-Control-Allow-Headers"
    ] = "*"

    return response


# ============================================================
# ALL HTTP REQUESTS
# ============================================================

@app.route(
    "/<path:path>",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "HEAD"
    ]
)
def compatibility(path):

    body = log_request(path)

    path_lower = path.lower()

    # --------------------------------------------------------
    # HEALTH
    # --------------------------------------------------------

    if path_lower == "health":

        return jsonify({
            "status": "online",
            "server": SERVER_NAME,
            "release": RELEASE
        })


    # --------------------------------------------------------
    # PING
    # --------------------------------------------------------

    if path_lower == "ping":

        print(
            "[COMPAT] /Ping received"
        )

        # Empty successful HTTP response.
        #
        # This does NOT fabricate a game protocol message.
        # It only confirms that the HTTP request reached us.

        response = Response(
            b"",
            status=204
        )

        response.headers[
            "X-Server"
        ] = SERVER_NAME

        response.headers[
            "X-Release"
        ] = RELEASE

        return response


    # --------------------------------------------------------
    # MAJORLOGIN
    # --------------------------------------------------------

    if path_lower == "majorlogin":

        print(
            "[COMPAT] /MajorLogin received"
        )

        print(
            "[COMPAT] Payload length:",
            len(body)
        )

        print(
            "[COMPAT] Payload SHA256:",
            sha256(body)
        )

        # IMPORTANT:
        #
        # We intentionally do not generate a fake
        # MajorLoginRes or bypass authentication.
        #
        # Returning an empty successful HTTP response lets
        # us observe whether the client continues or reports
        # a protocol error.

        response = Response(
            b"",
            status=204
        )

        response.headers[
            "X-Server"
        ] = SERVER_NAME

        response.headers[
            "X-Release"
        ] = RELEASE

        response.headers[
            "X-Protocol-Mode"
        ] = "compatibility"

        return response


    # --------------------------------------------------------
    # GENERIC REQUEST
    # --------------------------------------------------------

    print(
        "[COMPAT] Unknown endpoint:",
        "/" + path
    )

    # Generic empty response.
    #
    # This keeps the HTTP layer alive without pretending
    # to be an actual Free Fire protocol response.

    response = Response(
        b"",
        status=204
    )

    response.headers[
        "X-Server"
    ] = SERVER_NAME

    response.headers[
        "X-Release"
    ] = RELEASE

    return response


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def error_404(error):

    return Response(
        b"",
        status=404
    )


@app.errorhandler(405)
def error_405(error):

    return Response(
        b"",
        status=405
    )


@app.errorhandler(500)
def error_500(error):

    print(
        "[ERROR]",
        repr(error),
        flush=True
    )

    return Response(
        b"",
        status=500
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    print("=" * 80)
    print("LOGO PC OB55 HTTP COMPATIBILITY SERVER")
    print("=" * 80)

    print(
        "Server:",
        SERVER_NAME
    )

    print(
        "Release:",
        RELEASE
    )

    print(
        "Port:",
        PORT
    )

    print(
        "Listening:",
        "0.0.0.0"
    )

    print("=" * 80)

    app.run(
        host="0.0.0.0",
        port=PORT,
        threaded=True
    )