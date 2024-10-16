#!/usr/bin/env python
"""Converts the output of extract-images.py into a nice JSON object.

Output looks like:
  {
    '702370f.jpg': {
      'crops': {
        '702370f-1.jpg': { top: 10, left: 20, width: 400, height: 300},
        '702370f-2.jpg': { top: 10, left: 20, width: 400, height: 300},
        '702370f-3.jpg': { top: 10, left: 20, width: 400, height: 300}
      },
      'metadata': {
        'width': 1000,
        'height': 800
      }
    }
  }
"""

import fileinput
import json
import os

out = {}
for line in fileinput.input():
    d = json.loads(line)
    crops = {}
    if "rects" in d:
        for r in d["rects"]:
            crops[os.path.basename(r["file"])] = {
                "top": r["top"],
                "left": r["left"],
                "width": r["right"] - r["left"],
                "height": r["bottom"] - r["top"],
            }
    out[os.path.basename(d["file"])] = {
        "crops": crops,
        "metadata": {"width": d["shape"]["w"], "height": d["shape"]["h"]},
    }

print(json.dumps(out, indent=2, sort_keys=True))
