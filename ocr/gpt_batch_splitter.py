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


MAX_TOKENS = {
    'gpt-4o-mini': 2_000_000,
    'gpt-4o': 90_000,
}

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

    return int(tokens)


if __name__ == '__main__':
    total_tokens = 0

    # First pass: estimate the costs of all inputs, assign each to a bucket
    id_to_cost: dict[str, int] = {}
    model = None
    for input in sys.argv[1:]:
        for line_str in open(input):
            req = json.loads(line_str)
            m = req['body']['model']
            if model is None:
                model = m
            elif m != model:
                sys.stderr.write(
                    f'All requests must use the same model (found {model}, {m})\n')
                sys.exit(1)
            tokens = estimate_request_tokens(req)
            id = req['custom_id']
            assert id not in id_to_cost, f'Duplicate id: {id}'
            id_to_cost[id] = tokens

    bins = binpacking.to_constant_volume(id_to_cost, MAX_TOKENS[model] * 0.9)
    bins = binpacking.to_constant_bin_number(id_to_cost, len(bins))

    id_to_bin: dict[str, int] = {
        id: i
        for i, bin in enumerate(bins)
        for id in bin.keys()
    }
    N = len(bins)
    print(f'Model: {model}')
    print(f'Will use {N} shards for', sum(id_to_cost.values()), 'tokens.')
    for i, bin in enumerate(bins):
        total = sum(bin.values())
        print(f'{i}: ~{total} tokens')

    # Second pass: Write each task out to the appropriate JSONL shard.
    shard_pattern = 'shard-%03d-of-%03d.jsonl'
    for i in range(len(bins)):
        with open(shard_pattern % (i, N), 'w') as out:
            pass  # make sure to clear any existing files before appending

    for input in sys.argv[1:]:
        for line_str in open(input):
            req = json.loads(line_str)
            id = req['custom_id']

            shard = id_to_bin[id]
            with open(shard_pattern % (shard, N), 'a') as out:
                json.dump(req, out)
