# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""What the 11.32 scripts assume of `sgxfive-test probe` (the landed userspace/libsgxfive), against the mock.

No tool change is needed by any case of p1132 (tools/texture/p1132/plan.md section 7); these tests pin the behaviour the
scripts and tools/texture/p1132/recompute/recompute_p1132.py read, so that a change of the tool that breaks them is seen at
once. They pass on the landed tool. Run: SGXFIVE_TEST=path/to/sgxfive-test python3 -m pytest tools/texture
"""
import os, pathlib, re, subprocess, tempfile

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOL = os.environ.get("SGXFIVE_TEST", str(ROOT / "userspace/libsgxfive/build/sgxfive-test"))
ASM = pathlib.Path(os.environ.get("USSE_ASM", str(ROOT / "target/debug/usse-asm")))


@pytest.fixture(scope="module", autouse=True)
def have_tool():
    if not pathlib.Path(TOOL).exists() or not ASM.exists():
        pytest.skip(f"SKIPPED, NOT PASSED: no {TOOL} or {ASM} (build userspace/libsgxfive and usse-asm)")


def asm(tmp, text, name="p"):
    out = pathlib.Path(tmp) / f"{name}.bin"
    subprocess.run([str(ASM), "-o", str(out), "-"], input=text.encode(), check=True, capture_output=True)
    return out


def run(*a):
    return subprocess.run([TOOL, "--mock", "probe", *a], capture_output=True, text=True, timeout=60)


def test_row_lines_and_pa0_layout(tmp_path):
    f = asm(tmp_path, "phas #0, #0, pixel, end, parallel\nmov.skipinv.end o0, pa0\n")
    r = run("--temps", "8", "--coords", "--pixels", str(f))
    assert r.returncode == 0, r.stdout + r.stderr
    rows = {int(m.group(1)): m.group(2).split() for m in re.finditer(r"^probe p: row (\d+): (.*)$", r.stdout, re.M)}
    assert sorted(rows) == list(range(32)) and all(len(v) == 64 for v in rows.values())
    assert rows[5][7] == "00050007"          # (y << 16) | x, eight hex digits and no 0x
    assert re.search(r"^probe p: o0 mixed ", r.stdout, re.M)


def test_xfer_poke_is_accepted_and_scratch_pages_are_sized(tmp_path):
    f = asm(tmp_path, "phas #0, #0, pixel, end, parallel\nmov.skipinv.end o0, #0x12345678\n")
    r = run("--temps", "8", "--coords", "--pixels", "--poke", "xfer:17^=0x1", "--poke", "xfer:18=0x00950095",
            "--scratch-pages", "24", str(f))
    # the mock's fill does not run this poked command (it reports a fault); what the scripts and the
    # converter read is the two lines below, which the tool prints before the job
    assert re.search(r"scratch at 0x[0-9a-f]+ \(96 KiB\)", r.stdout)
    assert re.search(r"^probe p: pokes xfer:17\^=0x1 xfer:18=0x00950095$", r.stdout, re.M), r.stdout


def test_the_limit_of_256_words_is_a_refusal(tmp_path):
    f = asm(tmp_path, "phas #0, #0, pixel, end, parallel\n" + "mov.skipinv r1, #1\n" * 257 + "mov.skipinv.end o0, r1\n")
    r = run("--temps", "8", str(f))
    assert r.returncode != 0
