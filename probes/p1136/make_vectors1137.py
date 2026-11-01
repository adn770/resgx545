#!/usr/bin/env python3
"""The 11.37 firmware-task jobs (out/NAME/jobs/*.json of run_1137_logged.py) as hardware vectors, kind `firmware`
(the layout of tools/fwtask/make_vectors.py of ~/src/resgx545, imported read only): the program as the kernel patched
it, the page words the host wrote (init.mem) and the words the judge reads back (readback.mem: the control words and the
result region of the job).  Pure conversion, nothing is judged.

    make_vectors1137.py JOBS_DIR BLOBNAME TEMPS OUTFILE DATASET NOTE"""
import datetime, hashlib, json, pathlib, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(pathlib.Path.home() / "src/resgx545/tools/fwtask"))
sys.path.insert(0, str(HERE))
import fwtask  # noqa: E402
import layout as L  # noqa: E402
import judge1137 as J  # noqa: E402

RES, CONT = 0x32140000, {0: 6}


def h8(v):
    return "0x%08x" % (v & 0xffffffff)


def region(j):
    p = j["job"]
    if p.get("item") == 8:
        return list(range(L.slot(p["n"]), L.slot(p["n"]) + 4))
    if p.get("item") == 10:
        return [J.OUT1 + i for i in range(128 if p["task"] == "imm" else 64)]
    if p.get("item") == 11:
        return [J.OUT1 + n for n in p["test"]]
    if p.get("item") == 12:
        return [J.OUT1 + i for i in range(p["N"])]
    return []


def main(a):
    jobs_dir, blobname, temps, out, dataset, question = a
    raw = (HERE / "asm" / (blobname + ".blob")).read_bytes()
    blob = fwtask.parse_blob(raw)
    words = fwtask.apply_patches(blob.words, blob.patches, RES, CONT)
    prog = {"isa": "usse", "words": ["0x%016x" % w for w in words], "entry": blob.entries[0], "source": "recorded"}
    vecs = []
    for f in sorted(pathlib.Path(jobs_dir).glob("*.json")):
        j = json.loads(f.read_text())
        job, rec, page = j["job"], j["record"], j["page"]
        if not rec.get("done") or ("task" in job and "p1137_" + job["task"] != blobname):
            continue
        if job.get("control"):      # the no-wdf control: the simulator has no rule for it (it stops), not a vector of a set
            continue
        n = job["n"]
        init = {1: n, 2: 0, 3: rec["job"]["runid"], 4: 0}
        init.update({int(k): v for k, v in job["params"].items()})
        rb = {1: page[1], 2: page[2], 4: page[4], 5: page[5]}
        rb.update({i: page[i] for i in region(j)})
        vecs.append({"id": "%s__%s" % (blobname, j["tag"]), "program": prog,
                     "init": {"task": "firmware", "page": {"base": h8(RES), "dwords": L.PAGE_DWORDS},
                              "mem": {"0x%03x" % k: h8(v) for k, v in sorted(init.items())}, "regs": {},
                              "temps": int(temps), "state": {},
                              "ends": "the wrapper's tail call (lapc): the closed task is not run"},
                     "readback": {"failed": None, "mem": {"0x%03x" % k: h8(v) for k, v in sorted(rb.items())},
                                  "regs": {}, "state": {}},
                     "provenance": {"table": dataset, "question": question, "n": n, "ms": rec.get("ms"),
                                    "blob_sha256": hashlib.sha256(raw).hexdigest(), "template": blobname + ".s"}})
    doc = {"format": "sgx545-vectors", "version": 1,
           "run": {"raw": [dataset + "/jobs.tar.gz"], "raw_sha256": [hashlib.sha256(
               (pathlib.Path.home() / "src/resgx545-data" / dataset / "jobs.tar.gz").read_bytes()).hexdigest()],
               "converted": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
               "tool": "make_vectors1137.py 1"}, "vectors": vecs, "orphans": []}
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(out).write_text(json.dumps(doc, indent=1) + "\n")
    print("%s: %d vectors" % (out, len(vecs)))


if __name__ == "__main__":
    main(sys.argv[1:])
