#!/usr/bin/env python

import base64
import io
import json
import math
import sys

from PIL import Image


def as_list(x):
    if isinstance(x, list):
        return x
    return [x]


# TODO: make this a function of model
MAX_TOKENS = 2_000_000
# MAX_TOKENS = 90_000

# https://openai.com/api/pricing/
model_image_tokens = {
    'gpt-4o-mini': (2833, 5667),
    'gpt-4o': (85, 170),
}
max_size = (2048, 768)


def image_tokens(image_base64: str, model: str) -> int:
    data = image_base64.split(',', 1)[1]
    data_bytes = base64.b64decode(data)
    im = Image.open(io.BytesIO(data_bytes))
    w, h = im.size
    scale = 1
    maxw, maxh = max_size
    scale = min(1, maxw / w, maxh / h)
    w *= scale
    h *= scale
    tiles = math.ceil(w / 512) * math.ceil(h / 512)
    base, marginal = model_image_tokens[model]
    return base + tiles * marginal


def estimate_request_tokens(req: dict) -> int:
    body = req['body']
    messages = body['messages']
    tokens = 0
    for message in messages:
        submessages = as_list(message['content'])
        for submessage in submessages:
            if isinstance(submessage, str):
                tokens += len(submessage) / 4
            elif submessage['type'] == 'image_url':
                tokens += image_tokens(submessage['image_url']['url'], body['model'])
            else:
                raise ValueError(submessage['type'])

    return tokens


if __name__ == '__main__':
    total_tokens = 0
    shard = 0
    requests = []

    def dump():
        global shard
        global requests
        global total_tokens
        outpath = 'shard-%03d.jsonl' % shard
        with open(outpath, 'w') as out:
            for req in requests:
                json.dump(req, out)
                out.write('\n')
        print(f'{outpath}: {len(requests)} requests, {total_tokens} tokens')
        requests = []
        shard += 1
        total_tokens = 0

    for input in sys.argv[1:]:
        for line_str in open(input):
            req = json.loads(line_str)
            tokens = estimate_request_tokens(req)
            id = req['custom_id']
            # print(f'{id}\t{tokens}')
            requests.append(req)
            total_tokens += tokens

            # assume 100 output tokens/request, plus some padding
            if total_tokens * 1.1 + 100 * len(requests) > MAX_TOKENS:
                dump()

    if requests:
        dump()
