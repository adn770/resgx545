# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""fwsim M1 (the firmware-in-sim track): the stock microkernel boots and ticks in the simulator
under the hardware model (tools/fwsim/fwsim.py: every register read a run write, a cited seed, a
landed rule or a reset value the kept snapshots agree on, else the run stops), and what it does
is held against the kept boot and tick data of resgx545-data and the records that read them.
C1 (the boot chain) and C6 (GETMISCINFO, POWER IDLE replies) are test_sgx_boot.py and
test_sgx_ccb.py. Skipped without the private firmware or the public data.

The checks assert only what landed records state (E146's slot 0 start index, the event words of
E532 and E746, the after-boot snapshot of platform/boot-registers); nothing of the run's own
trace is asserted or printed beyond counts, registers and values."""
import json
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent.parent / "tools" / "fwsim"))
import fwsim  # noqa: E402
import kept  # noqa: E402
import test_sgx_boot as tb  # noqa: E402

DATA, FW = kept.data_dir(), fwsim.find_fw()
pytestmark = [
    *tb.pytestmark,
    pytest.mark.skipif(FW is None, reason="no sgx545_ukernel.fw in the private data repository"),
    pytest.mark.skipif(DATA is None, reason="no resgx545-data (platform/boot-registers, edm-tick)"),
]

SLOT0 = 6                                       # PDS #13 slot 0's start index (E146)
TICK_WORDS = [2, 0x02000000, 0x01061A70]        # pa0-pa2 of a tick after the arm (E532, E746)
TIMER_WORD = 0x01061A80                         # init_done's EVENT_TIMER: 400000 | 1 << 24 (E818)
CCB_READ_OFFSET = 1
TICKS, POWER_STATUS, ASSERT_DWORD = 12, 1, 14


def booted(trace="memory", arm=True) -> fwsim.Run:
    r = fwsim.Run(FW, DATA, trace=trace)
    r.boot()
    if arm:
        r.arm()
    return r


def regs(snapshot: dict) -> dict[int, int]:
    return snapshot["reg"]


def fw_writes(log: list) -> dict[int, int]:
    """The last value the firmware wrote to each register (index -> value), in a log slice."""
    return {e[2]: e[3] for e in log if e[0] == "write" and not e[1]}


def test_c2_the_boots_register_writes_equal_the_after_boot_snapshot():
    """C2: every register the firmware wrote in the boot reads the same in the kept after-boot
    snapshot (platform/boot-registers 'booted', E008), the reset values coming from the
    snapshots (E006, E008, E009) and the host's writes from the firmware file's part2 script.
    EVENT_TIMER runs on the hardware: there the run bit and a count below the written reload
    are compared [time]. The boot reads no register the model refuses."""
    r = booted(trace=None, arm=False)
    snap = regs(kept.boot_registers(DATA)["booted"])
    writes = fw_writes(r.s.log())
    assert writes and all(i * 4 in snap for i in writes)
    for i, v in writes.items():
        if i == fwsim.EVENT_TIMER:
            assert v == TIMER_WORD
            assert snap[i * 4] >> 24 == v >> 24 and snap[i * 4] & 0xFFFFFF < v & 0xFFFFFF
        else:
            assert snap[i * 4] == v, f"0x{i * 4:04x}"
    # the host's writes that the firmware left read as written, as E006 measured
    for off, v in r.boot_data.scripts["part2"]:
        if off // 4 not in writes and off in snap:
            assert snap[off] == v, f"0x{off:04x}"
    assert r.s.hw_refused() == {}


@pytest.fixture(scope="module")
def ticked():
    """The armed firmware, then 1000 tick passes, each pass's HostCtl and new firmware
    register writes kept."""
    r = booted(trace=None)
    rows = []
    for _ in range(1000):
        before, n = r.host_ctl(), len(r.s.log())
        r.tick()
        rows.append((before, r.host_ctl(), fw_writes(r.s.log()[n:]), r.s.reg(fwsim.EVENT_TIMER)))
    return r, rows


def test_c3_each_tick_pass_advances_hostctl_dword_12_and_nothing_else(ticked):
    """C3: per tick pass HostCtl dword 12 + 1 and no other HostCtl word (E009, hw_spec 12.2), for
    1000 passes; EVENT_TIMER stays at the tick handler's word 0x01061a80 (E818, E155) and no pass
    writes a register, so nothing the idle hardware moves (E009's four values) is written."""
    r, rows = ticked
    for k, (before, after, writes, timer) in enumerate(rows):
        assert after[TICKS] == before[TICKS] + 1, k
        assert [a for i, a in enumerate(after) if i != TICKS] == [b for i, b in enumerate(before) if i != TICKS], k
        assert writes == {}, k
        assert timer == TIMER_WORD, k
    assert r.s.hw_refused() == {}


def test_c4_a_tick_reaches_slot_0_with_the_measured_event_words():
    """C4: the tick enters slot 0 (index 6, E146) with pa0 = 2, pa1 = K << 24, K = 2 after the
    arm's two GETMISCINFO, and pa2 = the timer word 0x01061a70 (E532 2 of 2, E746, E768); with
    no arm, K = 0."""
    for arm, k in ((True, 2), (False, 0)):
        r = booted(arm=arm)
        n = len(r.events())
        r.tick()
        ins = fwsim.entries(r.events()[n:])
        assert [e["pc"] for e in ins][:1] == [SLOT0]
        assert ins[0]["pa"][:3] == [f"0x{w:08x}" for w in (2, k << 24, 0x01061A70)]
    assert TICK_WORDS == [2, 2 << 24, 0x01061A70]


@pytest.mark.parametrize("p", [[False, False, True, True], [False, True, False, False],
                               [False, False, True, False]])
def test_c5_a_closed_tick_pass_leaves_the_measured_next_entry(p):
    """C5: a closed tick pass leaves the CCB read offset at the write offset, HostCtl dword 14 0,
    and at the next entry pclink 0x98 and p0 1 whatever the entry held, with p1 to p3 as they
    were (row 1 of edm_pass.rs: E791, E792; E809: p1-p3 survive the closed task's pass, 8 of 8;
    the flags are E809's 0011, 0100 and 1010 with p0 cleared)."""
    r = booted(trace=None)
    r.s.seed_carry(pclink=0x1234, p=p, r20=0x11, r21=0x22, i0=0x33, i1=0x44)
    before = r.host_ctl()
    r.tick()
    c = r.s.carry()
    assert c["pclink"] == 0x98
    assert c["p"] == [True, *p[1:]]
    assert (c["r20"], c["r21"], c["i0"], c["i1"]) == (0x11, 0x22, 0x33, 0x44)
    rd, wr = r.ccb_offsets()
    assert rd == wr
    assert r.host_ctl()[ASSERT_DWORD] == 0 and before[ASSERT_DWORD] == 0


def test_c7_each_kick_is_one_slot_0_entry_with_the_count_and_the_kick_bit():
    """C7: after the arm (K = 2), each kick of a GETMISCINFO is one slot 0 entry with pa0 0 and
    pa1 = (K << 24) | 0x100, K = 2, 3, 4 in kick order, and the tick after it carries K + 1
    (E746 3 of 3, E768, E819, E834)."""
    r = booted()
    for k in (2, 3, 4):
        n = len(r.events())
        r.get_misc_info()
        ins = fwsim.entries(r.events()[n:])
        assert [(e["pc"], e["pa"][:2]) for e in ins] == [(SLOT0, ["0x00000000", f"0x{k << 24 | 0x100:08x}"])]
        n = len(r.events())
        r.tick()
        assert fwsim.entries(r.events()[n:])[0]["pa"][1] == f"0x{(k + 1) << 24:08x}"
    assert r.s.hw_refused() == {}


def test_c7_a_kick_without_the_bump_is_no_entry_and_what_follows_is_refused():
    """C7: a kick with the kicker word unchanged raises no event (E819 Q3, 3 of 3; E834); what
    follows it is open (Q290), so the next event is refused."""
    r = booted()
    n = len(r.events())
    r.submit("GETMISCINFO", fwsim.ccb.get_misc_info(r.lay.addr[fwsim.facts.MISC]), bump=False)
    assert fwsim.entries(r.events()[n:]) == []
    with pytest.raises(Exception, match="Q290"):
        r.tick()


def test_c8_the_served_event_count_answers_ticks_and_refuses_after_a_kick(ticked):
    """C8: CR_USE0_SERV_EVENT (bit 16 set, one count a tick: E009) is answered by the seeded rule
    while only ticks were served; after a kick the count is not measured and a read of it stops
    the run naming the register and E009 (POWER IDLE, whose reply test_sgx_ccb.py checks with an
    uncited seed, is such a read here)."""
    r, _ = ticked
    assert r.s.hw_refused() == {}
    p = booted(trace=None)
    with pytest.raises(Exception, match="0x0b14"):
        p.power_idle()
    assert p.s.hw_refused() == {0x0B14 // 4: 1}


def test_a_traced_run_writes_only_under_the_private_fwsim_directory(tmp_path):
    """T1: the trace and the run directory go only under <private>/firmware/fwsim/; any other
    path is refused before anything is written, by fwsim and by the simulator's sink."""
    private = tmp_path / "private"
    (private / "firmware" / "fwsim").mkdir(parents=True)
    for bad in (tmp_path / "trace.jsonl", private / "trace.jsonl", private / "firmware" / "fwsim",
                private / "firmware" / "fwsim" / ".." / "x" / "trace.jsonl"):
        with pytest.raises(fwsim.Refused):
            fwsim.Run(FW, DATA, trace=bad, private=private)
    s = fwsim.load.pysgx().Sgx()
    with pytest.raises(ValueError):
        s.trace_to(tmp_path / "trace.jsonl", private)
    assert sorted(p.name for p in tmp_path.rglob("*") if p.is_file()) == []


def test_the_idle_scenario_writes_its_run_directory_without_instruction_text(tmp_path):
    """fwsim.py idle: run.toml, trace.jsonl.gz, facts.txt and output.txt in the run directory,
    the plain trace removed; the trace and the facts hold no instruction text (FW-7)."""
    private = tmp_path / "private"
    (private / "firmware" / "fwsim").mkdir(parents=True)
    out = private / "firmware" / "fwsim" / "m1-test"
    log = fwsim.idle(3, out, True, DATA, FW, private)
    assert sorted(p.name for p in out.iterdir()) == ["facts.txt", "output.txt", "run.toml", "trace.jsonl.gz"]
    assert log[:3] == ["boot: ok", "arm: ok", "ticks x3: ok"] and log[3] == "power idle: stopped"
    text = (out / "facts.txt").read_text()
    assert "refused reads: 0x0b14 x1" in text and "alu_specials_in_movs" in text
    import gzip
    evs = [json.loads(line) for line in gzip.open(out / "trace.jsonl.gz", "rt")]
    assert {e["ev"] for e in evs} >= {"insn", "task", "pds", "pass", "event", "refusal", "wr", "ld", "st"}
    mnemonics = {"mov", "ldr", "str", "stad", "ldad", "emitpds", "nop", "wdf", "movs", "halt", "lapc", "emitpds.tasks.taske"}
    for src in (text, gzip.open(out / "trace.jsonl.gz", "rt").read()):
        words = set(src.replace('"', " ").replace(",", " ").split())
        assert not words & mnemonics, words & mnemonics
