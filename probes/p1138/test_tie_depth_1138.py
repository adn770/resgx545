"""tests of tie_depth_1138.py: the rounding rules and the tie detection (stdlib)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tie_depth_1138 as T  # noqa: E402


def test_rounded_half_up_and_down_at_a_tie():
    # K = 12: a grid unit is 16 units; 8 is the exact half
    assert T.rounded([8, 24, 7, 9], 12, "up") == [1, 2, 0, 1]
    assert T.rounded([8, 24, 7, 9], 12, "down") == [0, 1, 0, 1]


def test_rounded_k16_unit_is_256():
    assert T.rounded([128, 127, 129, 256 + 128], 16, "up") == [1, 0, 1, 2]
    assert T.rounded([128], 16, "down") == [0]


def test_rounded_grid_k8_is_identity():
    assert T.rounded([5, 10], 8, "up") == [5, 10]


def test_frac_at_finds_ties_and_127():
    assert T.frac_at([8, 16, 24, 7], 12, 128) == [0, 2]
    assert T.frac_at([127, 128, 383, 0], 16, 127) == [0, 2]
    assert T.frac_at([127, 128, 383, 0], 16, 128) == [1]
