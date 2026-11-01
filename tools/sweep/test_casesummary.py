# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""casesummary.py: the cases of a script table's output (one(): "== NAME: tri ARGS" blocks)."""
from __future__ import annotations

import casesummary

TEXT = """## uname
x
== control: tri --width 64
tri: render context for targets up to 64x64
job: ok
target: 64x64 hash 0xaaaa
diff: 0 of 4096 pixels
tri 64x64 #1: 1000 us
tri: 1 renders ok
rc 0
== b3: tri --kpoke-render 1:ta:143=0x1
job: ok
target: 64x64 hash 0xbbbb
diff: 12 of 4096 pixels, first (1, 2) 0x1 expected 0x2
tri 64x64 #1: 1500 us
scratch page 2: 3 dwords changed
rc 0
== hang: tri --poke vdm:1^=0x2000
job: failed: job hung, context lost (Connection timed out)
rc 1
== end
"""


def test_parse_reads_each_case():
    cs = casesummary.parse(TEXT)
    assert [c.name for c in cs] == ["control", "b3", "hang"]
    c, b, h = cs
    assert (c.job, c.wrong, c.hash, c.us, c.rc) == ("ok", 0, "0xaaaa", 1000, 0)
    assert (b.job, b.wrong, b.hash, b.us) == ("ok", 12, "0xbbbb", 1500)
    assert b.scratch == ["scratch page 2: 3 dwords changed"]
    assert h.job.startswith("failed") and h.hash is None and h.rc == 1
    assert c.args == "--width 64"


def test_table_marks_what_differs_from_the_control():
    out = casesummary.table(casesummary.parse(TEXT), "control")
    lines = out.splitlines()
    assert any(ln.startswith("b3") and "differs" in ln and "wrong 12" in ln for ln in lines)
    assert any(ln.startswith("hang") and "failed" in ln for ln in lines)
    assert any(ln.startswith("control") and "reference" in ln for ln in lines)


def test_a_case_with_the_reference_hash_and_no_scratch_holds():
    t = TEXT.replace("0xbbbb", "0xaaaa").replace("12 of 4096", "0 of 4096")
    t = t.replace("scratch page 2: 3 dwords changed\n", "")
    cs = casesummary.parse(t)
    assert "differs" not in casesummary.table(cs, "control").splitlines()[1]
