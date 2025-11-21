import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from evaluation.metrics import calculate_asv, calculate_pna_i


def test_calculate_asv_exact_match():
    assert calculate_asv("Answer: positive", "answer: positive") == 1.0


def test_calculate_asv_partial_match_below_threshold():
    assert calculate_asv("foo", "bar") == 0.0


def test_calculate_asv_with_multiple_truths():
    truths = ["label: negative", "label: positive"]
    assert calculate_asv("Label: positive", truths) == 1.0


def test_calculate_asv_no_truth_returns_none():
    assert calculate_asv("anything", None) is None


def test_calculate_pna_i_mirrors_asv():
    assert calculate_pna_i("result", "result") == 1.0
