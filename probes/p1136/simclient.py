#!/usr/bin/env python3
"""Run every case of a client table on sgx-sim (tables/target/debug/sgx-sim) and say which hypotheses
of the table the simulator's reading agrees with.  The simulator is a reference, not a measurement:
where it stops (a form it does not model) the case is counted as `stops`."""
import pathlib, re, subprocess, sys, tempfile, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, "/Users/jtorra/src/resgx545/tools/usse-asm")
import probe as P

SIM = HERE / "target/debug/sgx-sim"
BASE = 0x3e003000


def run_case(p, case, tdir):
    txt = P.render(p, case, (tdir / p.source).read_text())
    r = subprocess.run([str(SIM), "--temps", str(p.temps), "-"], input=txt, capture_output=True, text=True)
    out = r.stdout + r.stderr
    if "ended after" not in out:
        return None, out.strip().splitlines()[-1][:100] if out.strip() else "no output"
    o0 = int(re.search(r"^o0 = (0x[0-9a-f]+)", out, re.M).group(1), 16)
    scr = []
    for m in re.finditer(r"\[0x([0-9a-f]+)\] = 0x([0-9a-f]+) \(was 0x([0-9a-f]+)\)", out):
        a, v, w = int(m.group(1), 16), int(m.group(2), 16), int(m.group(3), 16)
        if v != w:
            scr.append((a - BASE, v))
    return P.Obs(o0=o0, scratch=tuple(scr)), None


def main(table):
    tdir = pathlib.Path(table).parent / "templates"
    tot = collections.Counter()
    for p in P.load(pathlib.Path(table)):
        score = collections.Counter()
        stops = []
        for i, c in enumerate(p.cases):
            obs, why = run_case(p, c, tdir)
            if obs is None:
                stops.append((i, why))
                continue
            for h, e in p.hypotheses.items():
                score[h] += P.matches(e[i], obs)
        n = len(p.cases) - len(stops)
        line = "%-34s %3d cases, sim stops %2d | " % (p.name, len(p.cases), len(stops))
        line += " | ".join("%s %d/%d" % (h.split(":")[0] + ":" + h.split(":")[1][:34], score[h], n) for h in p.hypotheses)
        print(line)
        if stops:
            print("     first stop: case %d: %s" % stops[0])


if __name__ == "__main__":
    for t in sys.argv[1:]:
        main(t)
