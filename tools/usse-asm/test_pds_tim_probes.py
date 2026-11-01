# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The EVENT_TIMER probes of probes/pds/timer.toml: they write the microkernel's tick timer,
so they are recorded only, never predicted."""
from __future__ import annotations

import probe

TABLE = probe.PROBES / "pds" / "timer.toml"
PDS_TEMPLATES = probe.PROBES / "pds" / "templates"
NAMES = {"pds-timer-tim-host", "pds-timer-tim-period", "pds-timer-tim-restore"}


def test_the_tim_probes_load_and_assemble(tmp_path):
    ps = {p.name: p for p in probe.load(TABLE)}
    assert NAMES <= set(ps)
    for name in NAMES:
        p = ps[name]
        assert p.isa == "pds" and not p.hypotheses
        assert len(probe.build(p, tmp_path, PDS_TEMPLATES)) == len(p.cases)


def test_the_tim_probes_load_what_they_say():
    ps = {p.name: p for p in probe.load(TABLE)}
    # stopped (bit 24 clear) for the host to read back; 10 ms at 400 MHz, running (bit 24
    # set); 1 ms at 400 MHz, running, to restore the tick
    assert "movs tim" in ps["pds-timer-tim-host"].params["OP"]
    words = {name: ps[name].cases[0] for name in NAMES}
    assert 0x00ABCDE0 in words["pds-timer-tim-host"]
    assert 0x013D0900 in words["pds-timer-tim-period"]
    assert 0x01061A80 in words["pds-timer-tim-restore"]


def test_the_tim_values_are_the_periods_the_comment_names():
    mhz = 400
    assert 0x013D0900 == (1 << 24) | 10_000 * mhz         # 10 ms in 400 MHz ticks
    assert 0x01061A80 == (1 << 24) | 1_000 * mhz          # 1 ms
