import Levenshtein
from ocr.tess.evaluate_ocr import contiguous_chunks, normalize_whitespace, try_transpositions


def test_contiguous_chunks():
    assert contiguous_chunks([1, 2, 3, 5, 6, 7]) == [[1, 2, 3], [5, 6, 7]]
    assert contiguous_chunks([1, 3, 5, 6, 7]) == [[1], [3], [5, 6, 7]]
    assert contiguous_chunks([1, 3, 4, 7]) == [[1], [3, 4], [7]]


def test_try_transpositions():
    # 730730b
    base_text = '\n'.join([
        "The Brooklyn Bridge and Manhattan's Wall Street outline as photographed southwestward from the Manhattan Bridge.",
        "",
        "1939",
        "Alexander Alland",
        "Neg. # 4069"
    ])
    exp_text = normalize_whitespace('''The Brooklyn Bridge and Manhattan's Wall Street outline as photographed southwestward from the Manhattan Bridge.

Alexander Alland

Neg. # 4069

1939''')

    d = Levenshtein.distance(normalize_whitespace(base_text), exp_text)
    assert d == 10

    d, adjusted_text = try_transpositions(base_text, exp_text)
    assert d == 0
    assert adjusted_text == '\n'.join([
        "The Brooklyn Bridge and Manhattan's Wall Street outline as photographed southwestward from the Manhattan Bridge.",
        "",
        "Alexander Alland",
        "Neg. # 4069",
        "1939",
    ])
