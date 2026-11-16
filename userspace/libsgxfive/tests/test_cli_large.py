# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""sgxfive-test's large-page options (Q109, the linux fork's debugfs vm_pde_*) against the mock:
copy --src-addr and fill --dst-addr aim a job at a fixed address in 4 MiB slots of their own,
the copy's source read back 4 KiB by 4 KiB as the kernel's tags name it, and --large-copy keeps
debugfs vm_large. The mock maps the buffers as ever (it does not model a large page) and checks
the knobs as the kernel does."""
from __future__ import annotations

import os
import pathlib
import re
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent
TOOL = os.environ.get("SGXFIVE_TEST", str(HERE.parent / "build" / "sgxfive-test"))
# one 4 KiB page a row: a copy of `rows` rows reads `rows` pages of the source
PAGE_ROWS = ["--width", "1024", "--src-stride", "4096", "--dst-stride", "4096"]


def run(*args: str, env=None) -> subprocess.CompletedProcess[str]:
    return subprocess.run([TOOL, *args], capture_output=True, text=True, timeout=60, env=env)


@pytest.fixture(scope="module", autouse=True)
def tool_exists():
    if not pathlib.Path(TOOL).exists():
        pytest.skip(f"{TOOL} not built (run make -C userspace/libsgxfive check)")


def test_usage_names_the_large_options():
    usage = run().stderr
    for opt in ("--src-addr", "--dst-addr", "--large-copy"):
        assert opt in usage, opt


def test_copy_src_addr_reads_a_fixed_address_in_a_slot_of_its_own():
    r = run("--mock", "copy", *PAGE_ROWS, "--height", "4", "--src-addr", "0x60004000")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "copy: source in 1 slot of 4 MiB at 0x60000000, the surface at +0x004000" in r.stdout
    # the mock reads the buffer's pattern: each page of the source, no tag, all pattern
    pages = re.findall(r"^tags: va \+0x(\w+): first 0x(\w+) \(slab \d+ page \d+ dword \d+\), "
                       r"(\d+)/1024 follow it, (\d+)/(\d+) pattern$", r.stdout, re.M)
    assert [int(p[0], 16) for p in pages] == [0x4000, 0x5000, 0x6000, 0x7000], r.stdout
    assert all(p[3] == p[4] == "1024" and int(p[2]) < 1024 for p in pages), pages
    assert "copy: ok" in r.stdout


def test_copy_src_addr_across_a_slot_end_maps_the_next_slot_as_ever():
    # the source crosses vm_pde_addr + 4 MiB: the next slot is a VM_MAP of its own
    r = run("--mock", "copy", *PAGE_ROWS, "--height", "4", "--src-addr", "0x603fe000")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "copy: source in 2 slots of 4 MiB at 0x60000000, the surface at +0x3fe000" in r.stdout
    assert re.findall(r"^tags: va \+0x(\w+):", r.stdout, re.M) == [
        "3fe000", "3ff000", "400000", "401000"]
    assert "copy: ok" in r.stdout


def test_fill_dst_addr_fills_a_fixed_address():
    r = run("--mock", "fill", "--width", "1024", "--height", "4", "--stride", "4096",
            "--dst-addr", "0x60ffe000")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "fill: destination in 2 slots of 4 MiB at 0x60c00000, the surface at +0x3fe000" \
        in r.stdout
    assert "fill: ok" in r.stdout


@pytest.mark.parametrize("args", [
    ["copy", "--src-addr", "0x60000800"],                   # not a page
    ["copy", "--src-addr", "0"],
    ["copy", "--src-addr", "0x60000000", "--page-before"],  # the source is the address
    ["fill", "--src-addr", "0x60000000"],
    ["copy", "--dst-addr", "0x60000000"],
    ["tri", "--large-copy", "out"],
    ["isolation", "--large-copy", "out"],
])
def test_large_options_refused_where_they_do_not_apply(args):
    r = run("--mock", *args)
    assert r.returncode == 2, r.stdout + r.stderr


def test_a_surface_past_two_slots_is_refused():
    r = run("--mock", "copy", *PAGE_ROWS, "--height", "1100", "--src-addr", "0x603ff000")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "Invalid argument" in r.stderr


def test_the_mock_refuses_what_the_kernel_refuses_at_vm_pde_addr():
    # code 5 has one block: no misalign layout (the kernel's -EINVAL at the map)
    knobs = ["--mock-knob", "vm_pde_addr=0x60000000", "--mock-knob", "vm_pde_size=5",
             "--mock-knob", "vm_pde_layout=2"]
    r = run("--mock", *knobs, "copy", *PAGE_ROWS, "--height", "4", "--src-addr", "0x603fc000")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "Invalid argument" in r.stderr
    # a pair it takes: the buffer mapped as ever, the copy exact
    knobs[3] = "vm_pde_size=3"
    r = run("--mock", *knobs, "copy", *PAGE_ROWS, "--height", "4", "--src-addr", "0x603fc000")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "copy: ok" in r.stdout


@pytest.mark.parametrize("cmd", ["copy", "fill"])
def test_large_copy_keeps_vm_large_and_the_mock_says_what_its_knobs_are(tmp_path, cmd):
    d = tmp_path / "large"
    knobs = ["--mock-knob", "vm_pde_addr=0x60000000", "--mock-knob", "vm_pde_size=3",
             "--mock-knob", "vm_pde_layout=1"]
    where = ["--src-addr" if cmd == "copy" else "--dst-addr", "0x6003e000"]
    size = PAGE_ROWS if cmd == "copy" else ["--width", "1024", "--stride", "4096"]
    r = run("--mock", *knobs, cmd, *size, "--height", "4", *where, "--large-copy", str(d))
    assert r.returncode == 0, r.stdout + r.stderr
    text = (d / "vm_large.txt").read_text()
    assert text == ("mock: vm_large not modelled: vm_pde_addr 0x60000000 vm_pde_size 3 "
                    "vm_pde_layout 1\n"), text
    assert f"{cmd}: vm_large: {d}/vm_large.txt" in r.stdout
