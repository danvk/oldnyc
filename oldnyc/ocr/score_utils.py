#!/usr/bin/env python
"""Evaluates the performance of an OCR program.

Requires two sets of text files: golden files and run files.
The files are paired up and normalized for whitespace.

The score for each pair is the Levenshtein distance between them divided by the
length of the golden file. These scores are averaged across all pairs to get an
overall score.
"""

import itertools
import re
import sys

import Levenshtein


def normalize_whitespace(text: str):
    s = re.compile(r"\s+")
    return " ".join([x for x in s.split(text) if x])


def contiguous_chunks(xs: list[int]) -> list[list[int]]:
    if not xs:
        return []
    short_chunks = [[xs[0]]]
    for i in xs[1:]:
        if i == short_chunks[-1][-1] + 1:
            short_chunks[-1].append(i)
        else:
            short_chunks.append([i])
    return short_chunks


def try_transpositions(base_txt: str, exp_text: str, name: str = "") -> tuple[int, str]:
    d = Levenshtein.distance(normalize_whitespace(base_txt), exp_text)
    in_lines = base_txt.split("\n")
    short_lines = [i for i, line in enumerate(in_lines) if len(line) <= 30]
    if not short_lines:
        return d, base_txt

    short_chunks = contiguous_chunks(short_lines)
    for chunk in short_chunks:
        if len(chunk) > 6:
            # too many; not worth the computation!
            # TODO: ignore blank lines here, they'll be normalized away
            continue
        best_perm = (d, chunk)
        for perm in itertools.permutations(chunk):
            lines = in_lines[:]
            for before, after in zip(chunk, perm):
                lines[after] = in_lines[before]
            dt = Levenshtein.distance(normalize_whitespace("\n".join(lines)), exp_text)
            if dt < best_perm[0]:
                best_perm = (dt, perm[:])

        if best_perm[0] < d:
            dt, perm = best_perm
            # print(f"{name} apply permutation {perm}: {d} -> {dt}")
            d = dt
            lines = in_lines[:]
            for before, after in zip(chunk, perm):
                in_lines[after] = lines[before]

    out_txt = "\n".join(in_lines)
    return d, out_txt


def score_for_pair(golden_text: str, run_text: str, name=""):
    run_text = normalize_whitespace(run_text)
    d, adjusted_golden = try_transpositions(golden_text, run_text, name)

    if len(golden_text) == 0:
        if len(run_text) == 0:
            score = 1
        else:
            score = 0
    else:
        score = max(0.0, 1.0 - 1.0 * d / len(golden_text))

    # sys.stderr.write('d: %d (%d vs. %d)\n' % (d, len(run_text), len(golden_text)))
    return (score, d, adjusted_golden)


if __name__ == "__main__":
    files = sys.argv[1:]
    assert len(files) % 2 == 0
    pairs = [(files[i], files[i + 1]) for i in range(0, len(files), 2)]

    scores = []
    for golden, run in pairs:
        golden_text = open(golden).read()
        run_text = open(run).read()
        (d, _, _) = score_for_pair(golden_text, run_text)
        print("%.3f  %s %s" % (d, golden, run))
        scores.append(d)

    mean = sum(scores) / len(scores)
    print("Average: %.3f" % mean)
