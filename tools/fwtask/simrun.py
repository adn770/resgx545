# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Run our firmware tasks in sgx-sim (pysgx) with our own stand-in for the closed task and a
what-if register bus. What this proves: encodings, control flow, patching, the results layout.
What it does not: any hardware behaviour. `ldr` and `str` have no hardware vector; the models
below are assumptions, never measurements."""
import dataclasses
import pathlib
import sys

import fwtask
import layout as L

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(fwtask.ROOT / "crates" / "pysgx"))
try:
    import load as _pysgx_load
    pysgx = _pysgx_load.pysgx()
except Exception:        # pragma: no cover: no cargo, or the extension does not build
    pysgx = None

RES = 0x32140000
BASE = fwtask.OWN_INDEX
STUB_MARK = 0x3f0              # dword of the results page the stand-in for the closed task writes
NOP = 0xF800014000000000


def available() -> bool:
    return pysgx is not None


def stub_words(slot: int):
    return fwtask.assemble_text(
        f"mov r1, #0x{RES + 4 * STUB_MARK:08x}\nmov r2, #0x{0x57ab0001 + slot:08x}\n"
        f"stad [r1,+#0], r2\nnop.end")


class Bus:
    """Memory of the results page, the SGX register file with a what-if model:
    ordered (a str lands at once, an ldr reads the register), lateK (a str lands K instructions
    after it is issued, for the task and the host alike), drop (a str never lands),
    ldr_overtakesK (an ldr reads the register as it was K instructions ago)."""

    now = 0

    def __init__(self, regs, model="ordered"):
        self.mem = {}
        self.regs = dict(regs)
        self.model = model
        self.pending = []
        self.hist = {}             # register -> [(step, value)] of landed writes
        self.reads, self.writes, self.stores, self.log, self.order = [], [], [], [], []

    def step(self):
        return self.now

    def _land(self, idx, v):
        self.regs[idx] = v
        self.hist.setdefault(idx, []).append((self.now, v))

    def _settle(self):
        for due, idx, v in sorted(self.pending):
            if due <= self.now:
                self._land(idx, v)
        self.pending = [p for p in self.pending if p[0] > self.now]

    def load32(self, addr):
        return self.mem.get(addr, 0)

    def store32(self, addr, v):
        d = (addr - RES) // 4
        self.mem[addr] = v
        self.order.append(("st", d, v))
        if d != STUB_MARK:
            self.stores.append((d, v))

    def reg_read(self, idx):
        self._settle()
        self.reads.append((idx, self.now))
        self.log.append(("ldr", self.now, idx))
        if self.model.startswith("ldr_overtakes"):
            k = int(self.model[len("ldr_overtakes"):])
            v = self.initial.get(idx, self.regs[idx])
            for st, val in self.hist.get(idx, []):
                if st <= self.now - k:
                    v = val
            return v
        return self.regs[idx]

    def reg_write(self, idx, v):
        self._settle()
        self.writes.append((idx, v))
        self.log.append(("str", self.now, idx, v))
        if self.model == "drop":
            return
        if self.model.startswith("late"):
            self.pending.append((self.now + int(self.model[4:]), idx, v))
            return
        self._land(idx, v)

    @property
    def initial(self):
        return self._initial

    def seal(self):
        self._initial = dict(self.regs)


@dataclasses.dataclass
class Result:
    mem: list
    stores: list
    reg_reads: list
    reg_writes: list
    stub_hit: bool
    stub_slot: int
    final_regs: dict
    order_ok: bool
    idf_before_done: bool
    machine: object = None
    final_sa: dict = dataclasses.field(default_factory=dict)
    final_pred: tuple = ()
    final_pclink: int = 0
    reading: str = ""
    ok: bool = True
    explain: str = ""
    log: list = dataclasses.field(default_factory=list)

    def slot(self, n):
        return self.mem[L.slot(n):L.slot(n) + 4]


def _source(name):
    return (fwtask.ASM / f"{name}.s").read_text()


def load(name):
    blob = fwtask.parse_blob(fwtask.build_blob_text(_source(name)))
    return blob


def prime(m, state=False):
    p = pysgx.Program(fwtask.assemble_text("mov r12, #0x00000000\nmov pclink, r12\nnop.end"))
    m.run(p, Bus({}))
    for n in range(4):
        m.set_pred(n, False)
    for r in (20, 21):
        m.set("r", r, 0)
    for i in range(2):
        m.set("i", i, 0)


def run(name, cmd=0, entry=0, pa=(0, 0, 0), regs=None, params=None, runid=1, mem_extra=None,
        entry_state=False, carry=None, r0=None, model="ordered", max_steps=200000):
    blob = load(name)
    nslots = 4
    # indices are local to the program here (the sim has no code base): nothing in our sources
    # branches to an absolute index but through the patched continue limm
    cont = {k: len(blob.words) + 8 + 8 * k for k in range(nslots)}
    words = fwtask.apply_patches(blob.words, blob.patches, RES, cont)
    img = words + [NOP] * 8
    for k in range(nslots):
        img += stub_words(k) + [NOP] * (8 - len(stub_words(k)))
    prog = pysgx.Program(img)
    bus = Bus(regs or {}, model)
    for i in range(L.PAGE_DWORDS):
        bus.mem[RES + 4 * i] = 0
    bus.mem[RES + 4 * L.CMD] = cmd
    bus.mem[RES + 4 * L.RUNID] = runid
    for k, v in (params or {}).items():
        bus.mem[RES + 4 * k] = v
    for k, v in (mem_extra or {}).items():
        bus.mem[RES + 4 * k] = v
    if carry is not None:
        m = carry.machine
        for k, v in carry.mem_dict.items():
            bus.mem[k] = v
        bus.mem[RES + 4 * L.CMD] = carry.mem[L.CMD]
        bus.mem[RES + 4 * L.STATE] = carry.mem[L.STATE]
    else:
        m = pysgx.Machine()
        if entry_state:
            prime(m)
    bus.m = m
    bus.seal()
    if r0 is not None:
        m.set('r', 0, r0)
    for i, v in enumerate(pa):
        m.set("pa", i, v)
    m.pc = blob.entries[entry] if blob.entries else 0
    n = 0
    while True:
        bus.now = n
        n += 1
        if m.step(prog, bus) or n > max_steps:
            break
    bus.now = 1 << 30
    bus._settle()
    mem = [bus.mem[RES + 4 * i] for i in range(L.PAGE_DWORDS)]
    hit = mem[STUB_MARK] != 0
    # order: results and cmd stored before state = done
    seq = [d for k, d, v in bus.order if k == "st"]
    done_at = max((i for i, (k, d, v) in enumerate(bus.order) if d == L.STATE and v == L.DONE),
                  default=None)
    order_ok = True
    if done_at is not None:
        later = [d for k, d, v in bus.order[done_at + 1:] if d != STUB_MARK]
        order_ok = not later
    idf = None
    r = Result(mem=mem, stores=bus.stores, reg_reads=[(i, s) for i, s in bus.reads],
               reg_writes=list(bus.writes), stub_hit=hit,
               stub_slot=(mem[STUB_MARK] - 0x57ab0001) if hit else -1,
               final_regs=dict(bus.regs), order_ok=order_ok, idf_before_done=False, machine=m,
               log=bus.log)
    r.mem_dict = dict(bus.mem)
    r.reg_reads = [(i, 0) for i, _ in bus.reads]
    r.final_sa = {n: m.get("sa", n) for n in (64, 100, 127, 20, 24)} if entry_state or carry else {}
    if entry_state or carry:
        r.final_pred = tuple(int(m.pred(n)) for n in range(4))
        q = pysgx.Program(fwtask.assemble_text("mov r31, pclink\nnop.end"))
        m.pc = 0
        m.run(q, Bus({}))
        r.final_pclink = m.get("r", 31)
    return r


def has_idf_before_done(text_lines):
    return False


def run_9b(reg, n, model="ordered"):
    name = "x9b_" + reg.lower()
    rr = {"R1": L.R1, "R2": L.R2}[reg]
    other = L.R2 if reg == "R1" else L.R1
    regs = {rr // 4: L.A[rr], other // 4: L.A[other], 7: 0x01150000, 8: 0x0001000d, 81: 0x100}
    r = run(name, cmd=n, regs=regs, params={L.PARAM_B: L.B[rr], L.PARAM_C: L.C[rr]}, model=model)
    r.idf_before_done = _idf_before_done(name, n)
    r.reading = reading_of(L.X9B[n], rr, r)
    exp = EXPECT_SEQUENTIAL(L.X9B[n], rr, other)
    r.ok = r.reading == exp
    r.explain = f"{L.X9B[n][0]} {reg} reading {r.reading} expected {exp}"
    return r


def _idf_before_done(name, n):
    """X9: the path to state = done has no idf (checked from the source's done_noidf)."""
    src = _source(name)
    tail = src.split("done_noidf:")[1].split("br @tail")[0]
    code = "\n".join(ln.split(";")[0] for ln in tail.splitlines())
    return "idf" in code


def reading_of(case, rr, r):
    """(L, H) of 4.2 as a label; L is the stored result, H the register after the task."""
    name, kind, d = case
    A, B, C = L.A[rr], L.B[rr], L.C[rr]
    slot0 = r.slot(n_of(case))[0]
    H = r.final_regs[rr // 4]
    return label(kind, slot0, H, A, B, C, r, case, rr)


def n_of(case):
    for n, c in L.X9B.items():
        if c == case:
            return n


def label(kind, Lv, H, A, B, C, r, case, rr):
    nm = lambda v: {A: "A", B: "B", C: "C"}.get(v, hex(v))
    if kind == "x8":
        other = L.R2 if rr == L.R1 else L.R1
        o = r.final_regs[other // 4]
        return f"L={nm_other(Lv, L.A[other])},R2H={'unchanged' if o == L.A[other] else hex(o)}"
    if kind == "x10":
        L2 = r.slot(n_of(case))[1]
        return f"L={nm(Lv)},L2={nm(L2)},H={nm(H)}"
    if kind == "x11":
        return f"L={nm(Lv)},H={nm(H)}"
    return f"L={nm(Lv)},H={nm(H)}"


def nm_other(v, a):
    return "A2" if v == a else hex(v)


def EXPECT_SEQUENTIAL(case, rr, other):
    name, kind, d = case
    if kind in ("x0", "x1"):
        return "L=A,H=A"
    if kind in ("x2", "x3", "x4", "x5", "x9", "x11"):
        return "L=B,H=B"
    if kind == "x6":
        return "L=A,H=B"
    if kind == "x7":
        return "L=C,H=C"
    if kind == "x8":
        return "L=A2,R2H=unchanged"
    if kind == "x10":
        return "L=B,L2=B,H=B"


# what each what-if model must make the classifier report, per command (4.2's rows)
# Closed form of each model, from the sequences of 4.2 (the distance is the number of
# instructions from the first str to the ldr whose value is read: str is at 0).
DIST = {"x2": lambda d: d + 1, "x3": lambda d: 2, "x4": lambda d: 3, "x5": lambda d: 2,
        "x7": lambda d: 2, "x9": lambda d: 1, "x11": lambda d: 1}


def _expect(model, kind, d):
    if kind == "x8":
        return "L=A2,R2H=unchanged"
    if kind == "x6":
        return "L=A,H=A" if model == "drop" else "L=A,H=B"
    if kind in ("x0",):
        return "L=A,H=A"
    if kind == "x1":
        return "L=A,H=A" if model != "drop" else "L=A,H=A"
    if kind == "x10":
        if model == "drop":
            return "L=A,L2=A,H=A"
        k = int(model[4:]) if model.startswith("late") else int(model[len("ldr_overtakes"):])
        return "L=A,L2=%s,H=B" % ("B" if 67 >= k else "A")
    if model == "drop":
        return "L=A,H=A"
    k = int(model[4:]) if model.startswith("late") else int(model[len("ldr_overtakes"):])
    dist = DIST[kind](d)
    if kind == "x7":
        return "L=%s,H=C" % ("C" if dist >= k else "A")
    return "L=%s,H=B" % ("B" if dist >= k else "A")


WHAT_IF_EXPECT = {m: {n: _expect(m, c[1], c[2]) for n, c in L.X9B.items()}
                  for m in ("late4", "late20", "drop", "ldr_overtakes4")}
