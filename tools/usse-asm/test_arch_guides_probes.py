# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The probes motivated by Imagination's public Rogue instruction set reference (special
constants, globals, internal registers as load targets and index bases, the output bank's
preload, .skipinv per instance), in probes/usse/{constant-banks,internal-registers,
output-registers,instance-masking}.toml. Hardware runs are not tested here: only that the
tables load, that every case assembles and that their hypotheses (if any) are well formed."""
from __future__ import annotations

import pathlib
import re

import pytest

import probe

HERE = pathlib.Path(__file__).resolve().parent
USSE = probe.PROBES / "usse"
SRC = USSE / "templates"
# the probes, by the old short name, in the tables that hold them
NAMES = {"cbank": "constant-banks", "gbank": "constant-banks", "ireg-ldad": "internal-registers",
         "ireg-ldr": "internal-registers", "ireg-index": "internal-registers",
         "o-preload": "output-registers", "skipinv-inst": "instance-masking",
         "skipinv-grad": "instance-masking"}


def full(short: str) -> str:
    return f"usse-{NAMES[short]}-{short}"


@pytest.fixture(scope="module")
def table():
    out = []
    for feature in sorted(set(NAMES.values())):
        out += [p for p in probe.load(USSE / f"{feature}.toml")
                if p.name in {full(s) for s in NAMES}]
    return out


def test_table_loads(table):
    names = [p.name for p in table]
    assert set(names) == {full(s) for s in NAMES}
    assert len(names) == len(set(names))
    for p in table:
        assert probe.NAME_RE.fullmatch(p.name), p.name
        assert p.cases and p.question, p.name
        assert len(p.labels) == len(p.cases), p.name



def test_every_case_assembles(table, tmp_path):
    for p in table:
        files = probe.build(p, tmp_path, SRC)
        assert len(files) == len(p.cases), p.name
        assert all(f.stat().st_size > 0 for f in files), p.name


def test_recorded_probes_have_no_hypotheses(table):
    predicted = {full("skipinv-inst")}
    for p in table:
        if p.name not in predicted:
            assert p.hypotheses == {}, p.name


def test_predictions_cover_cases_and_differ_pairwise(table):
    p = next(p for p in table if p.name == full("skipinv-inst"))
    assert len(p.hypotheses) >= 2
    vecs = list(p.hypotheses.values())
    for name, v in p.hypotheses.items():
        assert len(v) == len(p.cases), name
    for i, a in enumerate(vecs):
        for b in vecs[i + 1:]:
            assert repr(a) != repr(b)
            # they differ on at least one case, not only in form
            assert any(repr(x) != repr(y) for x, y in zip(a, b))


def test_bank_probes_cover_the_whole_bank(table):
    # cbank / gbank name every register of their half of bank 5 at least once
    for short, prefix in (("cbank", "c"), ("gbank", "g")):
        p = next(p for p in table if p.name == full(short))
        text = "\n".join(str(v) for case in p.cases for v in case)
        named = set(re.findall(rf"\b{prefix}(\d+)\b", text))
        assert named == {str(n) for n in range(64)}, short


def test_gbank_never_writes_a_global(table):
    p = next(p for p in table if p.name == full("gbank"))
    src = (SRC / p.source).read_text()
    for case in p.cases:
        text = probe.render(p, case, src)
        for line in text.splitlines():
            ops = line.split(";")[0].split(None, 1)
            if len(ops) == 2 and not ops[0].startswith("st"):
                dst = ops[1].split(",")[0].strip()
                assert not dst.startswith("g"), line


def test_skipinv_probe_stores_only_o0(table):
    # instances that may be invalid must not store anywhere but their own o0
    for p in table:
        if p.name.startswith("usse-instance-masking-skipinv"):
            text = "\n".join(str(v) for case in p.cases for v in case)
            assert not any(w.startswith("st") for w in text.split()), p.name
            assert p.coords and p.pixels, p.name


def test_o_preload_target_is_painted(table):
    """A preloaded o0 is told from zero: the host paints the fill target with its sentinel
    before the probe runs (sgxfive-test.c's surface()), and the question says which."""
    tool = HERE.parent.parent / "userspace" / "libsgxfive" / "tools" / "sgxfive-test.c"
    src = tool.read_text()
    (sentinel,) = re.findall(r"^#define SENTINEL\s+(0x[0-9a-fA-F]+)u", src, re.M)
    (p,) = [q for q in table if q.name == full("o-preload")]
    assert p.host == "fill"
    assert f"0x{int(sentinel, 16):08X}" in p.question
    assert "zero" not in p.question
