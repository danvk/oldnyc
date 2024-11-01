import base64
import json
from typing import Any


def encode_json_base64(o: Any) -> str:
    return base64.b64encode(json.dumps(o).encode("utf8")).decode("utf8")


def decode_json_base64(b64: str):
    return json.loads(base64.b64decode(b64).decode("utf-8"))
