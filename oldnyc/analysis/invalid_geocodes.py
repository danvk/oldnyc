"""How many old geocodes are invalid?"""

import base64
import binascii
import json
import re
from pathlib import Path


def softdecode(s: str) -> str:
    try:
        for i in range(0, 4):
            try:
                q = base64.b64decode(s).decode("latin-1")
                return q
            except binascii.Error:
                s = s[:-1]
    except UnicodeDecodeError:
        print(f"Cannot decode: {s}")
        raise
    raise ValueError(f"Cannot decode: {s}")


def main():
    geocache = Path("geocache")
    n_cache = 0
    n_int_q = 0
    n_hit, n_zero, n_miss = 0, 0, 0
    n_old_miss, n_new_miss = 0, 0
    out = open("/tmp/failed-geocodes.ndjson", "w")
    for path in geocache.iterdir():
        n_cache += 1
        query = softdecode(path.name)
        if not re.search(r"&|\band\b", query):
            continue

        n_int_q += 1
        with open(path) as f:
            data = json.load(f)
        assert "results" in data, path
        if data["status"] == "ZERO_RESULTS":
            n_zero += 1
            continue
        assert len(data["results"]) > 0, path
        if "intersection" in data["results"][0]["types"]:
            n_hit += 1
        else:
            n_miss += 1
            is_old = path.stat().st_mtime < 1447339825  # 2015-11-12
            if is_old:
                n_old_miss += 1
            else:
                n_new_miss += 1
            out.write(json.dumps({"query": query, "data": data}))
            out.write("\n")

    print(f"Cache: {n_cache}")
    print(f"Intersection queries: {n_int_q}")
    print(f"Hit: {n_hit}")
    print(f"Zero results: {n_zero}")
    print(f"Miss: {n_miss}")
    print(f"{n_new_miss=}, {n_old_miss=}")


if __name__ == "__main__":
    main()
