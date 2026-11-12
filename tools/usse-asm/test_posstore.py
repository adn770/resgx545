# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The position-store pixel program (probes/pds/templates/pix_posstore.s, Q291, E898): usse-asm
assembles the landed template to the binary the round 7 plan checked in sgx-sim
(closing7/a/q291/SHA256.txt), so the simulator check of the plan and of
crates/sgx-tools/tests/posstore_sim.rs is a check of this program."""
from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE.parent.parent / "probes" / "pds" / "templates" / "pix_posstore.s"
# sha256 of the plan's pix_posstore.bin (closing7/a/q291/SHA256.txt)
PLAN_BIN = "8a136e52d7966dc41b5f20da97f16347e5484bc8b6e1e37618def59cea2fdf9f"


def code(text: str) -> str:
    return "\n".join(ln.split(";", 1)[0] for ln in text.splitlines())


def test_posstore_assembles_to_the_plans_binary(tmp_path):
    out = tmp_path / "pix_posstore.bin"
    subprocess.run([str(HERE / "usse-asm"), "-o", str(out), str(TEMPLATE)], check=True)
    data = out.read_bytes()
    assert len(data) == 17 * 8
    assert hashlib.sha256(data).hexdigest() == PLAN_BIN


def test_posstore_reads_only_the_globals_of_a_triangles_pixel_task():
    # g23, g24 and g25 (E808); sgx-sim refuses the rest of the bank in a triangle's task
    text = TEMPLATE.read_text()
    assert "SPDX-" + "License-Identifier: MIT" in text
    assert sorted(set(re.findall(r"\bg(\d+)\b", code(text)))) == ["23", "24", "25"]
