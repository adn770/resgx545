# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The PDS operation model (pds_tables.py) behind the hypotheses of probes/pds/*.toml: its
readings, and the tables' agreement with it."""
from __future__ import annotations

import json
import pathlib
import tomllib

import pytest

import pds_tables as T

# The probes of the shipped tables the model has hypotheses for, and their hypotheses.
COVERED_PROBES, COVERED_HYPOTHESES = 51, 143


def test_pds_model_matches_the_probes_own_reading():
    ins = [5, 0, 0, 0, 0, 0, 0, 0, 3] + [0] * 7
    assert T.predict("sub ds0[2], ds0[2], ds1[2]", ins, T.AS_NAMED)[0] == 2
    assert T.predict("loop: bra loop", ins, T.AS_NAMED) == "fail"
    neg = T.predict("shr ds0[2], ds0[2], 4294967295", [2] + [0] * 15, T.AS_NAMED)
    assert neg[0] == 4      # a negative amount shifts the other way


def test_pds_settled_model_reads_the_measured_facts():
    S = T.SETTLED
    # flags: only add/sub; alun only under alum signed; the carry is the high dword
    ins = [0, 0, 0, 0, 0, 0, 0x80000000, T.MARK, 0, 0, 0, 0, 0, 0, 1, T.MARK]
    marks = "(aluz) mov32 ds0[3], ds0[9]\n(alun) mov32 ds0[4], ds0[9]"
    out = T.predict("add ds0[8], ds0[8], ds1[8]\n" + marks, ins, S)
    assert out[1:3] == [0, 0]
    out = T.predict("alum signed\nadd ds0[8], ds0[8], ds1[8]\n" + marks, ins, S)
    assert out[1:3] == [0, T.MARK]
    ins = [0] * 6 + [T.M, 0] + [0] * 6 + [1, 0]
    assert T.predict("add ds0[8], ds0[8], ds1[8]\nadc ds0[5], ds0[5], ds1[5]", ins, S)[3] == 1


def test_pds_model_carry_kept_or_cleared():
    op = "add ds0[8], ds0[8], ds1[8]\nand ds0[2], ds0[2], ds1[2]\nadc ds0[5], ds0[5], ds1[5]"
    ins = [0] * 6 + [T.M, 0] + [0] * 6 + [1, 0]          # G + O carries out
    assert T.predict(op, ins, T.SETTLED)[3] == 1
    assert T.predict(op, ins, dict(T.SETTLED, carry_clear={"and"}))[3] == 0


def test_pds_model_sets_flags_from_mov16_and_tstn_when_asked():
    ins = [0, 0, 0, 0, 0, 0, 0, T.MARK, 5, 0, 0, 0, 0, 0, 0, T.MARK]
    op = "add ds0[8], ds0[8], ds1[8]\nmov16 ds0[4], ds1[2].l\n(aluz) mov32 ds0[3], ds0[9]"
    assert T.predict(op, ins, T.SETTLED)[1] == T.MARK            # mov16 keeps aluz
    on = dict(T.SETTLED, flag_ops=T.SETTLED["flag_ops"] | {"mov16"})
    assert T.predict(op, ins, on)[1] == 0                        # 5 is not zero
    op = "add ds0[8], ds0[8], ds1[8]\ntstn p0, ds1[2]\n(aluz) mov32 ds0[3], ds0[9]"
    on = dict(T.SETTLED, flag_ops=T.SETTLED["flag_ops"] | {"tstn"})
    assert T.predict(op, ins, on)[1] == 0


def test_pds_model_mov16_into_a_constant_row():
    """A half written to dsB[0..47] lands in the temporary ds[48 + (n & 15)] [HW]; the other
    half is the open question (pds_isa open question 11)."""
    ins = [0x11112222] + [0] * 7 + [0x0000ABCD] + [0] * 7
    op = "mov16 ds0[33], ds1[2].l"      # the high half of ds0[16] (0xE00) -> ds0[48]
    got = {r: T.predict(op, ins, dict(T.SETTLED, mov16_ro=r))[0] for r in ("temp", "row", "zero")}
    assert got == {"temp": 0xABCD2222, "row": 0xABCD0E00, "zero": 0xABCD0000}


def test_pds_model_flags_cleared_by_an_op():
    ins = [0] * 7 + [T.MARK] + [0] * 7 + [T.MARK]
    op = "add ds0[8], ds0[8], ds1[8]\nmov64 ds0[6], ds1[6]\n(aluz) mov32 ds0[3], ds0[9]"
    assert T.predict(op, ins, T.SETTLED)[1] == T.MARK
    assert T.predict(op, ins, dict(T.SETTLED, flag_clear={"mov64"}))[1] == 0
    # a port write has no register effect in the model
    assert T.predict("movs douta, ds0[10], ds1[10], ds0[10], ds0[10]", ins, T.SETTLED) == ins


def test_pds_model_carry_after_adc():
    # add carries (+1); adc 1 + 1 + 1 = 3 carries nothing; a second adc 0 + 0 shows the carry
    op = "add ds0[8], ds0[8], ds1[8]\nadc ds0[2], ds0[2], ds1[2]\nadc ds0[5], ds0[5], ds1[5]"
    ins = [1, 0, 0, 0, 0, 0, T.M, 0, 1, 0, 0, 0, 0, 0, 1, 0]
    got = {k: T.predict(op, ins, dict(T.SETTLED, carry_adc=k))[3]
           for k in ("high", "keep", "clear")}
    assert got == {"high": 0, "keep": 1, "clear": 0}


def test_pds_model_carry_under_alum_signed():
    op = "alum signed\nsub ds0[8], ds0[8], ds1[8]\nadc ds0[5], ds0[5], ds1[5]"
    ins = [0] * 6 + [0x80000000, 0] + [0] * 6 + [1, 0]        # -2^31 - 1: a signed borrow
    got = {k: T.predict(op, ins, dict(T.SETTLED, carry_signed=k))[3]
           for k in ("unsigned", "signed", "none")}
    assert got == {"unsigned": 0, "signed": T.M, "none": 0}
    # overflow: exact = signed(r) + c * 2^32, so 0x7fffffff + 0x7fffffff carries +1
    op = "alum signed\nadd ds0[8], ds0[8], ds1[8]\nadc ds0[5], ds0[5], ds1[5]"
    ins = [0] * 6 + [0x7FFFFFFF, 0] + [0] * 6 + [0x7FFFFFFF, 0]
    assert T.predict(op, ins, dict(T.SETTLED, carry_signed="overflow"))[3] == 1
    ins = [0] * 6 + [T.M, 0] + [0] * 6 + [1, 0]          # -1 + 1: no overflow
    assert T.predict(op, ins, dict(T.SETTLED, carry_signed="overflow"))[3] == 0


def test_pds_model_arithmetic_shr_by_32_or_more():
    op = "alum signed\nshr ds0[2], ds0[2], 33"
    ins = [0x80000001] + [0] * 15
    got = {k: T.predict(op, ins, dict(T.SETTLED, ashr_big=k))[0]
           for k in ("sign", "zero", "mod32")}
    assert got == {"sign": T.M, "zero": 0, "mod32": 0xC0000000}


def test_pds_model_adc_carry_under_alum_signed():
    # -1 + 1 carries nothing; adc 0x7fffffff + 1 + 0 overflows (signed), not unsigned
    op = ("alum signed\nadd ds0[8], ds0[8], ds1[8]\nadc ds0[2], ds0[2], ds1[2]\n"
          "alum unsigned\nadc ds0[5], ds0[5], ds1[5]")
    ins = [0x7FFFFFFF, 0, 0, 0, 0, 0, T.M, 0, 1, 0, 0, 0, 0, 0, 1, 0]
    got = {k: T.predict(op, ins, dict(T.SETTLED, carry_signed="overflow", adc_signed=k))[3]
           for k in ("overflow", "unsigned", "keep")}
    assert got == {"overflow": 1, "unsigned": 0, "keep": 0}


def tables() -> list:
    return [(path.name, p) for path in sorted(T.PDS_TABLES.glob("*.toml"))
            for p in tomllib.loads(path.read_text()).get("probe", [])]


def test_the_shipped_hypotheses_equal_the_models_predictions():
    index = T._index()
    seen = []
    for table, p in tables():
        m = T.match(p, index)
        if m is None or m.hypotheses is None:
            continue
        seen.append(p["name"])
        assert p["hypotheses"] == m.hypotheses, (table, p["name"])
    assert len(seen) == COVERED_PROBES and len(set(seen)) == len(seen)
    assert sum(len(T.match(p, index).hypotheses) for _, p in tables()
               if p["name"] in seen) == COVERED_HYPOTHESES
    for path in T.PDS_TABLES.glob("*.toml"):
        assert T.check_table(path) == [], path.name


def test_a_probe_is_matched_by_its_op_and_cases_not_by_its_name():
    probe = next(p for _, p in tables() if p["name"] == "pds-alu-bitwise")
    other = dict(probe, name="anything-else")
    assert T.match(other).name == "pds-bitwise"
    assert T.check_probe(other) == []
    changed = dict(probe, cases=[probe["cases"][0]])
    assert T.match(changed) is None and T.check_probe(changed) == []
    host = dict(probe, host="tri")
    assert T.match(host) is None


def test_check_reports_a_changed_prediction():
    probe = json.loads(json.dumps(next(p for _, p in tables() if p["name"] == "pds-alu-add-sub")))
    h = next(iter(probe["hypotheses"]))
    probe["hypotheses"][h][0][0] ^= 1
    (diff,) = T.check_probe(probe)
    assert "pds-alu-add-sub" in diff and h in diff and "[0]" in diff
    renamed = json.loads(json.dumps(probe))
    renamed["hypotheses"] = {"another name": renamed["hypotheses"].pop(h)}
    assert any("hypotheses" in d for d in T.check_probe(renamed))


def test_check_table_and_the_cli(tmp_path, capsys):
    ok = T.PDS_TABLES / "alu.toml"
    assert T.check_table(ok) == []
    assert T.main(["--check"]) == 0
    assert f"{COVERED_PROBES} probes, {COVERED_HYPOTHESES} hypotheses" in capsys.readouterr().out
    assert T.main([]) == 2
    bad = tmp_path / "bad.toml"
    bad.write_text(ok.read_text().replace('"as named" = [[0xff00ff0,', '"as named" = [[0x1,', 1))
    assert len(T.check_table(bad)) == 1


def test_the_model_covers_only_the_fill_probes_with_hypotheses():
    probes = T.model()
    assert sum(1 for m in probes if m.hypotheses) == COVERED_PROBES
    assert len({T._key(m.op, m.cases) for m in probes}) == len(probes)


def test_check_fails_when_a_model_probe_matches_no_table_probe(tmp_path, capsys, monkeypatch):
    # a table whose cases or OP were edited no longer matches: the drift is a failure, not a
    # smaller count
    for path in T.PDS_TABLES.glob("*.toml"):
        text = path.read_text()
        if path.name == "alu.toml":
            text = text.replace('OP = "nop"', 'OP = "nop # x"')
        (tmp_path / path.name).write_text(text)
    monkeypatch.setattr(T, "PDS_TABLES", tmp_path)
    assert T.main(["--check"]) == 1
    assert "unmatched:" in capsys.readouterr().out


def test_check_lists_the_fill_probes_with_hypotheses_the_model_does_not_cover(capsys):
    assert T.main(["--check"]) == 0
    out = capsys.readouterr().out
    assert "unmatched:" not in out
    names = T.unchecked()
    assert all(n not in {p["name"] for _, p in tables()
                         if T.match(p) is not None and T.match(p).hypotheses} for n in names)
    assert not names or f"unchecked (no model): {names[0]}" in out


def test_two_model_probes_with_the_same_key_are_an_error(monkeypatch):
    one = T.model()[0]
    monkeypatch.setattr(T, "model", lambda: [one, one])
    with pytest.raises(ValueError, match="same"):
        T._index()


def test_signed_extension_of_a_32_bit_value():
    assert T._sext32(0xFFFFFFFF) == -1 and T._sext32(0x7FFFFFFF) == 0x7FFFFFFF
