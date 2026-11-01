# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for esil_vectors.py: its scratch patch and skip list are the simulator's, and the
vectors it runs under the fork's ESIL match the hardware. The run needs the data repository
($RESGX545_DATA, or resgx545-data beside the tree) and the fork's install with the lane and
float tests (R2_PREFIX, or its prefix beside the repository); it is skipped without them."""
import os
import pathlib
import subprocess
import sys

import pytest

import esil_vectors as ev


def test_patch_scratch_is_the_simulators():
    """A limm of 0x5cafnnnn loads the scratch address + nnnn; other words are untouched."""
    w = 0xFC22B08002002600                     # mov r16, #0xAD002600: not a scratch limm
    assert ev.patch_scratch(w) == w
    limm = ev.limm_put(0xFC20000000000000, 0x5CAF0010)
    assert ev.limm_get(ev.patch_scratch(limm)) == ev.SCRATCH + 0x10


def test_skip_list_comes_from_the_simulator():
    skip = ev.skip_list()
    src = (ev.ROOT / "crates" / "sgx-sim" / "src" / "vectors.rs").read_text()
    block = src[src.index("pub const SKIP"):]
    rows = [ln for ln in block[:block.index("];")].splitlines() if ln.lstrip().startswith('("')]
    assert len(skip) == len(rows) >= 10
    assert all(len(row) == 3 and row[2] for row in skip)
    assert any(probe == "usse-cache-control-modes" for _, probe, _ in skip)


def test_skip_rows_match_by_probe_id_or_prefix():
    skip = [("", "p-a", "why"), ("usse/loop/", "", "why"), ("", "p-b__1", "why")]
    assert ev.skipped(skip, "x/raw.txt", "p-a", "p-a__3")
    assert ev.skipped(skip, "usse/loop/raw.txt", "any", "any__0")
    assert ev.skipped(skip, "x/raw.txt", "p-b", "p-b__1")
    assert not ev.skipped(skip, "x/raw.txt", "p-b", "p-b__2")


def test_files_are_the_data_repositorys(tmp_path, monkeypatch):
    (tmp_path / "vectors" / "usse" / "x").mkdir(parents=True)
    (tmp_path / "vectors" / "usse" / "x" / "a.vec.json").write_text("{}")
    monkeypatch.setenv("RESGX545_DATA", str(tmp_path))
    assert ev.data_dir() == tmp_path / "vectors"
    monkeypatch.setattr(ev, "DATA", ev.data_dir())
    assert [p.name for p in ev.files()] == ["a.vec.json"]
    monkeypatch.setenv("RESGX545_DATA", str(tmp_path / "none"))
    assert ev.data_dir() is None


def test_without_the_data_repository_it_skips(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(ev, "DATA", None)
    monkeypatch.setattr(ev, "PREFIX", pathlib.Path(ev.__file__))      # exists check below
    monkeypatch.setattr(pathlib.Path, "exists", lambda self: True)
    assert ev.main([]) == 0
    assert "skip: no resgx545-data/vectors" in capsys.readouterr().err


def _vector(**over):
    v = {"id": "p__0", "program": {"isa": "usse"}, "init": {"pa0": "fill"},
         "readback": {"o0": "0x1", "failed": None}, "provenance": {"probe": "p", "options": []}}
    for k, val in over.items():
        v[k].update(val) if isinstance(val, dict) else v.__setitem__(k, val)
    return v


def test_triangle_host_vectors_are_not_run():
    assert ev.runnable(_vector(), "x/raw.txt", [])
    assert not ev.runnable(_vector(provenance={"options": ["--tri"]}), "x/raw.txt", [])
    assert not ev.runnable(_vector(readback={"failed": "timeout"}), "x/raw.txt", [])
    assert not ev.runnable(_vector(init={"pa0": "coords"}), "x/raw.txt", [])
    assert not ev.runnable(_vector(), "x/raw.txt", [("", "p", "why")])


def test_end_is_found_in_any_modifier_position():
    assert ev.has_end("mov.end r0, r1")
    assert ev.has_end("p0 mov.end r0, r1")
    assert ev.has_end("mov.skipinv.end o0, r1")
    assert not ev.has_end("mov r0, r1")
    assert not ev.has_end("mov.endless r0, r1")


def test_base_mnemonic_drops_predicate_and_flags():
    assert ev.base_mnemonic("p1 iadd16.testnat.chan2 r3, p0, r1, r2") == "iadd16"
    assert ev.base_mnemonic("!p0 fadd.testtaz.orall !c0, p0, r1, r2") == "fadd"


def _fork_lane_tests():
    prefix = ev.PREFIX
    if not (prefix / "bin" / "r2").exists():
        return False
    # iadd8.testnat.chan1 r7, p2, r5, r6
    out = subprocess.run([str(pathlib.Path(prefix) / "bin" / "r2"), "-q", "-a", "usse", "-b",
                          "32", "-c", "wx 8602f80098140048; aoj 1", "malloc://8"],
                         capture_output=True, text=True).stdout
    return "iadd8" in out and ",p2,=" in out


LANE_FILES = ["usse/test-channels/usse-test-channels-chan-tests.vec.json",   # fadd, iadd8
              "usse/test-channels/usse-test-channels-lanes-other.vec.json",  # fmul, imul16
              "usse/test-channels/usse-test-channels-chan-isub16.vec.json"]  # isub16


@pytest.mark.skipif(not _fork_lane_tests(), reason="no install of the radare2 fork")
@pytest.mark.skipif(ev.DATA is None, reason="no resgx545-data/vectors (set RESGX545_DATA)")
def test_the_lane_and_float_tests_match_the_hardware():
    r = subprocess.run([sys.executable, str(pathlib.Path(ev.__file__)), "--only",
                        "isub16,iadd8,imul16,fadd,fmul", *(str(ev.DATA / f) for f in LANE_FILES)],
                       capture_output=True, text=True, env=os.environ)
    assert r.returncode == 0, r.stdout + r.stderr
    rows = {ln.split()[0]: [int(x) for x in ln.split()[1:]] for ln in r.stdout.splitlines()[1:]}
    assert set(rows) == {"isub16", "iadd8", "imul16", "fadd", "fmul"}, r.stdout
    assert all(v[0] > 0 and v[1] == 0 for v in rows.values()), r.stdout
