# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests for tqcapture.py: the transfer captures (captures/firmware/transfer.toml) read as a
black box (doc/specs/fw_format.md §9-§10, evidence E004).

The synthetic tests build snapshots in the harness's format from made-up words; the capture
tests run on the private data repository's firmware/transfer and the user's libsrv_um.so,
and skip without them. No test stores a word of a closed program: they check counts,
offsets, field positions and agreement with facts.py.
"""
import collections
import pathlib
import struct
import sys

import pytest

import facts
import fwcutter
import tqcapture as T

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "records"))
import datasets  # noqa: E402

CAPTURE = (datasets.repos().get("data-private", pathlib.Path("/nonexistent"))
           / "firmware" / "transfer")
LIB = fwcutter.default_um_input()

USE, PDS, GEN = 0xF4000000, 0xE4000000, 0x08000000


# --- a synthetic run in the harness's format -----------------------------------------------

def _obj_line(k, heap, name, dva, size, mapped):
    return (f"{k:3d} heap={heap:<2d} {name:<24s} dva={dva:08x} size={size:#08x} "
            f"mapped={mapped:#08x} attribs=0000000d kind=0\n")


def doutu(addr, temps=0, base=USE):
    off = addr - base
    return ((off << 1) & 0xFFFF0) | ((off >> 19) & 0xF) | ((temps + 3) >> 2) << 24


def make_run(tmp_path, layers=0, use_base=USE, env=""):
    """One transfer: a command in a CCB object, a background object, a PDS ring with the
    pixel-event, primary and secondary programs, a USE ring with EOT and the primary's
    shader, and static USE objects for EOR and the secondary. Every program is made-up
    words ending in a non-zero word."""
    run = tmp_path / "run"
    d = run / "dump3d" / "xfer00"
    d.mkdir(parents=True)
    objs = {}                                        # k -> (heap, name, dva, bytearray)
    ccb, bgo, pring, uring, ueor, usec = 3, 4, 5, 6, 7, 8
    objs[ccb] = (3, "KERNEL_DATA", 0xF0017000, bytearray(0x1000))
    objs[bgo] = (0, "GENERAL", GEN + 0x82000, bytearray(0x1000))
    objs[pring] = (6, "PDSPIXEL_CODEDATA", PDS + 0x1000, bytearray(0x1000))
    objs[uring] = (4, "PIXELSHADER", use_base + 0x1000, bytearray(0x1000))
    objs[ueor] = (4, "PIXELSHADER", use_base + 0x2000, bytearray(0x1000))
    objs[usec] = (4, "PIXELSHADER", use_base + 0x3000, bytearray(0x1000))
    sizes = {ccb: 0x200, bgo: 0x80, pring: 0x400, uring: 0x400, ueor: 0x18, usec: 0x10}
    pe, pri, sec = PDS + 0x1000, PDS + 0x10D0, PDS + 0x10F0
    eot, fsh, eor, ush = use_base + 0x1000, use_base + 0x1050, use_base + 0x2000, \
        use_base + 0x3000

    def put(k, off, words):
        struct.pack_into(f"<{len(words)}I", objs[k][3], off, *words)
    cmd = [0] * 0x70
    cmd[0] = ((objs[bgo][2] - GEN) >> 4) | layers << 25
    cmd[0x18 // 4] = GEN
    cmd[0x24 // 4] = pe
    cmd[0x28 // 4] = 5
    cmd[0x3C // 4] = PDS
    put(ccb, 0, cmd)
    put(bgo, 0, [((sec - PDS) >> 4) | 1 << 26, 0x30000, ((pri - PDS) >> 4) | 1 << 26])
    put(pring, 0, [doutu(eot, 4, use_base), 0x800000, 0, doutu(eot, 4, use_base),
                   doutu(eor, 1, use_base), 0xC00000] + [0] * 14 + [0x1111] * 28 + [0x2222])
    put(pring, 0xD0, [doutu(fsh, 0, use_base), 4, 0, 0, 0x3333, 0x4444])
    put(pring, 0xF0, [doutu(ush, 0, use_base), 4, 0, 0, 0x5555, 0x6666])
    put(uring, 0, [0x7777] * 14)
    put(uring, 0x50, [0x8888] * 4)
    put(ueor, 0, [0x9999] * 6)
    put(usec, 0, [0xAAAA] * 4)
    lines = ""
    for k in sorted(objs):
        heap, name, dva, data = objs[k]
        (d / f"obj{k:03d}_{dva:08x}.bin").write_bytes(bytes(data))
        lines += _obj_line(k, heap, name, dva, sizes[k], len(data))
    (d / "objects.txt").write_text(lines)
    words = [0, 0xDEAD0001, 0x4D41000D, 0xAC, 0xF002A000] + [0] * 17
    (run / "dump3d" / "xfer00_in.bin").write_bytes(struct.pack("<22I", *words))
    (run / "bridge.txt").write_text(
        "==== fill a colour=0xff336699 rect=3,5,40,30 (objects so far: 9, kicks: 0) ====\n"
        "  -> nr=96 (SGX_SUBMITTRANSFER) insz=88 outsz=8\n"
        "     hCCBMemInfo                        4d41000d -> obj 3 KERNEL_DATA "
        "dva=f0017000 size=0x200\n")
    (run / "env.txt").write_text(env)
    return run, dict(pe=pe, pri=pri, sec=sec, eot=eot, fsh=fsh, eor=eor, ush=ush)


def test_parse_objects():
    text = _obj_line(19, 4, "PIXELSHADER", 0xF4001000, 0x800, 0x1000)
    (o,) = T.parse_objects(text)
    assert (o.index, o.heap, o.name, o.dva, o.size, o.mapped) == \
        (19, 4, "PIXELSHADER", 0xF4001000, 0x800, 0x1000)
    assert o.file == "obj019_f4001000.bin"


def test_doutu_and_pds_pointer_decode():
    for off in (0, 8, 0x1050, 0x7FFF8, 0x80000, 0x123458):
        assert T.doutu_addr(doutu(USE + off, 4), USE) == USE + off
    assert T.pds_ptr(((0x10F0) >> 4) | 3 << 26, PDS) == (PDS + 0x10F0, 0x30)


def test_heaps_default_and_env(tmp_path):
    run, _ = make_run(tmp_path)
    assert T.heaps(run) == {0: GEN, 4: USE, 6: PDS}
    (run / "env.txt").write_text("MOCK_HEAP_BASE_4=0xF4100000\nMOCK_HEAP_START=0x5000\n")
    assert T.heaps(run)[4] == 0xF4100000


@pytest.mark.parametrize("layers", [0, 1])
def test_read_transfer_follows_the_chain(tmp_path, layers):
    run, a = make_run(tmp_path, layers)
    (t,) = T.load_run(run).transfers
    assert t.kind == ("fill" if layers == 0 else "copy")
    prim_use, prim_pds = ("USE_FILL", "PDS_PRIM") if layers == 0 else ("USE_COPY",
                                                                       "PDS_PRIM_1SRC")
    want = {"PDS_PIXEVENT": a["pe"], prim_pds: a["pri"], "PDS_SEC": a["sec"],
            "USE_EOT": a["eot"], prim_use: a["fsh"], "USE_EOR": a["eor"], "USE_SEC": a["ush"]}
    assert {k: p.addr for k, p in t.progs.items()} == want
    assert t.cmd[0x24 // 4] == a["pe"]
    assert t.step == "fill a colour=0xff336699 rect=3,5,40,30"


def test_program_extents(tmp_path):
    run, _ = make_run(tmp_path)
    (t,) = T.load_run(run).transfers
    size = {k: len(p.data) for k, p in t.progs.items()}
    # the slot up to the next program, without its trailing zero words (USE: 8 bytes);
    # a program alone in its object: up to the object's size
    assert size == {"PDS_PIXEVENT": 0xC4, "PDS_PRIM": 0x18, "PDS_SEC": 0x18,
                    "USE_EOT": 0x38, "USE_FILL": 0x10, "USE_EOR": 0x18, "USE_SEC": 0x10}


def test_moved_use_heap(tmp_path):
    run, a = make_run(tmp_path, use_base=0xF4100000, env="MOCK_HEAP_BASE_4=0xF4100000\n")
    (t,) = T.load_run(run).transfers
    assert t.progs["USE_EOT"].addr == a["eot"]


def test_bridge_must_agree_with_the_snapshots(tmp_path):
    """One SGX_SUBMITTRANSFER line, one CCB object and one snapshot per transfer: a bridge
    that disagrees is an error, not a transfer with an empty step."""
    run, _ = make_run(tmp_path)
    good = (run / "bridge.txt").read_text()
    (run / "bridge.txt").write_text(good + "  -> nr=96 (SGX_SUBMITTRANSFER) insz=88 outsz=8\n")
    with pytest.raises(ValueError, match="2 SGX_SUBMITTRANSFER.*1 CCB.*1 transfer snapshot"):
        T.load_run(run)
    (run / "bridge.txt").write_text(good.replace("hCCBMemInfo", "hOther"))
    with pytest.raises(ValueError, match="0 CCB"):
        T.load_run(run)


def test_transfer_records_where_its_command_sits(tmp_path):
    run, _ = make_run(tmp_path)
    (t,) = T.load_run(run).transfers
    assert (t.offset, t.ccb, t.ccb_size) == (0xAC, 3, 0x200)


class _Obj:
    def __init__(self, index):
        self.index = index


class _Snap:
    """The snapshot of a made-up transfer: the object of an address is its 0x1000 page."""
    def obj(self, dva):
        return _Obj(dva >> 12)


def _run(offsets, placements, ccb_size=0x1000, ccbs=None):
    """A Run of made-up transfers: placements is [{template: address}]."""
    ts = [T.Transfer(i, "", "fill", [], {n: T.Program(a, b"") for n, a in pl.items()},
                     _Snap(), offsets[i], (ccbs or [7] * len(offsets))[i], ccb_size)
          for i, pl in enumerate(placements)]
    return T.Run("r", pathlib.Path("."), {}, ts, [])


def test_command_stream_problems():
    ok = _run([0xAC, 0x26C, 0x42C], [{}, {}, {}])
    assert T.command_stream(ok) == []
    wrapped = _run([0xAC, 0x26C, 0xAC], [{}, {}, {}])
    assert any("not after" in p for p in T.command_stream(wrapped))
    late = _run([0x100, 0x2C0], [{}, {}])
    assert any("first command" in p for p in T.command_stream(late))
    over = _run([0xAC, 0x1000], [{}, {}], ccb_size=0x1000)
    assert any("past the CCB" in p for p in T.command_stream(over))
    moved = _run([0xAC, 0x26C], [{}, {}], ccbs=[7, 8])
    assert any("another CCB" in p for p in T.command_stream(moved))


def test_placement_pattern_tells_rings_from_allocations():
    ring = {"USE_EOT": 0xF4001000, "USE_FILL": 0xF4001050, "USE_SEC": 0xF4033000}
    run = _run([0xAC, 0x26C, 0x42C],
               [ring, {**ring, "USE_EOT": 0xF4001060, "USE_FILL": 0xF40010B0},
                {**ring, "USE_EOT": 0xF40010C0, "USE_FILL": 0xF4001110}])
    pat = T.placement_pattern([run])
    assert pat["USE_EOT"].kind == "ring" and pat["USE_SEC"].kind == "allocation"
    assert pat["USE_EOT"].shared_with == ("USE_FILL",)
    assert pat["USE_SEC"].shared_with == ()
    # a ring that goes back is neither a ring nor an allocation
    back = _run([0xAC, 0x26C], [{"USE_EOT": 0xF4001060}, {"USE_EOT": 0xF4001000}])
    with pytest.raises(ValueError, match="USE_EOT"):
        T.placement_pattern([back])


def test_load_windows_are_found_with_the_immediates_masked():
    load = bytes([0x11, 0x22, 0x33, 0x04, 0xAA, 0xBB, 0xCC, 0xDD])
    other = bytes([0x99, 0x88, 0x35, 0x04, 0xAA, 0xBB, 0xCC, 0xDD])   # same load, other imm
    lib = b"\x55" * 16 + other + other + b"\x55" * 8 + load
    img = bytes(8) + load + load
    # the immediate is e[20:0], e[40:36], e[49:44]: its bits are don't-care
    assert T.load_windows(lib, img, [8], 1) == {(8, 1): [16, 24, 40]}
    assert T.load_windows(lib, img, [8], 2) == {(8, 2): [16]}
    assert T.load_windows(lib, img, [8, 16], 1) == {(8, 1): [16, 24, 40],
                                                    (16, 1): [16, 24, 40]}


def test_const_patch_is_visible_when_captured_and_not_in_the_template():
    c = T.ConstPatch("USE_EOT", 16, 1 << 21, captured=True, cut=0)
    assert c.visible
    assert not T.ConstPatch("PDS_PRIM", 8, 0, captured=True, cut=0).visible
    # a value the copies do not hold is no evidence, whatever the template has
    assert not T.ConstPatch("USE_EOT", 16, 1 << 21, captured=False, cut=0).visible


def test_trim_keeps_the_chain(tmp_path):
    run, _ = make_run(tmp_path)
    d = run / "dump3d" / "xfer00"
    (d / "obj099_c0001000.bin").write_bytes(b"\0" * 16)        # a stray object
    T.trim(run)
    kept = sorted(p.name for p in d.glob("obj*.bin"))
    assert len(kept) == 6 and "obj099_c0001000.bin" not in kept
    (t,) = T.load_run(run).transfers                         # still readable
    assert len(t.progs) == 7


def test_trim_keeps_the_ccb_in_the_last_transfer_only(tmp_path):
    run, _ = make_run(tmp_path)
    dd = run / "dump3d"
    import shutil
    shutil.copytree(dd / "xfer00", dd / "xfer01")
    (dd / "xfer01_in.bin").write_bytes((dd / "xfer00_in.bin").read_bytes())
    with open(run / "bridge.txt", "a") as f:
        f.write("  -> nr=96 (SGX_SUBMITTRANSFER) insz=88 outsz=8\n")
        f.write("     hCCBMemInfo                        4d41000d -> obj 3 KERNEL_DATA "
                "dva=f0017000 size=0x200\n")
    T.trim(run)
    assert not list((dd / "xfer00").glob("obj003_*"))
    assert list((dd / "xfer01").glob("obj003_*"))
    assert [t.cmd[9] for t in T.load_run(run).transfers] == [PDS + 0x1000] * 2


def test_varying_bits():
    assert T.varying([b"\x01\x02", b"\x03\x02", b"\x01\x06"]) == b"\x02\x04"


def test_candidates_mask_the_patched_bits():
    """A field a patch overwrites in every copy matches whatever the library holds."""
    lib = b"\x55" * 64 + b"PQRS" + bytes([0x0F, 0xAB]) + b"TUVW" + b"\x55" * 8 + b"PQRS"
    img = b"PQRS" + bytes([0xF0, 0xAB]) + b"TUVW"
    care = b"\xff" * 4 + bytes([0x00, 0xFF]) + b"\xff" * 4
    assert T.candidates(lib, img, care) == [64]
    assert T.candidates(lib, b"PQRS", b"\xff" * 4) == [64, 82]


def test_placement():
    assert T.placement(0x100, [0x100], []) == "unique"
    assert T.placement(0x100, [0x40, 0x100, 0x900], [0x120, 0x130, 0x7000]) == "nearest"
    assert T.placement(0x900, [0x40, 0x100, 0x900], [0x120]) == "one of 3"
    assert T.placement(0x40, [0x40, 0x100], []) == "one of 2"


# --- the commands report ------------------------------------------------------------------

class _FakeSnap:
    """A snapshot with the CCB object kept (or not) and a list of objects."""
    def __init__(self, objs, ccb=None):
        self.objs = objs
        self.ccb = ccb
        self.dir = pathlib.Path("fake")

    def by_index(self, k):
        return next(o for o in self.objs if o.index == k)

    def data(self, o):
        if o.index == 3 and self.ccb is not None:
            return self.ccb
        raise KeyError("not kept")


def _command_words(n, size=0x1C0, flags=0x8, updates=0, status=0xF0029000):
    """A made-up command: size, flags, one status entry whose value is n + 1, the fence n."""
    w = [0] * (size // 4)
    w[0xA4 // 4], w[0xA8 // 4] = size, flags
    w[(0xAC + 0xB8) // 4], w[(0xAC + 0xBC) // 4], w[(0xAC + 0xC0) // 4] = 1, status, n + 1
    w[0x198 // 4], w[0x19C // 4] = n, updates
    w[0x3C // 4] = 0x1234        # a fixed word
    w[0x40 // 4] = 0x100 + n     # a varying one
    return w


def _cmd_run(words_list, ccb_size=0x1000, keep=True, objs_extra=()):
    ccb = bytearray(ccb_size)
    off = 0
    offsets = []
    for w in words_list:
        struct.pack_into(f"<{len(w)}I", ccb, off, *w)
        offsets.append(off + T.CMD_SHARED)
        off += len(w) * 4
    objs = [T.Obj(3, 3, "KERNEL_DATA", 0xF0017000, ccb_size, 0x1000, 0x4F, 0),
            T.Obj(4, 3, "KERNEL_DATA", 0xF0018000, 8, 0x1000, 0x4F, 0),
            T.Obj(9, 3, "KERNEL_DATA", 0xF0029000, 4, 0x1000, 0x4F, 0),
            T.Obj(7, 3, "KERNEL_DATA", 0xF002A000, 0xB4, 0x1000, 0, 2), *objs_extra]
    snap = _FakeSnap(objs, bytes(ccb) if keep else None)
    ts = [T.Transfer(i, "", "fill", [], {}, snap, offsets[i], 3, ccb_size,
                     ctx=0xF002A000) for i in range(len(words_list))]
    return T.Run("r", pathlib.Path("."), {}, ts, [])


def test_command_words_cut_by_size():
    r = _cmd_run([_command_words(0), _command_words(1, size=0x1E0, updates=1)])
    c = T.command_words(r)
    assert [len(x) * 4 for x in c] == [0x1C0, 0x1E0]
    assert c[1][0x198 // 4] == 1


def test_commands_report_counts_the_status_rules():
    run = _cmd_run([_command_words(n) for n in range(3)])
    text = T.commands_report([run])
    assert "3 commands in 1 runs" in text
    assert "size word: 0x1c0 x3" in text
    assert "flags: 0x8 x3" in text
    assert "dummy flag 0x20 set in 0 commands" in text
    assert "fence == n in 3/3, status value == fence + 1 in 3/3" in text
    assert "update count: 0x0 x3" in text
    assert "0x3c = 0x1234" in text
    assert "0x40: tracks n + 256" in text or "0x40: varies" in text


def test_commands_report_notices_a_broken_rule():
    ws = [_command_words(n) for n in range(3)]
    ws[2][0xAC // 4 + 0xC0 // 4] = 99                # a status value not fence + 1
    ws[1][0xA8 // 4] |= 0x20                         # a dummy command
    text = T.commands_report([_cmd_run(ws)])
    assert "status value == fence + 1 in 2/3" in text
    assert "dummy flag 0x20 set in 1 commands" in text


def test_commands_report_follows_the_stream_and_wrap():
    run = _cmd_run([_command_words(n) for n in range(3)])
    text = T.commands_report([run])
    assert "steps between commands: 0x1c0 x2 (each equal to the size word)" in text
    assert "last command ends at 0x540 of the CCB's 0x1000: no wrap" in text


def test_commands_report_says_when_the_ccb_is_trimmed():
    text = T.commands_report([_cmd_run([_command_words(0)], keep=False)])
    assert "CCB not kept in any snapshot" in text


def test_commands_report_describes_the_objects():
    run = _cmd_run([_command_words(0)])
    text = T.commands_report([run])
    assert "CCB: obj 3 KERNEL_DATA size 0x1000 attribs 0x4f" in text
    assert "context: obj 7 KERNEL_DATA size 0xb4 attribs 0x0 kind 2" in text
    assert "context bytes: not kept" in text
    assert "status address: obj 9 KERNEL_DATA size 0x4" in text


def test_alloc_lines(tmp_path):
    p = tmp_path / "bridge.txt"
    p.write_text(
        "   [respond] ALLOC obj 13 heap=KERNEL_DATA attribs=0000004f size=0x104c8 align=0x1000"
        " dva=f0017000 hMap=4d41000d sync=-1\n"
        "   [respond] ALLOC obj 14 heap=KERNEL_DATA attribs=0000004f size=0x8 align=0x20"
        " dva=f0028000 hMap=4d41000e sync=-1\n"
        "  -> nr=96 (SGX_SUBMITTRANSFER) insz=88 outsz=8 IN=[]\n"
        "   [respond] ALLOC obj 15 heap=SYNCINFO attribs=00000003 size=0x4 align=0x10"
        " dva=e0004000 hMap=4d41000f sync=16\n")
    a = T.alloc_lines(p)
    assert [(x.index, x.heap, x.attribs, x.size, x.before_first) for x in a] == [
        (13, "KERNEL_DATA", 0x4F, 0x104C8, True), (14, "KERNEL_DATA", 0x4F, 8, True),
        (15, "SYNCINFO", 3, 4, False)]


def test_alloc_pairs_find_the_ccb_and_its_neighbour():
    allocs = [T.Alloc(4, "KERNEL_DATA", 0x4F, 0x10420, True),
              T.Alloc(5, "KERNEL_DATA", 0x4F, 8, True),
              T.Alloc(13, "KERNEL_DATA", 0x4F, 0x104C8, True),
              T.Alloc(14, "KERNEL_DATA", 0x4F, 8, True)]
    assert T.next_alloc(allocs, 13).index == 14
    assert T.next_alloc(allocs, 14) is None


# --- the captures ------------------------------------------------------------------------

@pytest.fixture(scope="module")
def cap():
    if not CAPTURE.is_dir():
        pytest.skip("SKIPPED, NOT PASSED: the transfer captures are not present (set "
                    "RESGX545_DATA_PRIVATE to the private data repository; looked for "
                    f"{CAPTURE})")
    return T.load_capture(CAPTURE)


@pytest.fixture(scope="module")
def lib():
    if LIB is None:
        pytest.skip("SKIPPED, NOT PASSED: libsrv_um.so not found (set RESGX545_CDV_LIBS to "
                    "the Cedarview package's usr/lib/, or SGX545_LIBSRV_UM to the file)")
    return LIB.read_bytes()


def test_capture_has_fills_and_copies(cap):
    """E004's counts: 14 runs, 67 transfers, 52 fills and 15 copies."""
    ts = [t for r in cap for t in r.transfers]
    assert (len(cap), len(ts)) == (14, 67)
    assert [t.kind for t in ts].count("fill") == 52
    assert [t.kind for t in ts].count("copy") == 15
    # the kind is what the chain says (a TSP layer or none); the step agrees
    assert all((t.kind == "copy") == bool(T._COPY.fullmatch(t.step)) for t in ts)
    # every template of facts is placed by some transfer
    assert {n for r in cap for t in r.transfers for n in t.progs} == set(facts.TQ_NAMES)


def test_capture_sizes_match_tq_meta(cap):
    meta = {facts.TQ_NAMES[m.id]: m for m in facts.TQ_META}
    for r in cap:
        for t in r.transfers:
            for name, p in t.progs.items():
                assert len(p.data) == meta[name].size, (r.name, t.index, name)


def test_capture_placement_rules(cap):
    """Each placed program is aligned as TQ_META says, in its heap, inside one page."""
    meta = {facts.TQ_NAMES[m.id]: m for m in facts.TQ_META}
    for r in cap:
        for t in r.transfers:
            for name, p in t.progs.items():
                m = meta[name]
                assert p.addr % m.align == 0
                assert p.addr >= r.heaps[m.heap]
                assert p.addr % 0x1000 + m.size <= 0x1000


def test_pieces_are_found_where_facts_cut_them(cap, lib):
    """Every piece of facts.py: the library holds the captured bytes at its offset."""
    checks = T.verify_pieces(cap, lib)
    assert len(checks) == sum(len(t.pieces) for t in T._um().templates)
    for c in checks:
        assert c.src in c.candidates, (c.template, hex(c.src))
    # E004: 7 pieces are the only place with their bytes, 8 are the candidate nearest the
    # template's unique pieces, 6 are one of several equal copies
    how = collections.Counter("equal" if c.how.startswith("one of") else c.how
                              for c in checks)
    assert how == {"unique": 7, "nearest": 8, "equal": 6}
    # the equal copies the document names
    equal = {(c.template, c.dst): len(c.candidates) for c in checks
             if c.how.startswith("one of")}
    assert equal[("USE_FILL", 0)] == 53
    assert sorted(equal.values()) == [2, 2, 2, 2, 2, 53]


def test_every_template_byte_is_cut_or_patched(cap):
    assert T.unexplained(cap) == {}


def test_patches_agree_with_facts(cap, lib):
    """The old tables (pieces + TQ_PATCHES), placed where the capture placed each program
    and given the parameters of the request, rebuild every captured program exactly."""
    result = T.rebuild(cap, lib)
    assert result.mismatches == []
    # E004: the 63 ARGB8888 transfers rebuild all 441 programs (the other 4 are XRGB8888
    # and RGB565 fills, which the parameters do not cover)
    assert (result.transfers, result.programs) == (63, 441)
    assert len(result.other_format) == 4


def test_varying_fields_are_patches(cap):
    """Every bit that varies across the captures lies in a field TQ_PATCHES writes."""
    assert T.unpatched_variation(cap) == {}


def test_command_words_agree_with_tq_cmd(cap):
    """E004: the 12 words of TQ_CMD hold in all 67 commands."""
    assert len(facts.TQ_CMD) == 12 and sum(len(r.transfers) for r in cap) == 67
    assert T.compare_cmd(cap) == []


def test_commands_follow_each_other_in_the_ccb(cap):
    """E004: the first command of a run starts at 0 (its shared block at 0xac) and the CCB
    does not wrap within a run."""
    for r in cap:
        assert T.command_stream(r) == [], r.name
        assert r.transfers[0].offset == T.CMD_SHARED
    assert {t.ccb_size for r in cap for t in r.transfers} == {0x104C8}


def test_rings_and_allocations(cap):
    """E004: the fill shader and USE_EOT share one ring, the pixel-event, PDS_PRIM and
    PDS_SEC another, each transfer at a new address; USE_SEC, USE_EOR and USE_COPY have one
    address a run, in an object of their own; the copy's PDS primaries are a ring of their
    own."""
    pat = T.placement_pattern(cap)
    assert {n: (p.kind, p.shared_with) for n, p in pat.items()} == {
        "USE_FILL": ("ring", ("USE_EOT",)), "USE_EOT": ("ring", ("USE_FILL",)),
        "PDS_PRIM": ("ring", ("PDS_PIXEVENT", "PDS_SEC")),
        "PDS_SEC": ("ring", ("PDS_PIXEVENT", "PDS_PRIM")),
        "PDS_PIXEVENT": ("ring", ("PDS_PRIM", "PDS_SEC")),
        "PDS_PRIM_1SRC": ("ring", ()),
        "USE_SEC": ("allocation", ()), "USE_EOR": ("allocation", ()),
        "USE_COPY": ("allocation", ())}


def test_copy_primaries_ring_has_16_slots(cap, lib):
    """E004: the copy's PDS primaries take 64-byte slots of a ring of 16; the slots after
    the used one hold exactly the template (code written, data zero), the others differ
    from it in patched fields only."""
    tpl = T.firmware(lib).tq_images[facts.TQ_NAMES.index("PDS_PRIM_1SRC")]
    n = 0
    for r in cap:
        copies = [t for t in r.transfers if t.kind == "copy"]
        for k, t in enumerate(copies):
            ring = T.copy_ring(t, tpl)
            assert (ring.slots, ring.slot_size, ring.used) == (16, 0x40, k)
            assert ring.idle_is_template and ring.patched_only
            n += 1
    assert n == 15


def test_ring_strides():
    """The step between consecutive placements of one program in one allocation."""
    seen = {("r1", "PDS_PRIM_1SRC", 74): [0xE4003000, 0xE4003040, 0xE4003080],
            ("r2", "PDS_PRIM_1SRC", 74): [0xE4003000],
            ("r1", "USE_FILL", 19): [0xF4001050, 0xF40010B0]}
    assert T.ring_strides(seen) == {"PDS_PRIM_1SRC": 0x40, "USE_FILL": 0x60}


def test_varying_fields_agree_with_tq_patches(cap):
    """Each per-transfer record of TQ_PATCHES (PARAM, ADDR, DOUTU) is a field that varies
    in the captures, with that encoding and that value; no other field varies."""
    found = T.fields(cap)
    assert len(found) == 15
    cmp = T.compare_fields(found)
    assert cmp["differ"] == [] and cmp["extra"] == [] and cmp["not varied"] == []
    assert len(cmp["agree"]) == 15


def test_const_records_and_which_the_captures_show(cap, lib):
    """E004: 16 CONST records; every one holds in every copy; 11 write values the cut
    templates lack, 5 write the 0 the template already holds."""
    consts = T.const_patches(cap, lib)
    assert len(consts) == 16 and all(c.captured for c in consts)
    assert sum(c.visible for c in consts) == 11
    hidden = [(c.template, c.offset) for c in consts if not c.visible]
    assert len(hidden) == 5 and all(c.value == 0 for c in consts if not c.visible)


def test_destination_registers_are_in_no_library_run(cap, lib):
    """E004: the library holds no byte range with USE_EOT's destination registers r1-r3
    (1 << 21 ... 3 << 21): with the immediates as don't-care, no two consecutive loads of
    the template are anywhere in it, though a single load is."""
    found = T.dest_register_search(cap, lib)
    assert {k: len(v) for k, v in found.items()} == {
        (8, 1): 2, (16, 1): 9, (24, 1): 2, (32, 1): 0,
        (8, 2): 0, (16, 2): 0, (24, 2): 0, (8, 3): 0, (16, 3): 0, (8, 4): 0}


def test_template_records_agree_with_tq_meta(cap):
    seen = T.meta(cap)
    # E004: every address is a multiple of 16 (PDS_PRIM_1SRC: 64), none crosses a page
    assert seen["PDS_PRIM_1SRC"].align == 64
    assert all(s.align >= 16 and s.straddles == 0 for s in seen.values())
    for m in facts.TQ_META:
        s = seen[facts.TQ_NAMES[m.id]]
        assert s.heaps == {m.heap} and s.sizes == {m.size}
        assert s.align % m.align == 0 and s.straddles == 0
        if m.heap == facts.PDSPIXEL:
            assert s.pds_data == {m.pds_data}
        else:
            assert s.trc == {(m.temps + 3) >> 2}


def test_report(cap, lib):
    text = T.report(CAPTURE, lib)
    assert "0 mismatches" in text and "ABSENT" not in text


def test_commands_report_on_the_capture(cap):
    text = T.commands_report(cap)
    assert "67 commands in 14 runs" in text
    assert "fence == n in 67/67" in text
