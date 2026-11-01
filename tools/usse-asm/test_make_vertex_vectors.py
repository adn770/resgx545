# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""make_vertex_vectors.py against the data repository: the decoder, the 11.33 rules the simulator
models, and the vector files' digests. Skips (with the reason) when the data repository is absent."""
import gzip
import hashlib
import json
import os
import pathlib

import pytest

import make_vertex_vectors as mv

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = pathlib.Path(os.environ.get("RESGX545_DATA") or ROOT.parent / "resgx545-data")
ASM = pathlib.Path(__file__).resolve().parent / "usse-asm"

pytestmark = pytest.mark.skipif(not (DATA / mv.RAW).is_dir(),
                                reason="no resgx545-data usse/globals-vertex-eot (set RESGX545_DATA)")


def all_jobs():
    return [(s, j) for s in mv.SCRIPTS for j in mv.jobs(DATA, s)]


def reg(v, g, group):
    return v[3 + mv.GROUPS[group].index(g)]


def rule(g, k, per):
    task, lane = divmod(k, per)
    return {17: task % 4, 22: lane // 4 % 2, 23: 0x10 * (task // 2 % 2), 24: 8 * (task % 2),
            25: lane % 4, 39: 4 * (lane // 4 % 2)}[g]


def dump(script, job):
    return mv.vertices(gzip.open(DATA / mv.RAW / script / f"{job[0]}.param.bin.gz").read(), job[1])


def test_the_decoder_reads_126_vertices_a_job_and_vertex_67_is_cut():
    assert len(all_jobs()) == 12
    for s, job in all_jobs():
        vs = dump(s, job)
        assert len(vs) == 126
        assert [k for k, v in enumerate(vs) if not mv.readable(v)] == [67], job[0]


def test_the_registers_follow_the_task_and_the_lane():
    for s, job in all_jobs():
        name, _, group, per = job
        vs = dump(s, job)
        for g in mv.GROUPS[group]:
            if g not in (17, 22, 23, 24, 25, 39) or (g == 23 and group != "A"):
                continue
            hits = sum(reg(v, g, group) == rule(g, k, per) for k, v in enumerate(vs) if k != 67)
            assert hits == 125, (name, g, hits)


def test_the_constants_and_the_last_task():
    for s, job in all_jobs():
        name, _, group, per = job
        vs = dump(s, job)
        const = {16: 0, 20: 1, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0, 31: 0, 40: 0, 42: 0x3F800000}
        for g, want in const.items():
            if g in mv.GROUPS[group]:
                assert all(reg(v, g, group) == want for k, v in enumerate(vs) if k != 67), (name, g)
        if group == "C":
            for k, v in enumerate(vs):
                if k == 67:
                    continue
                held = min(per, 126 - k // per * per)
                want = (3, 0x20000000) if held == 2 else (0xF, 0xDF000000)
                assert (reg(v, 41, "C"), reg(v, 43, "C")) == want, (name, k)


@pytest.mark.skipif(not ASM.exists(), reason="usse-asm is not built")
def test_the_vector_files_name_their_raw_dumps_and_digests(tmp_path):
    mv.make(DATA, tmp_path, ASM)
    for f, n in (("q053-vtx", 6), ("q053-vtx2", 6)):
        doc = json.loads((tmp_path / f"{f}.vec.json").read_text())
        assert len(doc["vectors"]) == n and len(doc["run"]["raw"]) == n
        for raw, sha in zip(doc["run"]["raw"], doc["run"]["raw_sha256"]):
            assert hashlib.sha256((DATA / raw).read_bytes()).hexdigest() == sha
        for v in doc["vectors"]:
            assert v["init"]["skip"] == [67] and v["init"]["instances"] == 126
            assert v["init"]["outputs"][-1] == "o14"
            # g18, g19 and g21 (not modelled) are left out: 5 of the group A registers, 8 of B, 5 of C
            group = v["id"][-2] if v["id"][-1].isdigit() else v["id"][-1]
            assert len(v["init"]["outputs"]) == {"A": 6, "B": 9, "C": 7}[group], v["id"]
            assert len(v["program"]["words"]) == len(v["init"]["outputs"]) + 1
    committed = DATA / "vectors/nokernel/usse/globals-vertex"
    if committed.is_dir():
        for f in ("q053-vtx", "q053-vtx2"):
            assert (committed / f"{f}.vec.json").read_text() == (tmp_path / f"{f}.vec.json").read_text()
