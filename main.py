import os
import time
import json
import base64
import hashlib
from datetime import datetime, timezone

from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# ============================================================
# CONFIG
# ============================================================

PORT = int(os.environ.get("PORT", "8080"))

MAX_BODY_LOG = 4096
MAX_HEX_LOG = 8192
MAX_PROTO_DEPTH = 2

SERVER_NAME = "logo-pc-ob55-analyzer"
EXPECTED_RELEASE = "OB55"


# ============================================================
# BASIC HELPERS
# ============================================================

def utc_now():
    return datetime.now(timezone.utc).isoformat()


def safe_text(value, limit=500):
    if value is None:
        return ""

    value = str(value)

    if len(value) > limit:
        return value[:limit] + "...[truncated]"

    return value


def printable_preview(data, limit=512):
    if not data:
        return ""

    result = []

    for b in data[:limit]:
        if 32 <= b <= 126:
            result.append(chr(b))
        else:
            result.append(".")

    return "".join(result)


def hex_preview(data, limit=MAX_HEX_LOG):
    if not data:
        return ""

    return data[:limit // 2].hex()


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def b64_preview(data, limit=512):
    if not data:
        return ""

    encoded = base64.b64encode(data).decode("ascii")

    if len(encoded) > limit:
        return encoded[:limit] + "...[truncated]"

    return encoded


# ============================================================
# PROTOBUF WIRE FORMAT DECODER
# ============================================================

def read_varint(data, offset):
    """
    Read protobuf varint.

    Returns:
        (value, new_offset)
    """

    value = 0
    shift = 0

    while offset < len(data):

        byte = data[offset]
        offset += 1

        value |= (byte & 0x7f) << shift

        if not (byte & 0x80):
            return value, offset

        shift += 7

        if shift >= 70:
            raise ValueError("varint too long")

    raise ValueError("unexpected end of varint")


def looks_printable(data):
    if not data:
        return False

    sample = data[:256]

    printable = sum(
        1 for b in sample
        if b in (9, 10, 13) or 32 <= b <= 126
    )

    return printable / len(sample) >= 0.80


def parse_possible_proto(data, depth=0):
    """
    Best-effort protobuf wire-format parser.

    IMPORTANT:
    This does NOT claim to know the OB55 schema.

    It only tries to identify:
      field number
      wire type
      varints
      fixed32
      fixed64
      length-delimited fields

    If the payload is encrypted/compressed/random binary,
    this parser will naturally fail or produce low-confidence
    results.
    """

    if not data:
        return {
            "success": True,
            "fields": []
        }

    if depth > MAX_PROTO_DEPTH:
        return {
            "success": False,
            "reason": "maximum recursion depth reached"
        }

    fields = []
    offset = 0

    try:

        while offset < len(data):

            field_start = offset

            key, offset = read_varint(data, offset)

            field_number = key >> 3
            wire_type = key & 0x07

            if field_number <= 0:
                raise ValueError("invalid field number")

            item = {
                "field": field_number,
                "wire_type": wire_type,
                "offset": field_start
            }

            # ------------------------------------------------
            # VARINT
            # ------------------------------------------------

            if wire_type == 0:

                value, offset = read_varint(data, offset)

                item["value"] = value
                item["hex"] = hex(value)

                fields.append(item)

            # ------------------------------------------------
            # FIXED64
            # ------------------------------------------------

            elif wire_type == 1:

                if offset + 8 > len(data):
                    raise ValueError("truncated fixed64")

                raw = data[offset:offset + 8]

                offset += 8

                item["raw_hex"] = raw.hex()
                item["value_little_endian"] = int.from_bytes(
                    raw,
                    "little"
                )

                fields.append(item)

            # ------------------------------------------------
            # LENGTH DELIMITED
            # ------------------------------------------------

            elif wire_type == 2:

                length, offset = read_varint(data, offset)

                if length < 0:
                    raise ValueError("negative length")

                if offset + length > len(data):
                    raise ValueError("truncated length-delimited field")

                raw = data[offset:offset + length]

                offset += length

                item["length"] = length
                item["raw_hex"] = raw[:512].hex()

                if looks_printable(raw):
                    item["text_preview"] = safe_text(
                        raw.decode(
                            "utf-8",
                            errors="replace"
                        ),
                        1000
                    )

                # Try nested protobuf only for reasonably sized
                # binary-looking fields.
                if (
                    depth < MAX_PROTO_DEPTH
                    and 0 < len(raw) <= 4096
                    and not looks_printable(raw)
                ):
                    nested = parse_possible_proto(
                        raw,
                        depth + 1
                    )

                    if nested.get("success"):
                        item["nested"] = nested["fields"]

                fields.append(item)

            # ------------------------------------------------
            # FIXED32
            # ------------------------------------------------

            elif wire_type == 5:

                if offset + 4 > len(data):
                    raise ValueError("truncated fixed32")

                raw = data[offset:offset + 4]

                offset += 4

                item["raw_hex"] = raw.hex()

                item["value_little_endian"] = int.from_bytes(
                    raw,
                    "little"
                )

                fields.append(item)

            # ------------------------------------------------
            # UNKNOWN / GROUP
            # ------------------------------------------------

            else:

                item["unsupported"] = True

                fields.append(item)

                raise ValueError(
                    f"unsupported protobuf wire type {wire_type}"
                )

        return {
            "success": True,
            "fields": fields
        }

    except Exception as exc:

        return {
            "success": False,
            "error": str(exc),
            "parsed_fields": fields
        }


# ============================================================
# REQUEST ANALYSIS
# ============================================================

def collect_headers():

    result = {}

    for key, value in request.headers.items():

        # Don't unnecessarily log authorization material.
        lower = key.lower()

        if lower == "authorization":
            result[key] = "[redacted]"
        else:
            result[key] = safe_text(value, 1000)

    return result


def analyze_request(path):

    started = time.time()

    body = request.get_data(cache=True)

    release_version = request.headers.get(
        "Releaseversion",
        ""
    )

    unity_version = request.headers.get(
        "X-Unity-Version",
        ""
    )

    content_type = request.headers.get(
        "Content-Type",
        ""
    )

    proto_result = parse_possible_proto(body)

    analysis = {

        "timestamp": utc_now(),

        "method": request.method,

        "path": "/" + path,

        "release_version": release_version,

        "expected_release": EXPECTED_RELEASE,

        "release_matches_expected": (
            release_version.upper() == EXPECTED_RELEASE
        ),

        "unity_version": unity_version,

        "content_type": content_type,

        "body_length": len(body),

        "sha256": sha256_hex(body),

        "body": {

            "hex": hex_preview(body),

            "printable_preview": printable_preview(
                body,
                1024
            ),

            "base64_preview": b64_preview(
                body,
                1024
            )
        },

        "protobuf": {

            "wire_format_parse_success":
                proto_result.get("success", False),

            "fields":
                proto_result.get(
                    "fields",
                    proto_result.get(
                        "parsed_fields",
                        []
                    )
                ),

            "error":
                proto_result.get("error")
        },

        "headers": collect_headers(),

        "processing_ms":
            round(
                (time.time() - started) * 1000,
                3
            )
    }

    return analysis


# ============================================================
# CONSOLE LOGGER
# ============================================================

def print_analysis(analysis):

    print()
    print("=" * 80)
    print("OB55 PROTOCOL ANALYZER")
    print("=" * 80)

    print(
        "Time:",
        analysis["timestamp"]
    )

    print(
        "Method:",
        analysis["method"]
    )

    print(
        "Path:",
        analysis["path"]
    )

    print(
        "Releaseversion:",
        analysis["release_version"]
    )

    print(
        "Unity:",
        analysis["unity_version"]
    )

    print(
        "Content-Type:",
        analysis["content_type"]
    )

    print(
        "Body:",
        analysis["body_length"],
        "bytes"
    )

    print(
        "SHA256:",
        analysis["sha256"]
    )

    print()
    print("--- BODY HEX ---")

    print(
        analysis["body"]["hex"]
    )

    print()
    print("--- PRINTABLE ---")

    print(
        analysis["body"]["printable_preview"]
    )

    print()
    print("--- PROTOBUF ---")

    protobuf = analysis["protobuf"]

    print(
        "Wire parse:",
        protobuf["wire_format_parse_success"]
    )

    if protobuf.get("error"):
        print(
            "Error:",
            protobuf["error"]
        )

    fields = protobuf.get("fields", [])

    if fields:

        for field in fields[:100]:

            print(
                json.dumps(
                    field,
                    ensure_ascii=False
                )
            )

    else:

        print(
            "No protobuf fields identified."
        )

    print()
    print("--- IMPORTANT HEADERS ---")

    important_headers = [
        "Releaseversion",
        "X-Unity-Version",
        "X-Ga",
        "X-Ga-Sv",
        "Content-Type",
        "Content-Encoding",
        "User-Agent"
    ]

    headers = analysis["headers"]

    for key in important_headers:

        if key in headers:

            print(
                f"{key}: {headers[key]}"
            )

    print()
    print("=" * 80)
    print()


# ============================================================
# JSON RESPONSE
# ============================================================

def analyzer_response(analysis):

    return jsonify({

        "status": "received",

        "server": SERVER_NAME,

        "protocol": {

            "name": "Free Fire HTTP protocol analyzer",

            "release": analysis[
                "release_version"
            ],

            "expected_release": EXPECTED_RELEASE,

            "unity": analysis[
                "unity_version"
            ]
        },

        "request": {

            "method": analysis[
                "method"
            ],

            "path": analysis[
                "path"
            ],

            "body_length": analysis[
                "body_length"
            ],

            "sha256": analysis[
                "sha256"
            ]
        },

        "analysis": {

            "protobuf_parse": analysis[
                "protobuf"
            ]

        },

        "note":
            "Diagnostic response only. "
            "This server does not fabricate "
            "a MajorLoginRes."
    })


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return jsonify({

        "status": "online",

        "server": SERVER_NAME,

        "release": EXPECTED_RELEASE,

        "time": utc_now()

    })


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return jsonify({

        "status": "online",

        "server": SERVER_NAME,

        "protocol": "OB55",

        "mode": "protocol-analyzer",

        "endpoints": [

            "/health",

            "/MajorLogin",

            "/Ping",

            "any other path"

        ]

    })


# ============================================================
# CATCH ALL
# ============================================================

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

    analysis = analyze_request(path)

    print_analysis(analysis)

    response = analyzer_response(
        analysis
    )

    response.headers[
        "X-Analyzer"
    ] = SERVER_NAME

    response.headers[
        "X-Protocol"
    ] = EXPECTED_RELEASE

    return response


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(400)
def bad_request(error):

    return jsonify({

        "status": "error",

        "error": "bad_request"

    }), 400


@app.errorhandler(404)
def not_found(error):

    return jsonify({

        "status": "error",

        "error": "not_found",

        "server": SERVER_NAME

    }), 404


@app.errorhandler(500)
def internal_error(error):

    print(
        "INTERNAL ERROR:",
        repr(error),
        flush=True
    )

    return jsonify({

        "status": "error",

        "error": "internal_server_error"

    }), 500


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    print("=" * 80)
    print("LOGO PC - OB55 PROTOCOL ANALYZER")
    print("=" * 80)

    print(
        "Server:",
        SERVER_NAME
    )

    print(
        "Expected release:",
        EXPECTED_RELEASE
    )

    print(
        "Port:",
        PORT
    )

    print(
        "Listening on 0.0.0.0"
    )

    print("=" * 80)

    app.run(
        host="0.0.0.0",
        port=PORT,
        threaded=True
    )