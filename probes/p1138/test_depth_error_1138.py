"""tests of depth_error_1138.py: the exact plane, the float32 conversions, the E465 index (stdlib)"""
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import depth_error_1138 as D  # noqa: E402


def test_plane_exact_at_vertices():
    case = dict(v=[5120, 5120, 5120, 11264, 10240, 8192], z=[346, 842, 608])
    a, b, c = D.plane(case)
    assert a * 20 + b * 20 + c == Fraction(346, 1024)
    assert a * 20 + b * 44 + c == Fraction(842, 1024)
    assert a * 40 + b * 32 + c == Fraction(608, 1024)


def test_plane_degenerate_is_none():
    assert D.plane(dict(v=[0, 0, 256, 256, 512, 512], z=[0, 0, 0])) is None


def test_f32_roundings():
    x = Fraction(3, 4) + Fraction(1, 1 << 30)
    nearest = D.f32_round_nearest(x)
    assert D.bits_f32(nearest) == 0.75
    up = Fraction(3, 4) - Fraction(1, 1 << 30)
    assert D.f32_truncate(up) == D.f32_bits(0.75) - 1
    assert D.f32_truncate(Fraction(3, 4)) == D.f32_bits(0.75)


def test_true_ulp():
    assert D.true_ulp(Fraction(1)) == Fraction(1, 1 << 23)
    assert D.true_ulp(Fraction(3, 4)) == Fraction(1, 1 << 24)


def test_depth_index_origin_and_tile():
    assert D.depth_index(0, 0, 1) == 0
    assert D.depth_index(1, 0, 1) == 2
    assert D.depth_index(0, 1, 1) == 1
    assert D.depth_index(32, 0, 1) == 512
    assert D.depth_index(0, 16, 1) == 1024


def test_covered_pixels_reads_rows():
    text = "row 0: 0xff203040 0x11\nrow 1: 0x22 0xff203040\n"
    assert D.covered_pixels(text, 2, 2) == [(1, 0), (0, 1)]
    assert D.covered_pixels(text, 2, 3) is None
