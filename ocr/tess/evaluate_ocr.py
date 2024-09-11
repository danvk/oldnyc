#!/usr/bin/env python
"""Evaluates the performance of an OCR program.

Requires two sets of text files: golden files and run files.
The files are paired up and normalized for whitespace.

The score for each pair is the Levenshtein distance between them divided by the
length of the golden file. These scores are averaged across all pairs to get an
overall score.
"""

import re
import sys

import Levenshtein


def normalize_whitespace(text):
    s = re.compile(r'\s+')
    return ' '.join([x for x in s.split(text) if x])


def score_for_pair(golden_text, run_text):
    golden_text = normalize_whitespace(golden_text)
    run_text = normalize_whitespace(run_text)
    d = Levenshtein.distance(golden_text, run_text)
    #sys.stderr.write('d: %d (%d vs. %d)\n' % (d, len(run_text), len(golden_text)))
    return (max(0.0, 1.0 - 1.0 * d / len(golden_text)), d)


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
