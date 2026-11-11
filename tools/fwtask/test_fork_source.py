# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""What the kernel fork's source must say, where no host build or KUnit can run it (phase 11.29
review R2): the own task's code page is mapped read-only in the EDM's page directory, and the
only buffer it may store into is the results page. A text check of the checkout: it fails on the
fork before the fix and skips without a checkout."""
import pathlib
import re
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gen_verify  # noqa: E402

DEBUG = gen_verify.SGXFIVE / "sgxfive_debug.c"


@pytest.fixture(scope="module")
def src():
    if not DEBUG.is_file():
        pytest.skip(f"SKIPPED, NOT PASSED: no fork commit {gen_verify.forkpin.pin()} in {gen_verify.LINUX} (RESGX545_LINUX)")
    return DEBUG.read_text()


def row(src, name):
    m = re.search(rf"\[{name}\] = \{{([^}}]*)\}}", src)
    assert m, name
    return [x.strip() for x in m.group(1).split(",")]


def test_own_code_page_is_read_only_for_the_edm(src):
    assert row(src, "XB_OWNCODE")[-1] == "SGX_MMU_RO"


def test_own_results_page_stays_writable(src):
    assert row(src, "XB_OWNRES")[-1] == "0"


def test_map_pd_passes_the_flags_to_the_mmu():
    mmu = gen_verify.SGXFIVE / "sgxfive.c"
    if not mmu.is_file():
        pytest.skip(f"SKIPPED, NOT PASSED: no fork commit {gen_verify.forkpin.pin()} in {gen_verify.LINUX} (RESGX545_LINUX)")
    s = mmu.read_text()
    m = re.search(r"int sgxfive_map_pd\(.*?\n}\n", s, re.S)
    assert m and "u32 flags" in m.group(0) and "b->npages, flags)" in m.group(0)


def test_the_kernel_resolves_cont4_for_the_documented_firmware_file_only():
    """R3-K11: the digest the kernel ties the shared exit's index to is the sha256 that
    tools/fwcutter/README.md documents for the cut (format v3), the file E154 read."""
    own = gen_verify.SGXFIVE / "sgxfive_owntask.c"
    if not own.is_file():
        pytest.skip(f"SKIPPED, NOT PASSED: no fork commit {gen_verify.forkpin.pin()} in {gen_verify.LINUX} (RESGX545_LINUX)")
    m = re.search(r"sgx_own_exit_fw_sha256\[32\] = \{(.*?)\};", own.read_text(), re.S)
    assert m
    digest = bytes(int(x, 16) for x in re.findall(r"0x([0-9a-f]{2})", m.group(1))).hex()
    readme = (gen_verify.fwtask.ROOT / "tools/fwcutter/README.md").read_text()
    doc = re.search(r"`sgx545_ukernel\.fw` \(format v3\) has SHA-256\s+`([0-9a-f]{64})`", readme)
    assert doc and digest == doc.group(1) == gen_verify.fwtask.EXIT_FW_SHA256
