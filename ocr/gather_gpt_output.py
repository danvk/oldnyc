#!/usr/bin/env python
"""Gather output from a GPT batch JSONL into a JSON file for evaluation."""

import json
import sys

from ocr.cleaner import clean



if __name__ == '__main__':
    gpt_output_file = sys.argv[1]
    gpt_data = [
        json.loads(line) for line in open(gpt_output_file)
    ]

    mapping = {}
    for r in gpt_data:
        back_id = r['custom_id']
        response = r['response']
        assert response['status_code'] == 200
        choices = response['body']['choices']
        assert len(choices) == 1
        gpt_text: str = choices[0]['message']['content']
        for delim in ('```', '---'):
            if delim in gpt_text:
                gpt_text = gpt_text.split(delim)[1]
                break
        if gpt_text.startswith('**Transcription:**') or gpt_text.startswith('**Transcription of the text:**'):
            gpt_text = gpt_text.split('\n', 1)[1]
        gpt_text = gpt_text.strip() + '\n'
        mapping[back_id] = clean(gpt_text)

    print(json.dumps(mapping, indent=2))
