#!/usr/bin/env python
"""Gather output from a GPT batch JSONL into a JSON file for evaluation."""

import json
import sys

from ocr.cleaner import clean



if __name__ == '__main__':
    gpt_data = [
        json.loads(line)
        for gpt_output_file in sys.argv[1:]
        for line in open(gpt_output_file)
    ]

    mapping = {}
    for r in gpt_data:
        back_id = r['custom_id']
        response = r['response']
        assert response['status_code'] == 200
        choices = response['body']['choices']
        assert len(choices) == 1
        data_str = choices[0]['message']['content']
        try:
            data = json.loads(data_str)
        except json.decoder.JSONDecodeError:
            sys.stderr.write(f'JSON response for {back_id} is malformed.\n')
            data_str += '"}'
            data = json.loads(data_str)
        rotated = data.get('rotated')
        gpt_text = data['text']
        mapping[back_id] = {
            'text': clean(gpt_text) if not rotated else '(rotated)',
            'original': gpt_text
        }
        if rotated:
            sys.stderr.write(f'GPT says {back_id} is rotated.\n')

    print(json.dumps(mapping, indent=2))
