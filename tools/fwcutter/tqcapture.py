# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The transfer captures read as a black box (doc/specs/fw_format.md §9-§10, evidence E004).

captures/firmware/transfer.toml runs the closed OpenVG stack under the harness
(harness/ukernel-extract: fakedrm.c, xfer.c) through fills and copies; fakedrm.c snapshots
device memory at every SGX_SUBMITTRANSFER. This module follows each transfer to the
programs the GPU would receive, the way the GPU finds them:

- the command (the client CCB at the kick's shared offset, minus the shared block's
  offset 0xac in the command) gives the pixel-event PDS program (EDMPixelPDSExec, +0x24),
  the PDS execution base (+0x3c) and the background object (ISPBgObjTag, +0x00, relative to
  Bif3DReqBase, +0x18; its TSPDATASIZE [30:25] counts the layers: 0 for a fill, 1 for a copy);
- the background object's PDS state pointers (dwords 0 and 2: BASEADD [23:0] in 16-byte
  units above the PDS base, DATASIZE [31:26]) give the secondary and primary PDS programs;
- each PDS program's DOUTU word 0 (EXE [19:4], CBASE [3:0]) gives the USE program it starts,
  and the pixel-event program's data dwords 0, 3 and 4 give the end-of-tile and end-of-render
  USE programs.

A program's extent is its slot (up to the next program in the same allocation, else the
allocation's size) without trailing zero dwords (USE: whole 8-byte instructions).

It then compares the captures with facts.py: searches libsrv_um.so for the captured bytes
under each piece (verify_pieces; bits that vary or that a patch writes are don't-care),
finds the bits that vary between copies and what explains each varying field (fields,
compare_fields), rebuilds every ARGB8888 transfer's programs from the old tables
(rebuild) and checks the fixed command words (compare_cmd) and the template records (meta).

    tqcapture.py trim RUN...              keep only what the chains touch (the capture script)
    tqcapture.py report DIR [LIBSRV_UM]   the per-template report of E004
    tqcapture.py commands DIR             the commands, the CCB and the context (counts, value
                                          classes; no program words)
"""
from __future__ import annotations

import collections
import dataclasses
import pathlib
import re
import struct
import sys

# fakedrm.c's heap bases (GENERAL, PIXELSHADER, PDSPIXEL), unless the run's env.txt moves them
HEAP_DEFAULTS = {0: 0x08000000, 4: 0xF4000000, 6: 0xE4000000}
GENERAL, PIXELSHADER, PDSPIXEL = 0, 4, 6
CMD_SHARED = 0xAC                 # the shared block's offset in a transfer command
CMD_BYTES = 0x1A0                 # the command words read here (up to the update list)
MAX_SLOT = 0x100


@dataclasses.dataclass
class Obj:
    index: int
    heap: int
    name: str
    dva: int
    size: int
    mapped: int
    attribs: int = 0
    kind: int = 0                   # fakedrm.c's devmem_kind: 0 memory, 1 sync, 2 context

    @property
    def file(self) -> str:
        return f"obj{self.index:03d}_{self.dva:08x}.bin"


_OBJ = re.compile(r"\s*(\d+) heap=(\d+)\s+(\S+)\s+dva=([0-9a-f]+) size=(0x[0-9a-f]+) "
                  r"mapped=(0x[0-9a-f]+)(?: attribs=([0-9a-f]+) kind=(\d+))?")


def parse_objects(text: str) -> list[Obj]:
    """fakedrm.c's objects.txt: one line per live object."""
    out = []
    for line in text.splitlines():
        m = _OBJ.match(line)
        if m:
            k, heap, name, dva, size, mapped, attribs, kind = m.groups()
            out.append(Obj(int(k), int(heap), name, int(dva, 16), int(size, 16),
                           int(mapped, 16), int(attribs or "0", 16), int(kind or 0)))
    return out


class Snapshot:
    """One snapshot directory: objects.txt and the obj files kept in it."""

    def __init__(self, d: pathlib.Path, extra: list[pathlib.Path] = ()):
        self.dir = pathlib.Path(d)
        self.objs = parse_objects((self.dir / "objects.txt").read_text())
        self.extra = list(extra)          # other snapshots to read a missing object from
        self._data: dict[int, bytes] = {}

    def obj(self, dva: int) -> Obj:
        for o in self.objs:
            if o.dva <= dva < o.dva + o.mapped:
                return o
        raise KeyError(f"{self.dir.name}: no object at {dva:#010x}")

    def by_index(self, k: int) -> Obj:
        return next(o for o in self.objs if o.index == k)

    def data(self, o: Obj) -> bytes:
        if o.index not in self._data:
            for d in [self.dir, *self.extra]:
                p = d / o.file
                if p.exists():
                    self._data[o.index] = p.read_bytes()
                    break
            else:
                raise KeyError(f"{self.dir.name}: {o.file} not kept")
        return self._data[o.index]

    def read(self, dva: int, n: int) -> bytes:
        o = self.obj(dva)
        return self.data(o)[dva - o.dva:dva - o.dva + n]

    def word(self, dva: int) -> int:
        return struct.unpack("<I", self.read(dva, 4))[0]


def doutu_addr(u0: int, use_base: int) -> int:
    """The USE program a DOUTU word 0 starts: EXE [19:4] and CBASE [3:0] (format §9.4)."""
    return use_base + (((u0 & 0xFFFF0) >> 1) | ((u0 & 0xF) << 19))


def pds_ptr(word: int, pds_base: int) -> tuple[int, int]:
    """A PDS state pointer: (program address, data segment bytes)."""
    return pds_base + ((word & 0xFFFFFF) << 4), (word >> 26) << 4


def heaps(run: pathlib.Path) -> dict[int, int]:
    """The heap bases of a run: fakedrm.c's defaults, moved by env.txt's MOCK_HEAP_BASE_<id>."""
    out = dict(HEAP_DEFAULTS)
    env = pathlib.Path(run) / "env.txt"
    for line in env.read_text().splitlines() if env.exists() else []:
        m = re.fullmatch(r"MOCK_HEAP_BASE_(\d+)=(\S+)", line.strip())
        if m and int(m.group(1)) in out:
            out[int(m.group(1))] = int(m.group(2), 0)
    return out


@dataclasses.dataclass
class Program:
    addr: int
    data: bytes
    pds_data: int = 0               # PDS: the data segment its pointer or command gives


@dataclasses.dataclass
class Transfer:
    index: int
    step: str                       # the xfer.c step that submitted it
    kind: str                       # "fill" (no TSP layer) or "copy" (one)
    cmd: list[int]                  # the command words, CMD_BYTES of them
    progs: dict[str, Program]       # template name (facts.TQ_NAMES) -> placed program
    snapshot: Snapshot
    offset: int = 0                 # the kick's shared offset in the CCB
    ccb: int = 0                    # the CCB's object index
    ccb_size: int = 0               # its allocation size
    ctx: int = 0                    # the HW transfer context the request names


@dataclasses.dataclass
class Run:
    name: str
    dir: pathlib.Path
    heaps: dict[int, int]
    transfers: list[Transfer]
    allocs: list[tuple[str, str, int, int]]     # (step, heap name, dva, size) in order


def _bridge(run: pathlib.Path) -> tuple[list[str], list[int], list[tuple[str, str, int, int]]]:
    """bridge.txt: the step before each transfer, each transfer's CCB object, the
    allocations with the step that made them."""
    steps, ccbs, allocs = [], [], []
    step = ""
    for line in (run / "bridge.txt").read_text().splitlines():
        m = re.match(r"==== (.*) \(objects so far", line)
        if m:
            step = m.group(1)
        elif "(SGX_SUBMITTRANSFER)" in line:
            steps.append(step)
        m = re.match(r"\s+hCCBMemInfo\s+\S+ -> obj (\d+)", line)
        if m:
            ccbs.append(int(m.group(1)))
        m = re.search(r"\[respond\] ALLOC obj \d+ heap=(\S+) .*size=(0x[0-9a-f]+) .*"
                      r"dva=([0-9a-f]+)", line)
        if m:
            allocs.append((step, m.group(1), int(m.group(3), 16), int(m.group(2), 16)))
    return steps, ccbs, allocs


def _chain(s: Snapshot, cmd: list[int], hp: dict[int, int]
           ) -> tuple[str, dict[str, int], dict[str, int]]:
    """(kind, {template name: address}, {PDS template name: data segment bytes}) of one
    command."""
    pds = cmd[0x3C // 4]
    bg = cmd[0x18 // 4] + ((cmd[0] & 0xFFFFFF) << 4)
    layers = (cmd[0] >> 25) & 0x3F
    sec, sec_data = pds_ptr(s.word(bg), pds)
    pri, pri_data = pds_ptr(s.word(bg + 8), pds)
    pe = cmd[0x24 // 4]
    use = hp[PIXELSHADER]
    kind = "fill" if layers == 0 else "copy"
    prim_use, prim_pds = (("USE_FILL", "PDS_PRIM") if kind == "fill" else
                          ("USE_COPY", "PDS_PRIM_1SRC"))
    return kind, {"PDS_PIXEVENT": pe, prim_pds: pri, "PDS_SEC": sec,
                  "USE_EOT": doutu_addr(s.word(pe + 12), use),
                  "USE_EOR": doutu_addr(s.word(pe + 16), use),
                  prim_use: doutu_addr(s.word(pri), use),
                  "USE_SEC": doutu_addr(s.word(sec), use)}, \
        {"PDS_PIXEVENT": cmd[0x28 // 4] << 4, prim_pds: pri_data, "PDS_SEC": sec_data}


def _extent(s: Snapshot, addr: int, others: list[int], unit: int, stride: int = 0) -> bytes:
    o = s.obj(addr)
    after = [a for a in others if addr < a < o.dva + o.size]
    end = min(after + ([addr + stride] if stride else []) + [o.dva + o.size])
    data = s.read(addr, min(end - addr, MAX_SLOT))
    n = len(data)
    while n >= unit and not any(data[n - unit:n]):
        n -= unit
    return data[:n]


def _command(s: Snapshot, ccb: int, offset: int) -> list[int]:
    raw = s.data(s.by_index(ccb))[offset - CMD_SHARED:offset - CMD_SHARED + CMD_BYTES]
    return list(struct.unpack(f"<{CMD_BYTES // 4}I", raw))


def ring_strides(seen: dict[tuple[str, str, int], list[int]]) -> dict[str, int]:
    """{program: the smallest step between two placements of it in one allocation of one
    run}, from {(run, program, allocation): [addresses]}: the slot of a ring that keeps
    other slots' contents (the copy's PDS primaries)."""
    out: dict[str, int] = {}
    for (_run, name, _obj), addrs in seen.items():
        a = sorted(set(addrs))
        for x, y in zip(a, a[1:]):
            out[name] = min(out.get(name, y - x), y - x)
    return out


def command_stream(r: Run) -> list[str]:
    """What breaks E004's reading of the CCB in one run (empty when it holds): the first
    command starts at 0 (its shared block at CMD_SHARED), every later one is further on in
    the same CCB, and each ends inside it, so the CCB does not wrap."""
    out = []
    for i, t in enumerate(r.transfers):
        if i == 0 and t.offset != CMD_SHARED:
            out.append(f"{r.name}: the first command starts at {t.offset - CMD_SHARED:#x}, "
                       "not 0")
        if i and t.ccb != r.transfers[i - 1].ccb:
            out.append(f"{r.name}/xfer{i:02d}: another CCB than the transfer before")
        if i and t.offset <= r.transfers[i - 1].offset:
            out.append(f"{r.name}/xfer{i:02d}: command at {t.offset:#x} not after the one "
                       f"before ({r.transfers[i - 1].offset:#x})")
        if t.offset - CMD_SHARED + CMD_BYTES > t.ccb_size:
            out.append(f"{r.name}/xfer{i:02d}: command at {t.offset:#x} reaches past the "
                       f"CCB ({t.ccb_size:#x})")
    return out


@dataclasses.dataclass
class Pattern:
    kind: str                       # "ring": a new address at every transfer; "allocation":
                                    # one address in a run
    shared_with: tuple[str, ...]    # the other templates in its objects


def placement_pattern(cap: list[Run]) -> dict[str, Pattern]:
    """{template: how the stack places it}, over the runs that place it more than once: a
    ring when every transfer has an address above the one before, an allocation when
    every transfer has the same; ValueError for anything else. shared_with: the templates
    that sit in an object it sits in (in any run)."""
    kinds: dict[str, set[str]] = {}
    shared: dict[str, set[str]] = {}
    for r in cap:
        objs: dict[int, set[str]] = {}
        addrs: dict[str, list[int]] = {}
        for t in r.transfers:
            for n, p in t.progs.items():
                addrs.setdefault(n, []).append(p.addr)
                objs.setdefault(t.snapshot.obj(p.addr).index, set()).add(n)
        for n, a in addrs.items():
            if len(a) < 2:
                kinds.setdefault(n, set())
            elif a == sorted(set(a)):
                kinds.setdefault(n, set()).add("ring")
            elif len(set(a)) == 1:
                kinds.setdefault(n, set()).add("allocation")
            else:
                raise ValueError(f"{r.name}: {n} is placed at {[hex(x) for x in a]}, neither "
                                 "a new address each time nor one")
        for names in objs.values():
            for n in names:
                shared.setdefault(n, set()).update(names - {n})
    for n, k in kinds.items():
        if len(k) != 1:
            raise ValueError(f"{n}: {sorted(k) or 'placed once in every run'}")
    return {n: Pattern(next(iter(k)), tuple(sorted(shared[n]))) for n, k in kinds.items()}


@dataclasses.dataclass
class CopyRing:
    slots: int                      # the ring's object holds this many slots
    slot_size: int
    used: int                       # the slot this copy's program is in
    idle_is_template: bool          # the slots after it are exactly the cut template
    patched_only: bool              # the slots up to it differ from it in patched bits only


def copy_ring(t: Transfer, template: bytes) -> CopyRing:
    """The ring of the copy's PDS primaries as the copy's snapshot holds it (E004): the
    object of PDS_PRIM_1SRC cut in slots the size of the template."""
    p = t.progs["PDS_PRIM_1SRC"]
    o = t.snapshot.obj(p.addr)
    data, n = t.snapshot.data(o), len(template)
    slots = [data[i:i + n] for i in range(0, o.size - n + 1, n)]
    used = (p.addr - o.dva) // n
    pb = patched_bits("PDS_PRIM_1SRC")
    return CopyRing(len(slots), n, used,
                    all(s == template for s in slots[used + 1:]),
                    all(not any((a ^ b) & ~m & 0xFF for a, b, m in zip(s, template, pb))
                        for s in slots[:used + 1]))


def load_run(run: pathlib.Path, strides: dict[str, int] | None = None) -> Run:
    run = pathlib.Path(run)
    hp = heaps(run)
    steps, ccbs, allocs = _bridge(run)
    dd = run / "dump3d"
    n = len(list(dd.glob("xfer*_in.bin")))
    if not len(steps) == len(ccbs) == n:
        raise ValueError(f"{run.name}: bridge.txt has {len(steps)} SGX_SUBMITTRANSFER lines "
                         f"and {len(ccbs)} CCB objects, dump3d {n} transfer snapshots; "
                         "they must agree")
    dirs = [dd / f"xfer{i:02d}" for i in range(n)]
    out = []
    for i in range(n):
        s = Snapshot(dirs[i], extra=dirs[i + 1:][::-1])
        words = struct.unpack("<5I", (dd / f"xfer{i:02d}_in.bin").read_bytes()[:20])
        cmd = _command(s, ccbs[i], words[3])
        kind, addrs, datas = _chain(s, cmd, hp)
        progs = {}
        for name, a in addrs.items():
            unit = 8 if name.startswith("USE") else 4
            progs[name] = Program(a, _extent(s, a, list(addrs.values()), unit,
                                             (strides or {}).get(name, 0)),
                                  datas.get(name, 0))
        out.append(Transfer(i, steps[i], kind, cmd, progs, s, words[3], ccbs[i],
                            s.by_index(ccbs[i]).size, words[4]))
    return Run(run.name, run, hp, out, allocs)


def load_capture(d: pathlib.Path) -> list[Run]:
    """Every run of a capture directory (a run: a directory with bridge.txt), each program
    cut to its slot with the ring strides of the whole capture."""
    dirs = [p.parent for p in sorted(pathlib.Path(d).glob("*/bridge.txt"))]
    seen: dict[tuple[str, str, int], list[int]] = {}
    for r in map(load_run, dirs):
        for t in r.transfers:
            for name, p in t.progs.items():
                seen.setdefault((r.name, name, t.snapshot.obj(p.addr).index), []).append(p.addr)
    strides = ring_strides(seen)
    return [load_run(p, strides) for p in dirs]


def trim(run: pathlib.Path) -> int:
    """Delete every snapshot object no chain reads; the CCB stays in the last transfer only
    (the client writes each command once and the CCB does not wrap within a run). Returns
    the number of files deleted."""
    run = pathlib.Path(run)
    r = load_run(run)
    _, ccbs, _ = _bridge(run)
    gone = 0
    for t in r.transfers:
        s = t.snapshot
        cmd = t.cmd
        keep = {s.obj(cmd[0x18 // 4] + ((cmd[0] & 0xFFFFFF) << 4)).file}
        keep |= {s.obj(p.addr).file for p in t.progs.values()}
        if t.index == len(r.transfers) - 1:
            keep.add(s.by_index(ccbs[t.index]).file)
        for p in s.dir.glob("obj*.bin"):
            if p.name not in keep:
                p.unlink()
                gone += 1
    return gone


def varying(images: list[bytes]) -> bytes:
    """The bits that differ between any two of equally long images."""
    first = images[0]
    out = bytearray(len(first))
    for img in images[1:]:
        for i, (a, b) in enumerate(zip(first, img)):
            out[i] |= a ^ b
    return bytes(out)


def _byte_class(v: int, care: int) -> bytes:
    """A regex class of every byte b with b & care == v & care."""
    if care == 0xFF:
        return re.escape(bytes([v]))
    return b"[" + b"".join(re.escape(bytes([b])) for b in range(256)
                           if b & care == v & care) + b"]"


def candidates(lib: bytes, img: bytes, care: bytes) -> list[int]:
    """Every library offset whose bytes equal img on the bits care selects."""
    pat = b"".join(_byte_class(v, c) for v, c in zip(img, care))
    return [m.start() for m in re.finditer(b"(?=" + pat + b")", lib, re.DOTALL)]


def load_windows(lib: bytes, img: bytes, starts: list[int], loads: int
                 ) -> dict[tuple[int, int], list[int]]:
    """{(start, loads): library offsets} of the runs of `loads` consecutive 8-byte USSE_LIMM
    instructions of img from each start, every bit but the immediates' (LIMM_MASK) cared."""
    care = (~LIMM_MASK & 0xFFFFFFFFFFFFFFFF).to_bytes(8, "little")
    return {(a, loads): candidates(lib, img[a:a + 8 * loads], care * loads)
            for a in starts}


def placement(src: int, cands: list[int], anchors: list[int]) -> str:
    """How a byte search fixes a piece at src: "unique"; "nearest" when src is the candidate
    nearest the template's unique pieces (contiguity); else "one of N" equal copies."""
    if cands == [src]:
        return "unique"
    if anchors:
        ref = sorted(anchors)[len(anchors) // 2]
        if min(cands, key=lambda c: abs(c - ref)) == src:
            return "nearest"
    return f"one of {len(cands)}"


# --- the analysis --------------------------------------------------------------------------

def _facts():
    import facts
    return facts


def programs(cap: list[Run]) -> dict[str, list[bytes]]:
    """{template: every captured copy}."""
    out: dict[str, list[bytes]] = {}
    for r in cap:
        for t in r.transfers:
            for name, p in t.progs.items():
                out.setdefault(name, []).append(p.data)
    return out


def _um():
    facts = _facts()
    return next(k for k in facts.KNOWN_INPUTS if k.role == "um" and k.templates)


def care(name: str, imgs: list[bytes]) -> bytes:
    """The bits of a template that hold the same value in every copy and that no patch of
    TQ_PATCHES writes: what the cut template itself must supply."""
    return bytes(0xFF & ~(v | p) for v, p in zip(varying(imgs), patched_bits(name)))


@dataclasses.dataclass
class PieceCheck:
    template: str
    src: int                   # facts.py's piece: libsrv_um offset, length, program offset
    size: int
    dst: int
    informative: int           # its bytes with a fixed, unpatched, non-zero bit
    candidates: list[int]      # library offsets holding the captured bytes on those bits
    how: str                   # placement()


def verify_pieces(cap: list[Run], lib: bytes) -> list[PieceCheck]:
    """Search libsrv_um for the captured bytes under each piece of facts.py (on the bits
    care() selects) and say how the search fixes the piece's offset."""
    facts = _facts()
    progs = programs(cap)
    out = []
    for t in _um().templates:
        name = facts.TQ_NAMES[t.template]
        imgs = progs[name]
        c, img = care(name, imgs), imgs[0]
        rows = []
        for p in t.pieces:
            span = slice(p.dst, p.dst + p.size)
            rows.append((p, sum(1 for k in range(p.dst, p.dst + p.size) if img[k] & c[k]),
                         candidates(lib, img[span], c[span])))
        anchors = [cands[0] for _, _, cands in rows if len(cands) == 1]
        for p, inf, cands in rows:
            out.append(PieceCheck(name, p.src, p.size, p.dst, inf, cands,
                                  placement(p.src, cands, anchors)))
    return out


def dest_register_search(cap: list[Run], lib: bytes) -> dict[tuple[int, int], list[int]]:
    """E004's search for USE_EOT's destination registers: the template's four immediate
    loads (+8, +16, +24, +32; r0-r3) looked up in the library alone and in runs of 2 to 4,
    with the immediates as don't-care and the registers cared. {(first load, loads):
    library offsets}."""
    img = programs(cap)["USE_EOT"][0]
    out: dict[tuple[int, int], list[int]] = {}
    for loads in range(1, 5):
        starts = [8 + 8 * k for k in range(5 - loads)]
        out.update(load_windows(lib, img, starts, loads))
    return out


def unexplained(cap: list[Run]) -> dict[str, list[int]]:
    """{template: [byte]} of bytes with a fixed, unpatched, non-zero bit that no piece of
    facts.py cuts: template bytes the old tables do not account for."""
    facts = _facts()
    progs = programs(cap)
    out = {}
    for t in _um().templates:
        name = facts.TQ_NAMES[t.template]
        cut = {p.dst + k for p in t.pieces for k in range(p.size)}
        c, img = care(name, progs[name]), progs[name][0]
        bad = [i for i, (b, m) in enumerate(zip(img, c)) if b & m and i not in cut]
        if bad:
            out[name] = bad
    return out


# The request behind each transfer (xfer.c's step) and the surfaces it names.
_IMG = re.compile(r"img (\S+) fmt=(\S+) size=(\d+)x(\d+)")
_FILL = re.compile(r"fill (\S+) colour=(0x[0-9a-f]+) rect=(\d+),(\d+),(\d+),(\d+)")
_COPY = re.compile(r"copy (\S+) pos=(\d+),(\d+) from (\S+) rect=(\d+),(\d+),(\d+),(\d+)")
BPP = {"8888": 4, "x888": 4, "565": 2}


@dataclasses.dataclass
class Surface:
    fmt: str
    width: int
    height: int
    addr: int

    @property
    def stride(self) -> int:
        """Bytes per line: the closed OpenVG stack pads each line to 8 pixels (E004)."""
        return BPP[self.fmt] * -(-self.width // 8) * 8


def surfaces(r: Run) -> dict[str, Surface]:
    """Each image of a run: the first GENERAL allocation its creation step made that is big
    enough to hold it."""
    out = {}
    for step, heap, dva, size in r.allocs:
        m = _IMG.fullmatch(step)
        if m and heap == "GENERAL" and m.group(1) not in out:
            name, fmt, w, h = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
            if size >= BPP[fmt] * w * h:
                out[name] = Surface(fmt, w, h, dva)
                if size < out[name].stride * h:
                    raise ValueError(f"{r.name}: image {name} is smaller than its lines")
    return out


def request(r: Run, t: Transfer) -> tuple[str, list[int] | None] | None:
    """(the destination format, the nine parameters of format §9.6/§10.4) of a transfer,
    from its request: the step's colour and rectangles and the surfaces' allocations. A
    copy's texture words describe its whole source surface. The parameters are None for
    another format than ARGB8888 (§9.6 covers that one); None for an unknown step."""
    import fwload
    surf = surfaces(r)
    m = _IMG.fullmatch(t.step)
    if m:
        s = surf[m.group(1)]
        if s.fmt != "8888":
            return s.fmt, None
        return s.fmt, fwload.fill_params(s.addr, s.width, s.height, s.stride, 0)
    m = _FILL.fullmatch(t.step)
    if m:
        s = surf[m.group(1)]
        if s.fmt != "8888":
            return s.fmt, None
        x, y, w, h = map(int, m.groups()[2:])
        return s.fmt, fwload.fill_params(s.addr, w, h, s.stride, int(m.group(2), 16), x, y)
    m = _COPY.fullmatch(t.step)
    if m:
        d, src = surf[m.group(1)], surf[m.group(4)]
        if d.fmt != "8888" or src.fmt != "8888":
            return d.fmt, None
        dx, dy = int(m.group(2)), int(m.group(3))
        w, h = int(m.group(7)), int(m.group(8))
        pbe = fwload.fill_params(d.addr, w, h, d.stride, 0, dx, dy)
        tex = fwload.copy_params(src.addr, 0, src.width, src.height, src.stride,
                                 (src.stride + 7) & ~7)
        return d.fmt, [0, *pbe[1:6], *tex[6:9]]
    return None


def firmware(lib: bytes):
    """The old tables as a firmware object: facts.py's pieces cut from lib, TQ_META,
    TQ_PATCHES and TQ_CMD."""
    import fwcutter
    import fwformat as F
    facts = _facts()
    u = fwcutter.identify(lib, "um")
    return F.Firmware(ddk=u.ddk, build_options=u.build_options, images={}, buffers=[],
                      patches=[], values={F.V_TQ_CMD: list(facts.TQ_CMD)},
                      tq_images={t.template: fwcutter.cut_template(u, t, lib)
                                 for t in u.templates},
                      tq_meta=list(facts.TQ_META), tq_patches=list(facts.TQ_PATCHES))


def _layout(r: Run, t: Transfer):
    import fwload
    facts = _facts()
    return fwload.Layout(addr={}, heap_base={PIXELSHADER: r.heaps[PIXELSHADER],
                                             PDSPIXEL: r.heaps[PDSPIXEL]},
                         tq_addr={facts.TQ_NAMES.index(n): p.addr
                                  for n, p in t.progs.items()})


@dataclasses.dataclass
class Rebuild:
    programs: int = 0
    transfers: int = 0
    other_format: list[str] = dataclasses.field(default_factory=list)  # not ARGB8888
    mismatches: list[str] = dataclasses.field(default_factory=list)


def rebuild(cap: list[Run], lib: bytes) -> Rebuild:
    """Rebuild every ARGB8888 transfer's programs with the old tables, placed where the
    capture placed them and given the request's parameters; compare byte for byte."""
    import fwload
    facts = _facts()
    fw = firmware(lib)
    out = Rebuild()
    for r in cap:
        for t in r.transfers:
            req = request(r, t)
            where = f"{r.name}/xfer{t.index:02d}"
            if req is None:
                out.mismatches.append(f"{where}: unknown step {t.step!r}")
                continue
            fmt, params = req
            if params is None:
                out.other_format.append(where)
                continue
            built = fwload.build_tq(fw, _layout(r, t), params)
            out.transfers += 1
            for name, p in t.progs.items():
                out.programs += 1
                if built.images[facts.TQ_NAMES.index(name)] != p.data:
                    out.mismatches.append(f"{where}: {name}")
    return out


def compare_cmd(cap: list[Run]) -> list[str]:
    """TQ_CMD's words (VALUES list 4) against every captured command."""
    import fwload
    facts = _facts()
    out = []
    for r in cap:
        for t in r.transfers:
            lay = _layout(r, t)
            for e in facts.TQ_CMD:
                v = fwload.tq_evaluate(e, lay, None, [0] * 9)
                if t.cmd[e.offset // 4] != v:
                    out.append(f"{r.name}/xfer{t.index:02d}: +{e.offset:#05x} "
                               f"{t.cmd[e.offset // 4]:#x} != {v:#x}")
    return out


LIMM_MASK = 0x0003F1F0001FFFFF           # format §4: e[20:0], e[40:36], e[49:44]
SB_MASK = 0x00C001F80FC00000             # format §9.4: e[27:22], e[40:35], e[55:54]


def patched_bits(name: str, except_const: bool = False) -> bytes:
    """The bits TQ_PATCHES writes in one template (except_const: leave out the CONST
    records)."""
    import fwformat as F
    facts = _facts()
    tid = facts.TQ_NAMES.index(name)
    size = next(m.size for m in facts.TQ_META if m.id == tid)
    out = bytearray(size)
    for e in facts.TQ_PATCHES:
        if e.buffer != tid or (except_const and e.kind == F.K_CONST):
            continue
        if e.encoding == F.ENC_WORD32:
            mask, n = 0xFFFFFFFF, 4
        else:
            mask, n = (LIMM_MASK if e.encoding == F.ENC_USSE_LIMM else SB_MASK), 8
        for k, b in enumerate(mask.to_bytes(n, "little")):
            out[e.offset + k] |= b
    return bytes(out)


def unpatched_variation(cap: list[Run]) -> dict[str, list[tuple[int, int]]]:
    """{template: [(byte, bits)]} of bits that vary between captured copies outside every
    field TQ_PATCHES writes."""
    out = {}
    for name, imgs in programs(cap).items():
        v, pb = varying(imgs), patched_bits(name)
        bad = [(i, b & ~m & 0xFF) for i, (b, m) in enumerate(zip(v, pb)) if b & ~m & 0xFF]
        if bad:
            out[name] = bad
    return out


@dataclasses.dataclass
class Field:
    template: str
    offset: int                # byte offset of the dword (PDS) or instruction (USE)
    encoding: str              # WORD32, USSE_LIMM, EMITPIX_SB, or "other"
    mask: int                  # the bits that vary
    label: str                 # what the value is in every copy: "DOUTU X", "ADDR X",
                               # "PARAM k", or "?"
    copies: int
    trc: set[int] = dataclasses.field(default_factory=set)   # DOUTU: bits [31:24] seen


def _doutu_low(addr: int, base: int) -> int:
    off = addr - base
    return ((off << 1) & 0xFFFF0) | ((off >> 19) & 0xF)


def fields(cap: list[Run]) -> list[Field]:
    """The varying fields of every template, each with the encoding its bits fit and the
    value that explains it in every copy: a DOUTU word or address of a program of the same
    transfer, or a parameter of the request (ARGB8888 transfers; format §9.6, §10.4)."""
    import fwload
    copies: dict[str, list[tuple[Run, Transfer, bytes]]] = {}
    for r in cap:
        for t in r.transfers:
            for name, p in t.progs.items():
                copies.setdefault(name, []).append((r, t, p.data))
    out = []
    for name, cs in copies.items():
        v = varying([d for _, _, d in cs])
        unit = 8 if name.startswith("USE") else 4
        for off in range(0, len(v), unit):
            mask = int.from_bytes(v[off:off + unit], "little")
            if not mask:
                continue
            if unit == 4:
                enc, get = "WORD32", (lambda w: w)
            elif mask & ~LIMM_MASK == 0:
                enc, get = "USSE_LIMM", fwload.limm_get
            elif mask & ~SB_MASK == 0:
                enc, get = "EMITPIX_SB", fwload.emitpix_sb_get
            else:
                enc, get = "other", (lambda w: w)
            labels: set[str] | None = None
            trc = set()
            for r, t, d in cs:
                val = get(int.from_bytes(d[off:off + unit], "little"))
                use = r.heaps[PIXELSHADER]
                here = set()
                for n, p in t.progs.items():
                    if unit == 4 and val & 0xFFFFFF == _doutu_low(p.addr, use) \
                            and name.startswith("PDS") and n.startswith("USE"):
                        here.add(f"DOUTU {n}")
                        trc.add(val >> 24)
                    if val == p.addr:
                        here.add(f"ADDR {n}")
                req = request(r, t)
                params = req[1] if req and req[1] is not None else None
                # a transfer without parameters (another format) constrains no PARAM label
                here |= {f"PARAM {k}" for k in range(9)
                         if params is None or params[k] == val}
                labels = here if labels is None else labels & here
            label = " / ".join(sorted(labels)) if labels else "?"
            out.append(Field(name, off, enc, mask, label, len(cs),
                             trc if label.startswith("DOUTU") else set()))
    return out


def compare_fields(found: list[Field]) -> dict[str, list[str]]:
    """TQ_PATCHES's per-transfer records (kinds PARAM, ADDR, DOUTU) against the fields:
    {"agree": [...], "differ": [...], "not varied": [...], "extra": [...]}."""
    import fwformat as F
    facts = _facts()
    enc = {F.ENC_WORD32: "WORD32", F.ENC_USSE_LIMM: "USSE_LIMM",
           F.ENC_EMITPIX_SB: "EMITPIX_SB"}
    by = {(f.template, f.offset): f for f in found}
    out: dict[str, list[str]] = {"agree": [], "differ": [], "not varied": [], "extra": []}
    seen = set()
    for e in facts.TQ_PATCHES:
        if e.kind == F.K_CONST:
            continue
        name = facts.TQ_NAMES[e.buffer]
        key = (name, e.offset if e.encoding == F.ENC_WORD32 else e.offset & ~7)
        want = {F.K_PARAM: f"PARAM {e.target}", F.K_ADDR: f"ADDR {facts.TQ_NAMES[e.target]}",
                F.K_DOUTU: f"DOUTU {facts.TQ_NAMES[e.target]}"}[e.kind]
        rec = f"{name} +{e.offset} {enc[e.encoding]} {want}"
        f = by.get(key)
        seen.add(key)
        if f is None:
            out["not varied"].append(rec)
        elif f.encoding == enc[e.encoding] and want in f.label.split(" / "):
            out["agree"].append(rec)
        else:
            out["differ"].append(f"{rec}: captured {f.encoding} {f.label}")
    for key, f in by.items():
        if key not in seen:
            out["extra"].append(f"{f.template} +{f.offset} {f.encoding} {f.label}")
    return out


@dataclasses.dataclass
class ConstPatch:
    template: str
    offset: int
    value: int                 # the record's addend
    captured: bool             # every captured copy holds it there
    cut: int                   # what the cut template holds there (both: the bits no
                               # other kind of record writes)

    @property
    def visible(self) -> bool:
        """The captures show it: the copies hold the value and the cut template does not.
        A patch that writes what the template already holds cannot be told from the
        template."""
        return self.captured and self.cut != self.value


def const_patches(cap: list[Run], lib: bytes) -> list[ConstPatch]:
    """Each CONST record of TQ_PATCHES against the captured copies and the cut template."""
    import fwformat as F
    import fwload
    facts = _facts()
    fw = firmware(lib)
    get = {F.ENC_WORD32: lambda w: w, F.ENC_USSE_LIMM: fwload.limm_get,
           F.ENC_EMITPIX_SB: fwload.emitpix_sb_get}
    imgs = programs(cap)
    out = []
    for e in facts.TQ_PATCHES:
        if e.kind != F.K_CONST:
            continue
        name = facts.TQ_NAMES[e.buffer]
        unit = 4 if e.encoding == F.ENC_WORD32 else 8
        off = e.offset if unit == 4 else e.offset & ~7

        # a USSE_LIMM record writes the immediate bits of a dword a CONST record also writes
        others = int.from_bytes(patched_bits(name, True)[off:off + unit], "little")

        def val(img: bytes) -> int:
            raw = int.from_bytes(img.ljust(off + unit, b"\0")[off:off + unit], "little")
            return get[e.encoding](raw & ~others)
        out.append(ConstPatch(name, e.offset, e.addend,
                              all(val(i) == e.addend for i in imgs[name]),
                              val(fw.tq_images[e.buffer])))
    return out


@dataclasses.dataclass
class Meta:
    heaps: set[int]
    sizes: set[int]
    align: int                 # the largest power of two (to a page) dividing every address
    straddles: int             # copies that cross a 4 KiB page
    pds_data: set[int]
    trc: set[int]              # DOUTU [31:24] of the programs that start it


def meta(cap: list[Run]) -> dict[str, Meta]:
    """What the captures show of each template's TQ_META record."""
    heap_of = {}
    for r in cap:
        for b, base in r.heaps.items():
            heap_of.setdefault(r.name, []).append((base, b))
    out: dict[str, Meta] = {}
    trc: dict[str, set[int]] = {}
    for f in fields(cap):
        if f.label.startswith("DOUTU"):
            trc.setdefault(f.label.split()[1], set()).update(f.trc)
    for r in cap:
        for t in r.transfers:
            for name, p in t.progs.items():
                m = out.setdefault(name, Meta(set(), set(), 0x1000, 0, set(),
                                              trc.get(name, set())))
                base = max((b for b in heap_of[r.name] if b[0] <= p.addr), default=(0, -1))
                m.heaps.add(base[1])
                m.sizes.add(len(p.data))
                while p.addr % m.align:
                    m.align //= 2
                m.straddles += p.addr % 0x1000 + len(p.data) > 0x1000
                if name.startswith("PDS"):
                    m.pds_data.add(p.pds_data)
    return out


def report(d: pathlib.Path, lib: bytes) -> str:
    """The facts E004 records, as text: counts, offsets, field positions; no program bytes."""
    cap = load_capture(d)
    ts = [t for r in cap for t in r.transfers]
    out = [f"{len(cap)} runs, {len(ts)} transfers: "
           f"{sum(t.kind == 'fill' for t in ts)} fills, {sum(t.kind == 'copy' for t in ts)} "
           f"copies"]
    out.append("\nTQ_META as captured (template: heap, size, align seen, straddles, PDS data,"
               " DOUTU TRC):")
    for name, m in sorted(meta(cap).items()):
        out.append(f"  {name}: heap {sorted(m.heaps)}, size {sorted(hex(x) for x in m.sizes)}"
                   f", align {m.align:#x}, straddles {m.straddles}, data "
                   f"{sorted(hex(x) for x in m.pds_data)}, trc {sorted(m.trc)}")
    out.append("\nfacts.py pieces (template +dst: src+len, informative bytes, candidates, how):")
    for c in verify_pieces(cap, lib):
        out.append(f"  {c.template} +{c.dst}: {c.src:#x}+{c.size}, {c.informative}, "
                   f"{len(c.candidates)}, {c.how}{'' if c.src in c.candidates else ' ABSENT'}")
    out.append(f"\nunexplained template bytes: {unexplained(cap) or 'none'}")
    out.append("\nvarying fields (template +offset: encoding, varying bits, value, copies):")
    for f in fields(cap):
        out.append(f"  {f.template} +{f.offset}: {f.encoding}, {f.mask:#x}, {f.label}"
                   f"{f' (TRC {sorted(f.trc)})' if f.trc else ''}, {f.copies}")
    for k, v in compare_fields(fields(cap)).items():
        out.append(f"TQ_PATCHES {k}: {len(v)}" + "".join(f"\n  {x}" for x in v))
    out.append("\nCONST records (template +offset = value, visible):")
    for c in const_patches(cap, lib):
        out.append(f"  {c.template} +{c.offset} = {c.value:#x}, "
                   f"{'visible' if c.visible else 'hidden'}"
                   f"{'' if c.captured else ' NOT IN THE CAPTURES'}")
    out.append("\nUSE_EOT's loads in the library (first load, loads: places):")
    for (a, n), cands in sorted(dest_register_search(cap, lib).items(),
                                key=lambda kv: kv[0][::-1]):
        out.append(f"  +{a}, {n}: {len(cands)}")
    rb = rebuild(cap, lib)
    out.append(f"\nrebuild with the old tables: {rb.transfers} ARGB8888 transfers, "
               f"{rb.programs} programs, {len(rb.mismatches)} mismatches"
               + "".join(f"\n  {x}" for x in rb.mismatches)
               + f"; other formats: {', '.join(rb.other_format) or 'none'}")
    bad = compare_cmd(cap)
    out.append(f"TQ_CMD: {len(facts_cmd())} words x {len(ts)} commands, {len(bad)} mismatches"
               + "".join(f"\n  {x}" for x in bad))
    out.append(f"bits varying outside TQ_PATCHES fields: {unpatched_variation(cap) or 'none'}")
    return "\n".join(out)


# --- the commands: the client CCB, its context, what each command holds -----------------

CMD_SIZE, CMD_FLAGS = 0xA4, 0xA8        # the size and flags words (transfer §2.3)
CMD_FENCE, CMD_UPDATES = 0x198, 0x19C   # fence_id, the update count
CMD_STATUS = CMD_SHARED + 0xB8          # the shared block's first status entry:
                                        # count, address, value
CMD_DUMMY = 0x20                        # the dummy flag of the flags word
CMD_SYNC_WORDS = (CMD_SHARED, CMD_SHARED + 0xB8)   # the sync block, up to the status entries


@dataclasses.dataclass
class Alloc:
    index: int
    heap: str
    attribs: int
    size: int
    before_first: bool              # made before the run's first SGX_SUBMITTRANSFER


def alloc_lines(bridge: pathlib.Path) -> list[Alloc]:
    """The ALLOC lines of a bridge.txt, in order."""
    out, seen = [], False
    for line in pathlib.Path(bridge).read_text().splitlines():
        if "(SGX_SUBMITTRANSFER)" in line:
            seen = True
        m = re.search(r"\[respond\] ALLOC obj (\d+) heap=(\S+) attribs=([0-9a-f]+) "
                      r"size=(0x[0-9a-f]+)", line)
        if m:
            out.append(Alloc(int(m.group(1)), m.group(2), int(m.group(3), 16),
                             int(m.group(4), 16), not seen))
    return out


def next_alloc(allocs: list[Alloc], index: int) -> Alloc | None:
    """The allocation made right after object `index` (the next index), if any."""
    return next((a for a in allocs if a.index == index + 1), None)


def ccb_image(r: Run) -> bytes | None:
    """The CCB as the last snapshot that holds it has it (trim keeps it in the last transfer
    only; the client writes each command once and the CCB does not wrap)."""
    for t in reversed(r.transfers):
        try:
            return t.snapshot.data(t.snapshot.by_index(t.ccb))
        except KeyError:
            continue
    return None


def command_words(r: Run) -> list[list[int]]:
    """Every command of the run in full (the size word's bytes from its start), [] when the
    CCB is not kept."""
    img = ccb_image(r)
    if img is None:
        return []
    out = []
    for t in r.transfers:
        o = t.offset - CMD_SHARED
        size = struct.unpack_from("<I", img, o + CMD_SIZE)[0]
        size = min(size, len(img) - o) & ~3
        out.append(list(struct.unpack_from(f"<{size // 4}I", img, o)))
    return out


def _ranges(offs: list[int]) -> str:
    out, i = [], 0
    while i < len(offs):
        j = i
        while j + 1 < len(offs) and offs[j + 1] == offs[j] + 4:
            j += 1
        out.append(f"{offs[i]:#x}" if i == j else f"{offs[i]:#x}-{offs[j] + 3:#x}")
        i = j + 1
    return ", ".join(out)


def _counts(values) -> str:
    c = collections.Counter(values)
    return ", ".join(f"{k:#x} x{n}" for k, n in sorted(c.items()))


def _obj_text(o: Obj) -> str:
    return f"obj {o.index} {o.name} size {o.size:#x} attribs {o.attribs:#x}"


def _object_at(snap, dva: int) -> Obj | None:
    return next((o for o in snap.objs if o.dva <= dva < o.dva + max(o.mapped, o.size)), None)


def _word_class(col: list[int], ns: list[int], snaps: list) -> str:
    if len(set(col)) == 1:
        return f"= {col[0]:#x}"
    ks = {(v - n) & 0xFFFFFFFF for v, n in zip(col, ns)}
    if len(ks) == 1:
        k = ks.pop()
        return "tracks n" + (f" + {k}" if k else "")
    objs = {(o.index if (o := _object_at(s, v)) else None) for v, s in zip(col, snaps)}
    if None not in objs and len(objs) <= 3:
        return f"addresses in obj {sorted(objs)} ({len(set(col))} distinct)"
    return f"varies ({len(set(col))} distinct, {sum(v == 0 for v in col)} zero)"


def commands_report(cap: list[Run]) -> str:
    """What the closed stack's transfer commands hold: the objects behind the kick, the
    stream of commands in the CCB, and every word of the command classed (zero, fixed,
    tracking the command's index n in the run, an address, varying). Counts and classes
    only; the fixed words are the command's own, not program words."""
    ts = [t for r in cap for t in r.transfers]
    out = [f"{len(ts)} commands in {len(cap)} runs"]
    out.append("\nobjects (per run: the CCB the kick names, the allocation after it, the "
               "context, the status address):")
    cnt: dict[str, int] = collections.Counter()
    for r in cap:
        last = r.transfers[-1]
        s = last.snapshot
        ccb = s.by_index(last.ccb)
        cnt[f"CCB: {_obj_text(ccb)}"] += 1
        br = r.dir / "bridge.txt"
        allocs = alloc_lines(br) if br.exists() else []
        nxt = next_alloc(allocs, ccb.index)
        if nxt:
            cnt[f"allocation after the CCB: obj {nxt.index} {nxt.heap} size {nxt.size:#x} "
                f"attribs {nxt.attribs:#x}"] += 1
        for a in allocs:
            if a.before_first and a.heap == "KERNEL_DATA" and a.attribs == 0x4F:
                cnt[f"KERNEL_DATA attribs 0x4f before the first transfer: obj {a.index} "
                    f"size {a.size:#x}"] += 1
        ctx = _object_at(s, last.ctx)
        if ctx:
            kept = any((t.snapshot.dir / ctx.file).exists() for t in r.transfers)
            cnt[f"context: {_obj_text(ctx)} kind {ctx.kind}"] += 1
            cnt["context bytes: " + ("kept" if kept else "not kept in any snapshot "
                                     "(trimmed)")] += 1
        else:
            cnt["context: not in the snapshot's objects"] += 1
    ws = {r.name: command_words(r) for r in cap}
    if not any(ws.values()):
        cnt["CCB not kept in any snapshot: the commands cannot be read"] += 1
    for r in cap:
        for t, w in zip(r.transfers, ws[r.name]):
            st = _object_at(t.snapshot, w[CMD_STATUS // 4 + 1]) if len(w) > CMD_STATUS // 4 \
                else None
            cnt["status address: " + (_obj_text(st) if st else "not in an object")] += 1
    out += [f"  {k} (x{n})" for k, n in cnt.items()]
    if not any(ws.values()):
        return "\n".join(out)

    out.append("\nstream in the CCB:")
    steps, ends, fits = collections.Counter(), [], 0
    for r in cap:
        w = ws[r.name]
        ts_ = r.transfers
        ends.append((ts_[-1].offset - CMD_SHARED + len(w[-1]) * 4, ts_[-1].ccb_size))
        for i in range(1, len(ts_)):
            steps[ts_[i].offset - ts_[i - 1].offset] += 1
            fits += ts_[i].offset - ts_[i - 1].offset == len(w[i - 1]) * 4
    inc = all(b.offset > a.offset for r in cap for a, b in zip(r.transfers, r.transfers[1:]))
    end, size = max(ends)
    out.append(f"  first command at "
               f"{_counts(r.transfers[0].offset - CMD_SHARED for r in cap)} (runs)")
    out.append(f"  steps between commands: {_counts(steps)}"
               + (" (each equal to the size word)" if fits == sum(steps.values()) else
                  f" ({fits} of {sum(steps.values())} equal to the size word)"))
    out.append(f"  last command ends at {end:#x} of the CCB's {size:#x}: "
               + ("no wrap" if inc and all(e <= z for e, z in ends) else "WRAPS or overruns"))

    cmds = [(r, i, w) for r in cap for i, w in enumerate(ws[r.name])]
    out.append(f"\nper command ({len(cmds)}):")
    out.append(f"  size word: {_counts(len(w) and w[CMD_SIZE // 4] for _, _, w in cmds)}")
    out.append(f"  flags: {_counts(w[CMD_FLAGS // 4] for _, _, w in cmds)}")
    out.append(f"  dummy flag {CMD_DUMMY:#x} set in "
               f"{sum(bool(w[CMD_FLAGS // 4] & CMD_DUMMY) for _, _, w in cmds)} commands")
    out.append(f"  update count: {_counts(w[CMD_UPDATES // 4] for _, _, w in cmds)}")
    fence = sum(w[CMD_FENCE // 4] == i for _, i, w in cmds)
    val = sum(w[CMD_STATUS // 4 + 2] == w[CMD_FENCE // 4] + 1 for _, _, w in cmds)
    out.append(f"  fence == n in {fence}/{len(cmds)}, status value == fence + 1 in "
               f"{val}/{len(cmds)} (n: the command's index in its run)")
    out.append(f"  status entries (count at +{CMD_STATUS - CMD_SHARED:#x}): "
               f"{_counts(w[CMD_STATUS // 4] for _, _, w in cmds)}")
    zero = sum(not any(w[CMD_SYNC_WORDS[0] // 4:CMD_SYNC_WORDS[1] // 4]) for _, _, w in cmds)
    out.append(f"  sync block (+0x0..+0xb7 of the shared block): all zero in {zero}/{len(cmds)}")

    n = min(len(w) for _, _, w in cmds)
    zeros, rows = [], []
    for k in range(n):
        col = [w[k] for _, _, w in cmds]
        if not any(col):
            zeros.append(k * 4)
        else:
            cls = _word_class(col, [i for _, i, _ in cmds],
                              [r.transfers[i].snapshot for r, i, _ in cmds])
            rows.append(f"  {k * 4:#x}{'' if cls.startswith('=') else ':'} {cls}")
    out.append(f"\nwords of the first {n * 4:#x} bytes of the command, over all commands:")
    out.append(f"  zero in every command: {_ranges(zeros)}")
    out += rows
    return "\n".join(out)


def facts_cmd() -> list:
    return list(_facts().TQ_CMD)


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "trim":
        for run in argv[1:]:
            print(f"{run}: {trim(pathlib.Path(run))} objects dropped")
        return 0
    if len(argv) in (2, 3) and argv[0] == "report":
        import fwcutter
        lib = pathlib.Path(argv[2]) if len(argv) == 3 else fwcutter.default_um_input()
        if lib is None:
            print("tqcapture.py: no libsrv_um.so (give it, or set RESGX545_CDV_LIBS)",
                  file=sys.stderr)
            return 1
        print(report(pathlib.Path(argv[1]), lib.read_bytes()))
        return 0
    if len(argv) == 2 and argv[0] == "commands":
        print(commands_report(load_capture(pathlib.Path(argv[1]))))
        return 0
    print("\n".join(__doc__.strip().splitlines()[-4:]), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
