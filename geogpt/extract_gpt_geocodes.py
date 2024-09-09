#!/usr/bin/env python
"""Extract photo ID -> geocodable string mapping from GPT JSONL output files."""

import json
import sys


IGNORE_GEOCODES = {
    'not in NYC',
    'no location information',
}


if __name__ == '__main__':
    out = {}
    for path in sys.argv[1:]:
        outputs = [json.loads(line) for line in open(path)]
        for r in outputs:
            id = r['custom_id']
            response = r['response']
            assert response['status_code'] == 200
            choices = response['body']['choices']
            assert len(choices) == 1
            data_str = choices[0]['message']['content']
            data = json.loads(data_str)
            gpt_location = data['location']
            if gpt_location in IGNORE_GEOCODES:
                continue
            out[id] = gpt_location

    print(json.dumps(out, indent=2, sort_keys=True))
