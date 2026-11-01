# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The decoder-vector table probes/usse/decoder-vectors.toml: every case assembles."""
import probe

TABLE = probe.PROBES / "usse" / "decoder-vectors.toml"


def test_decoder_vector_cases_assemble(tmp_path):
    table = probe.load(TABLE)
    names = [p.name for p in table]
    assert len(names) == len(set(names))
    assert not any(p.hypotheses for p in table)          # recorded, not probed
    other = {p.name for t in probe.PROBES.glob("*/*.toml") if t != TABLE
             for p in probe.load(t)}
    assert not set(names) & other
    n = sum(len(probe.build(p, tmp_path, TABLE.parent / "templates")) for p in table)
    assert n == sum(len(p.cases) for p in table) >= 300
