#!/usr/bin/env python
"""Evaluates the performance of an OCR program.

Requires two sets of text files: golden files and run files.
The files are paired up and normalized for whitespace.

The score for each pair is the Levenshtein distance between them divided by the
length of the golden file. These scores are averaged across all pairs to get an
overall score.
"""

import json
import re
import sys

import Levenshtein


def normalize_whitespace(text):
    s = re.compile(r'\s+')
    return ' '.join([x for x in s.split(text) if x])


def advance1(i: int, ary: list[str]) -> int | None:
    j = i + 1
    while j < len(ary):
        if ary[j]:
            return j
        j += 1
    return None


def try_transpositions(in_lines: list[str], exp_text: str, d: float) -> float:
    any_changes = False
    for i in range(0, len(in_lines) - 1):
        a = in_lines[i]
        if len(a) > 30:
            continue
        for delta in range(1, 3):
            j = i
            for _ in range(0, delta):
                j = advance1(j, in_lines)
                if j is None:
                    break

            if j is None:
                continue
            b = in_lines[j]
            if len(b) > 30:
                continue
            lines = in_lines[:]
            lines[i], lines[j] = lines[j], lines[i]
            dt = Levenshtein.distance(normalize_whitespace('\n'.join(lines)), exp_text)
            if dt < d:
                print(f'  swap {i}, {j}: {d} -> {dt}')
                in_lines[i], in_lines[j] = in_lines[j], in_lines[i]
                d = dt
                any_changes = True
            else:
                # pass
                print(f'  reject swap {i}, {j}: {d} -> {dt}')

    if any_changes:
        return try_transpositions(in_lines, exp_text, d)
    return d


def score_for_pair(golden_text, run_text):
    run_text = normalize_whitespace(run_text)
    d = Levenshtein.distance(normalize_whitespace(golden_text), run_text)

    golden_lines = golden_text.split('\n')
    print(json.dumps(golden_lines, indent=2))
    d = try_transpositions(golden_lines, run_text, d)
    adjusted_golden = '\n'.join(golden_lines)

    #sys.stderr.write('d: %d (%d vs. %d)\n' % (d, len(run_text), len(golden_text)))
    return (max(0.0, 1.0 - 1.0 * d / len(golden_text)), d, adjusted_golden)


if __name__ == '__main__':
    files = sys.argv[1:]
    assert len(files) % 2 == 0
    pairs = [(files[i], files[i+1]) for i in range(0, len(files), 2)]

    scores = []
    for golden, run in pairs:
        golden_text = open(golden).read()
        run_text = open(run).read()
        (d, _) = score_for_pair(golden_text, run_text)
        print('%.3f  %s %s' % (d, golden, run))
        scores.append(d)

    mean = sum(scores) / len(scores)
    print('Average: %.3f' % mean)
