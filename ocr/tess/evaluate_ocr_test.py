import Levenshtein
from ocr.tess.evaluate_ocr import contiguous_chunks, normalize_whitespace, try_transpositions


def test_contiguous_chunks():
    assert contiguous_chunks([1, 2, 3, 5, 6, 7]) == [[1, 2, 3], [5, 6, 7]]
    assert contiguous_chunks([1, 3, 5, 6, 7]) == [[1], [3], [5, 6, 7]]
    assert contiguous_chunks([1, 3, 4, 7]) == [[1], [3, 4], [7]]


def test_try_transpositions():
    # 730730b
    base_lines = [
        "The Brooklyn Bridge and Manhattan's Wall Street outline as photographed southwestward from the Manhattan Bridge.",
        "",
        "1939",
        "Alexander Alland",
        "Neg. # 4069"
    ]
    exp_text = normalize_whitespace('''The Brooklyn Bridge and Manhattan's Wall Street outline as photographed southwestward from the Manhattan Bridge.

Alexander Alland

Neg. # 4069

1939''')

    d = Levenshtein.distance(normalize_whitespace('\n'.join(base_lines)), exp_text)
    assert d == 10

    d = try_transpositions(base_lines, exp_text, d)
    assert d == 0
    assert base_lines == [
        "The Brooklyn Bridge and Manhattan's Wall Street outline as photographed southwestward from the Manhattan Bridge.",
        "",
        "Alexander Alland",
        "Neg. # 4069",
        "1939",
    ]
