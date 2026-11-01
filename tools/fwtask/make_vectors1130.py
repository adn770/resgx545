# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The phase 11.30 firmware-task runs as hardware vectors, kind `firmware` (see make_vectors.py for
the layout), now with task state: init.state seeds the machine as the hardware had it at the task's
entry (sa, r, i, p, pclink, pa) and readback.state lists what the task left that the hardware's next
reading agrees with. The run ends at the wrapper's tail call: the closed task is not run, so a
register that differs at the next entry (sa64, p0, pclink, and p2 and p3, which move with no
writer in between) is never in readback.state.

    make_vectors1130.py DATA_FW_DIR OUTDIR     (DATA_FW_DIR is the data repository's firmware-tasks)
"""
import datetime
import hashlib
import json
import pathlib
import sys

import fwtask
import layout as L

RES = 0x32140000
CONT = {0: 6, 1: 1434, 2: 2766, 3: 3594}      # E146 states the four start indices: jump targets only
                        # (the events stubs of slots 1 to 3 are in the program words; every vector starts at slot 0)
RD = {"a": 10, "b": 11, "c": 12, "d": 13}


def h8(v):
    return f"0x{v:08x}"


def hx(d):
    return {str(k): h8(v) for k, v in sorted(d.items())}


def program(blobname, entry_slot=0):
    raw = fwtask.blob_of(blobname)
    blob = fwtask.parse_blob(raw)
    words = fwtask.apply_patches(blob.words, blob.patches, RES, CONT)
    return {"isa": "usse", "words": [f"0x{w:016x}" for w in words], "entry": blob.entries[entry_slot],
            "source": "recorded"}, hashlib.sha256(raw).hexdigest()


def vec(vid, blobname, init_mem, state, out_mem, out_state, prov, entry_slot=0, temps=32, pa=None):
    prog, sha = program(blobname, entry_slot)
    st = dict(state)
    if pa is not None:
        st["pa"] = hx(pa)
    return {"id": vid, "program": prog,
            "init": {"task": "firmware", "page": {"base": h8(RES), "dwords": L.PAGE_DWORDS},
                     "mem": {f"0x{k:03x}": h8(v) for k, v in sorted(init_mem.items())},
                     "regs": {}, "temps": temps, "state": st,
                     "ends": "the wrapper's tail call (lapc): the closed task is not run"},
            "readback": {"failed": None, "mem": {f"0x{k:03x}": h8(v) for k, v in sorted(out_mem.items())},
                         "regs": {}, "state": out_state},
            "provenance": dict(prov, blob_sha256=sha, template=blobname + ".s")}


def entry_state(e, sa_from=None):
    """Task state at entry from one reader capture (b_entry of run_stage)."""
    s = {"pclink": h8(e["pclink"]), "p": {str(i): h8(int(x)) for i, x in enumerate(e["p"])},
         "r": hx({20: e["r20"], 21: e["r21"]}), "i": hx({0: e["i0"], 1: e["i1"]}),
         "sa": hx(dict(zip((64, 100, 127, 20, 24), e["sa"])))}
    return s


def b_entry(r):
    s = r["slots"]
    return dict(pclink=s["10"][0], p=tuple(s["10"][1:4]) + (s["11"][0],), r20=s["11"][1], r21=s["11"][2],
                i0=s["11"][3], i1=s["13"][1], sa=tuple(s["12"]) + (s["13"][0],))


def reader_vec(vid, e, r, prov):
    s = r["slots"]
    out = {1: 0, 2: L.DONE, 5: 100 + r["k"]}
    for n in (10, 11, 12):
        for j in range(4):
            out[L.slot(n) + j] = s[str(n)][j]
    out[L.slot(13)] = s["13"][0]
    out[L.slot(13) + 1] = s["13"][1]
    init = {1: 9, 3: 100 + r["k"]}
    for n in (10, 11, 12, 13):
        for j in range(4):
            init[L.slot(n) + j] = L.INITFILL
    return vec(vid, "state2", init, entry_state(e), out, {}, dict(prov, role="reader"))


def state_vectors(data):
    d = pathlib.Path(data) / "p1130-b-tailpair"
    ctl = json.loads((d / "b-controls.json").read_text())
    out = json.loads((d / "b-rounds.json").read_text())
    mk = json.loads((d / "b-markers.json").read_text())
    vs = []
    prov = {"table": "firmware-tasks/p1130-b-tailpair", "question": "Q124"}
    prev = b_entry(ctl["rounds"][1])
    for k, r in enumerate(ctl["rounds"]):
        r["k"] = k
        vs.append(reader_vec(f"state2__control{k}", b_entry(r), r, dict(prov, round=f"control{k}")))
    for k in range(3):
        w, g, f = out["rounds"][3 * k:3 * k + 3]
        m = mk["markers"][k]
        pat = mk["p_pattern"]
        for x in (w, g, f):
            x["k"] = out["rounds"].index(x)
        init = {1: 1, 3: 100 + w["k"], 32 + 9: pat[0], 42: pat[1], 43: pat[2], 44: pat[3]}
        for i, v in enumerate(m):
            init[32 + i] = v
        # the writer's own entry state is what the task before it left (not stored by the writer):
        # seeded from the reading before it
        state = entry_state(prev)
        # what the hardware read at the next event, for the registers the closed task does not change:
        nxt = b_entry(w)
        keep = {"sa": hx({100: nxt["sa"][1], 127: nxt["sa"][2], 20: nxt["sa"][3], 24: nxt["sa"][4]}),
                "r": hx({20: nxt["r20"], 21: nxt["r21"]}), "i": hx({0: nxt["i0"], 1: nxt["i1"]}),
                "p": {"1": h8(nxt["p"][1])}}   # p2 and p3 move with no writer in between (E536)
        vs.append(vec(f"state2__writer__r{k}", "state2", init, state,
                      {1: 9, 2: L.DONE, 5: 100 + w["k"]}, keep,
                      dict(prov, role="writer", round=k, note="readback.state is what the next event's reader read "
                           "(after the closed task ran); sa64, p0 and pclink at that entry are not listed [infer: the "
                           "closed task's], nor are p2 and p3 (they differ between readings with no writer)")))
        vs.append(reader_vec(f"state2__next__r{k}", nxt, w, dict(prov, round=k, when="next event")))
        vs.append(reader_vec(f"state2__gap__r{k}", b_entry(g), g, dict(prov, round=k, when="after 1200 ms")))
        vs.append(reader_vec(f"state2__fill__r{k}", b_entry(f), f, dict(prov, round=k, when="after a client fill")))
        prev = b_entry(f)
    return vs


def events_vectors(data):
    vs = []
    for run in ("p1130-c-events", "p1130-c2-events", "p1130-c3-events"):
        d = pathlib.Path(data) / run
        j = json.loads((d / "q033-q1.json").read_text())
        log = j["log"]
        prov = {"table": "firmware-tasks/" + run, "question": "Q033"}
        init = {1: 0}
        for k in range(16):
            init[L.LOG + k] = 0
        pa = {0: log[1], 1: log[2], 2: log[3]}
        out = {L.LOG + k: log[k] for k in range(16)}
        vs.append(vec(f"events_m__{run}__miscinfo", "events_m", init, {}, out, {}, dict(prov, event="miscinfo"), 0, pa=pa))
        quiet = {L.LOG + k: j["quiet_log"][k] for k in range(16)}
        vs.append(vec(f"events_m__{run}__tick", "events_m", init, {}, quiet, {},
                      dict(prov, event="tick (pa from E532, 2 of 2 runs; quiet window of 50 ms logged nothing)"), 0,
                      pa={0: 2, 1: 0x02000000, 2: 0x01061a70}))
    return vs


def slow_vectors(data):
    d = pathlib.Path(data) / "p1130-d-slow"
    vs = []
    for i, line in enumerate((d / "s11.jsonl").read_text().splitlines()):
        r = json.loads(line)
        n = r["job"]["params"]["10"]
        init = {1: 1, 3: i + 1, 10: n, 2: 0}
        out = {1: 0, 2: L.DONE, 4: r["overlap"], 5: r["echo"]}
        vs.append(vec(f"slow__n{n}__{i}", "slow", init, {}, out, {},
                      {"table": "firmware-tasks/p1130-d-slow", "question": "Q131", "n": n, "ms": r["ms"]}))
    return vs


def trc_vectors(data):
    d = pathlib.Path(data) / "p1130-e-trc"
    vs = []
    for t in (31,):
        recs = [json.loads(x) for x in (d / f"s13-T{t}.jsonl").read_text().splitlines()]
        r = recs[0]
        init = {1: 1, 3: 1}
        for k in range(4):
            init[L.slot(1) + k] = L.INITFILL
        out = {1: 0, 2: L.DONE, 5: r["echo"], L.slot(1): r["slot"][0], L.slot(1) + 2: r["slot"][2]}
        vs.append(vec(f"trc_{t:02d}__T{t}", f"trc_{t:02d}", init, {"r": {"0": "0x00000000"}}, out, {},
                      {"table": "firmware-tasks/p1130-e-trc", "question": "Q133", "trc": t}, temps=4 * t))
    return vs


def write(outdir, run, vectors, data, raws):
    """One file of a vector set: `raws` are the run files (relative to the firmware-tasks directory)
    the vectors were converted from, with their sha256."""
    shas = {r: hashlib.sha256((pathlib.Path(data) / r).read_bytes()).hexdigest() for r in raws}
    f = {"format": "sgx545-vectors", "version": 1,
         "run": {"raw": ["firmware-tasks/" + r for r in raws], "raw_sha256": [shas[r] for r in raws],
                 "converted": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                 "tool": "make_vectors1130.py 1"}, "vectors": vectors, "orphans": []}
    out = pathlib.Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{run}.vec.json").write_text(json.dumps(f, indent=1) + "\n")
    print(f"{run}: {len(vectors)} vectors")


def main(argv):
    data, outdir = argv[1], pathlib.Path(argv[2])
    write(outdir / "fwtask-state", "p1130-b-tailpair", state_vectors(data), data,
          [f"p1130-b-tailpair/{n}" for n in ("b-controls.json", "b-rounds.json", "b-markers.json")])
    write(outdir / "fwtask-events", "p1130-c-events", events_vectors(data), data,
          [f"{r}/q033-q1.json" for r in ("p1130-c-events", "p1130-c2-events", "p1130-c3-events")])
    write(outdir / "fwtask-slow", "p1130-d-slow", slow_vectors(data), data, ["p1130-d-slow/s11.jsonl"])
    write(outdir / "fwtask-trc", "p1130-e-trc", trc_vectors(data), data, ["p1130-e-trc/s13-T31.jsonl"])


if __name__ == "__main__":
    main(sys.argv)
