# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""gen_kernel_words.py writes the kernel-word sweep tables: the tracked ones are its output,
their sweeps load, and no data sweep pokes an address word or a pass-through word."""
from __future__ import annotations

import pathlib
import sys
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools" / "sweep"))
import gen_kernel_words  # noqa: E402
import sweep  # noqa: E402


def test_the_tracked_tables_are_current():
    out = gen_kernel_words.tables()
    assert sorted(out) == ["render/kernel-words.toml", "transfer/kernel-words.toml"]
    for rel, text in out.items():
        assert (HERE.parent / rel).read_text() == text, \
            f"{rel}: run probes/transfer/gen_kernel_words.py"


def test_the_sweeps_load_and_the_address_sweeps_are_open():
    for rel in gen_kernel_words.tables():
        path = HERE.parent / rel
        names = [s.name for s in sweep.load_all(path)]
        assert [n for n in names if n.endswith("-addr")]
        assert tomllib.loads(path.read_text())["open"] == [n for n in names if n.endswith("-addr")]


def test_a_data_sweep_leaves_out_addresses_and_pass_through_words():
    skip = gen_kernel_words.passed()
    assert 2 in skip["rd"] and 4 in skip["ta"]          # the pixel back end, a background-object word
    for rel, text in gen_kernel_words.tables().items():
        for sw in text.split("[[sweep]]")[1:]:
            if "-addr" in sw.split("\n")[1]:
                continue
            for r in sw.split("[[sweep.range]]")[1:]:
                space = r.split('"')[1]
                a, b = [int(x) for x in r.split("[")[1].split("]")[0].split(",")]
                for i in range(a, b + 1):
                    assert i not in gen_kernel_words.ADDR[space] and i not in skip[space], \
                        (rel, space, i)
