# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The table probes/usse/quad-lock.toml: a shared counter every pixel instance of a fill
increments, with no mutex, inside lock/release on two mutexes, and with a lock never
released: what lock serialises."""
import probe

TABLE = probe.PROBES / "usse" / "quad-lock.toml"


def test_counter_cases():
    ps = {p.name: p for p in probe.load(TABLE)}
    assert len(ps) == 2
    p = ps["usse-quad-lock-counter"]
    assert p.pixels and len(p.cases) == 4
    ops = [c[0] for c in p.cases]
    assert ops[1].startswith("lock #0\n") and ops[1].endswith("\nrelease #0")
    assert "release" not in ops[0] and "release" not in ops[3]
