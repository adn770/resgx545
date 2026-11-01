# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""glossary_coverage.py: glossary coverage per unit."""
from __future__ import annotations

import glossary_coverage
import glossary


def row(group, name, meaning="a meaning", tier="ours", evidence="", status="named"):
    return dict(group=group, name=name, status=status, term=name, kind="field", sgx545="x",
                meaning=meaning, tier=tier, source="src", citation="cite", licence="MIT",
                evidence=evidence)


def test_units_and_counts():
    rows = [row("registers", "CR_ISP_REG_0418", "function not established", status="unset"),
            row("registers", "CR_ISP_DEPTHSORT", tier="1"),
            row("words", "MTECTL.NO_TRANSFORM", evidence="[HW] x"),
            row("words", "VDM_STATE1.BITS11_9", "function not established", status="unset"),
            row("words", "REGION_HDR.POS", evidence="[HW] x"),
            row("units", "x")]
    st = glossary_coverage.units(rows)
    isp = st["registers: ISP"]
    assert (isp["rows"], isp["named"], isp["unset"], isp["neutral"]) == (2, 1, 1, 1)
    assert isp["tier 1"] == 1 and isp["tier ours"] == 1
    assert st["words: MTE state block words"]["hw/cap"] == 1
    assert st["words: VDM stream words"]["neutral"] == 1
    assert st["words: the TA's parameter buffer and TA data"]["named"] == 1


def test_inferred_readings_are_counted_apart():
    """A row whose term's status is inferred is neither named nor unset: the report keeps it
    in its own column."""
    rows = [row("words", "DOUTU1.BIT2", "a hint", status="inferred"),
            row("words", "DOUTU1.WAIT_ITER")]
    st = glossary_coverage.units(rows)["words: PDS DOUT words"]
    assert (st["rows"], st["named"], st["unset"], st["inferred"]) == (2, 1, 0, 1)
    assert "inferred" in glossary_coverage.report(glossary_coverage.units(rows)).splitlines()[0]


def test_report_has_a_total():
    text = glossary_coverage.report(glossary_coverage.units([row("words", "BG.TSP_DWORDS")]))
    assert text.splitlines()[-1].split()[:3] == ["TOTAL", "1", "1"]


def test_the_glossary_reads():
    assert "TOTAL" in glossary_coverage.report(glossary_coverage.units(glossary.load()))


def test_the_module_does_not_shadow_the_coverage_package():
    import pathlib
    assert not (pathlib.Path(__file__).parent / "coverage.py").exists()
