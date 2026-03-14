import base64
import json
from typing import Any, Sequence


def encode_json_base64(o: Any) -> str:
    return base64.b64encode(json.dumps(o).encode("utf8")).decode("utf8")


def decode_json_base64(b64: str):
    return json.loads(base64.b64decode(b64).decode("utf-8"))


def pick[K, V](o: dict[K, V], fields: Sequence[K]) -> dict[K, V]:
    return {k: o[k] for k in fields if k in o}


def remove_empty(obj):
    return {
        k: (remove_empty(v) if isinstance(v, dict) else v)
        for k, v in obj.items()
        if v is not None and v != []
    }
