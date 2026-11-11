# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The closing-session scorer kit (scorekit.py): one case per failure mode of the round-3 scorer
audit (C1 to C11, A1), each drawn from the audit's reproduction, plus the plain cases."""
import pytest

import scorekit as K


# ---- brackets ------------------------------------------------------------------------------
def test_bracket_plain_ladder():
    b = K.bracket([(4, False), (14, False), (56, False), (110, True), (220, True)])
    assert (b.lo, b.hi, b.monotone, b.void_inside) == (56, 110, True, ())


def test_bracket_never_set_is_open_above():
    b = K.bracket([(4, False), (14, False)])
    assert (b.lo, b.hi) == (14, None)


def test_bracket_set_at_the_first_point_is_open_below():
    b = K.bracket([(1760, True), (1978, True)])
    assert (b.lo, b.hi) == (None, 1760)


def test_bracket_void_row_widens_it():
    # C1: the 256x256 n110 row made void; the bracket is (56, 220], with 110 inside it, void
    b = K.bracket([(53, False), (56, False), (110, None), (220, True), (880, True)])
    assert (b.lo, b.hi, b.void_inside) == (56, 220, (110,))


def test_bracket_void_rows_outside_do_not_count():
    b = K.bracket([(4, None), (56, False), (110, True), (880, None)])
    assert (b.lo, b.hi, b.void_inside) == (56, 110, ())


def test_bracket_not_monotone():
    b = K.bracket([(56, False), (110, True), (220, False), (440, True)])
    assert (b.lo, b.hi, b.monotone) == (56, 110, False)


def test_bracket_no_usable_row():
    b = K.bracket([(56, None), (110, None)])
    assert (b.lo, b.hi, b.usable) == (None, None, 0)


def test_bracket_order_of_the_input_does_not_matter():
    assert K.bracket([(110, True), (56, False)]) == K.bracket([(56, False), (110, True)])


# ---- window overlap (A1, C4, C8) -------------------------------------------------------------
def test_overlap_open_lower_end_is_not_zero_and_there_is_no_slack():
    # A1: b4v bracket (None, 1760], HV-INSTR window 2090..2200: the scorer said consistent
    assert K.overlaps((None, 1760), (2090, 2200)) is False


def test_overlap_the_other_q_v_rows_agree():
    # qv_strict.out: the nine rows the strict test and the scorer agreed on, all disjoint
    for br, win in [((601, 649), (522.5, 550.0)), ((601, 649), (402.325, 423.5)),
                    ((None, 1760), (5225, 5500)), ((554, 698), (1045, 1100)),
                    ((554, 698), (261.25, 275.0)), ((329, 538), (65.3125, 68.75))]:
        assert K.overlaps(br, win) is False


def test_overlap_ends():
    assert K.overlaps((100, 200), (200, 300)) is True        # hi is inside the bracket
    assert K.overlaps((100, 200), (50, 100)) is False        # lo is not
    assert K.overlaps((100, 200), (50, 100.5)) is True
    assert K.overlaps((100, 200), (201, 300)) is False


def test_overlap_open_ends_of_the_window():
    # C4: a one-sided window is written with None, not with a zero or a large number
    assert K.overlaps((100, 200), (None, 150)) is True
    assert K.overlaps((100, 200), (None, 100)) is False
    assert K.overlaps((100, 200), (250, None)) is False
    assert K.overlaps((None, None), (5, 6)) is True


def test_overlap_not_containment():
    # C8: c1_verdict / ladder_verdict used containment; [0x356, 0x36e) overlaps [0x35e, 0x37e)
    assert K.overlaps((0x356, 0x36e), (0x35e, 0x37e)) is True
    assert K.contains((0x356, 0x36e), (0x35e, 0x37e)) is False


def test_overlap_takes_a_bracket():
    assert K.overlaps(K.bracket([(1760, True)]), (2090, 2200)) is False


def test_overlap_refuses_a_reversed_window():
    with pytest.raises(ValueError):
        K.overlaps((1, 2), (5, 3))


# ---- exact points (C1, A3) -------------------------------------------------------------------
LADDER = [53, 56, 110, 220, 880]


def test_point_held_on_a_tight_bracket():
    b = K.bracket([(53, False), (56, False), (110, True), (220, True)])
    assert K.point_verdict(b, {110}) is True
    assert K.point_verdict(b, {220}) is False


def test_point_void_row_in_the_bracket_is_cannot_tell():
    # C1: kept 256x256 read ok; with n110 void it read MISS. Now: cannot tell
    b = K.bracket([(53, False), (56, False), (110, None), (220, True), (880, True)])
    assert K.point_verdict(b, {110}) is None
    assert K.point_verdict(b, {220}) is None


def test_point_refuted_only_when_every_allowed_point_is_outside():
    b = K.bracket([(53, False), (56, False), (110, None), (220, True), (880, True)])
    assert K.point_verdict(b, {53, 880}) is False
    assert K.point_verdict(b, {53, 110}) is None


def test_point_open_ends_never_hold():
    above = K.bracket([(53, False), (56, False)])
    assert K.point_verdict(above, {110}) is None
    assert K.point_verdict(above, {53}) is False
    below = K.bracket([(56, True), (110, True)])
    assert K.point_verdict(below, {56}) is None
    assert K.point_verdict(below, {110}) is False


def test_point_several_allowed_points_all_possible():
    b = K.bracket([(56, False), (110, None), (220, True)])
    assert K.point_verdict(b, {110, 220}) is True


def test_point_no_usable_row_is_cannot_tell():
    assert K.point_verdict(K.bracket([(56, None), (110, None)]), {110}) is None


def test_point_reference_range():
    # A3: a hypothesis scaled from a reference that is itself a bracket: allowed points for every
    # reference the bridge allows; one point inside is enough to not refute
    b = K.bracket([(56, False), (220, True), (880, True)])
    assert K.point_verdict(b, {220}) is True
    assert K.point_verdict(b, {880}) is False


# ---- controls (C2, C7, C11) ------------------------------------------------------------------
def test_gate_all_pass():
    g = K.gate({"c1": "PASS", "c2": True})
    assert g.ok and g.problems == []


def test_gate_nodata_gates():
    # C2: k-f4 with the c3 control's output deleted still printed 8 of 8 AGREES
    g = K.gate({"c3-64x64-k1": "NODATA", "c2-64x64-k4": "PASS", "c1-288x144-k1": "PASS"})
    assert not g.ok and g.problems == ["c3-64x64-k1: NODATA"]


def test_gate_cannot_tell_gates():
    # B6: ctl_ok = all(k is not False ...) passed a cannot-tell proof
    g = K.gate({"t0": None, "t2": True})
    assert not g.ok and g.problems == ["t0: cannot tell"]


def test_gate_failed():
    g = K.gate({"am": False})
    assert not g.ok and g.failed == ["am"] and g.problems == ["am: FAILED"]


def test_gate_refuses_values_that_are_not_states():
    # C11: ctl.get("c-e709", (False,))[0] is not None was always true; a tuple is no state
    with pytest.raises(TypeError):
        K.gate({"c-e709": (False,)})
    with pytest.raises(ValueError):
        K.gate({"x": "ok-ish"})


def test_gate_with_no_control_is_shut():
    g = K.gate({})
    assert not g.ok and g.problems == ["no control"]


def test_gated_row_every_dependent_row():
    # C7: a failed control gated some rows only; every dependent row is cannot tell
    g = K.gate({"am": False})
    rows = [True, False, None]
    assert [K.gated(g, r) for r in rows] == [None, None, None]
    assert [K.gated(K.gate({"am": True}), r) for r in rows] == rows


# ---- tallies and replicates (B4, C5, C6) ----------------------------------------------------
def test_tally_counts_decided_rows_apart():
    t = K.tally([True, True, None, False, None])
    assert (t.held, t.failed, t.cannot_tell, t.decided) == (2, 1, 2, 3)
    assert str(t) == "2 held, 1 FAILED, 2 cannot tell of 5"


def test_tally_held_needs_a_decided_row():
    # C5: jobs the rows call cannot tell are not counted for the stage hypothesis
    assert K.tally([None, None]).verdict() is None
    assert K.tally([True, None]).verdict() is True
    assert K.tally([True, False]).verdict() is False


def test_combine_replicates():
    # C6: `elif False in ks` printed supported when one rep stopped of three
    assert K.combine([True, True, True]) == "held"
    assert K.combine([False, False]) == "refuted"
    assert K.combine([True, True, False]) == "mixed"
    assert K.combine([True, None]) == "cannot tell"
    assert K.combine([]) == "cannot tell"


# ---- headlines (C3, C9, C10) ----------------------------------------------------------------
def test_headline_no_data_is_cannot_tell():
    # C3: every job record deleted; "defaults as designed" still printed
    h = K.headline("defaults as designed", {"K0 defaults": None}, [None])
    assert h == "cannot tell: no row decided; controls: K0 defaults: cannot tell"


def test_headline_kept_data():
    h = K.headline("defaults as designed", {"K0 defaults": True}, [True])
    assert h == "defaults as designed (1 of 1 rows decided)"


def test_headline_failed_control():
    h = K.headline("x", {"a": False, "b": True}, [True, True])
    assert h == "controls FAILED: a: FAILED"


def test_headline_cannot_tell_control():
    h = K.headline("x", {"a": "NODATA", "b": True}, [True])
    assert h == "cannot tell: controls: a: NODATA"


def test_headline_rows_read_but_refuting():
    # C10: rows were read and matched none: not "no row could be read"
    h = K.headline("x", {"a": True}, [False, False, False, False])
    assert h == "x is not supported: 0 held, 4 FAILED, 0 cannot tell of 4"


def test_headline_says_how_many_rows_decided():
    # C9: a headline resting on one decided row of 12 says so
    h = K.headline("consistent with H-LATCH, H-HWC", {"a": True}, [True] + [None] * 11)
    assert h == "consistent with H-LATCH, H-HWC (1 of 12 rows decided)"


def test_headline_mixed_rows():
    h = K.headline("x", {"a": True}, [True, False, None])
    assert h == "x is not supported: 1 held, 1 FAILED, 1 cannot tell of 3"
