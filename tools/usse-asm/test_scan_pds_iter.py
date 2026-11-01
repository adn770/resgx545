# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""scan_pds_iter.py: the pixel PDS programs of a capture's heap-6 allocations, each with its
doutu U1, its douti word pairs and whether it fetches."""
from __future__ import annotations

import pytest

import probe
import scan_pds_iter

FETCH = probe.PROBES / "texture" / "fetch.toml"


@pytest.mark.skipif(not scan_pds_iter.DIS.exists(), reason="pds-dis not built")
def test_scan_finds_a_two_fetch_primary(tmp_path):
    """The two-fetch primary of texture-fetch-tex2-pa0 (probes/texture/fetch.toml) after a
    page of zeros in a heap-6 allocation: its U1, both DOUTI pairs, its fetch."""
    p = next(q for q in probe.load(FETCH) if q.name == "texture-fetch-tex2-pa0")
    p.cases = p.cases[:1]
    (case,) = probe.build(p, tmp_path / "b", FETCH.parent / "templates")
    d = tmp_path / "cap" / "dump"
    d.mkdir(parents=True)
    (d / "alloc01_heapbeef0006_sz002000.bin").write_bytes(bytes(64) + case.read_bytes())
    rows = scan_pds_iter.scan(tmp_path / "cap")
    ((key, n, where),) = rows
    assert n == 1 and where.endswith("alloc01_heapbeef0006_sz002000.bin@0x40")
    assert key == ("U1 0x02000004", "0x06012201/0x0 0x46012201/0x0", "doutt")
