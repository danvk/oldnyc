#!/usr/bin/env python

import base64
import io
import json
import math
import sys

from PIL import Image
import binpacking


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

    # First pass: estimate the costs of all inputs
    id_to_cost: dict[str, int] = {}
    for input in sys.argv[1:]:
        for line_str in open(input):
            req = json.loads(line_str)
            tokens = estimate_request_tokens(req)
            id = req['custom_id']
            assert id not in id_to_cost, f'Duplicate id: {id}'
            id_to_cost[id] = tokens

    bins = binpacking.to_constant_volume(id_to_cost, MAX_TOKENS * 0.9)
    bins = binpacking.to_constant_bin_number(id_to_cost, len(bins))

    for i, bin in enumerate(bins):
        total = sum(bin.values())
        print(f'{i}: {total}')
