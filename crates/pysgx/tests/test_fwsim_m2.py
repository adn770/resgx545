# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""fwsim M2, first package (P3, the kick builder): one kept render job as our kernel built it
(tools/fwsim/kick.py, held to the kept words by tools/fwsim/test_kick.py), placed at its device
addresses and kicked through the kernel CCB into the stock microkernel under the hardware model.
Skipped without the private firmware, the public data, the linux fork's commit or a C compiler.

The checks assert only what landed records state: the kick's slot 0 entry and its event words
(E146, E746, E768, E819), and that a command with the data cache-control bit makes the firmware
write CR_CACHE_CTRL (edm_dataflow.md, E013), the read before it answered by E1122. Where the run
stops is a refusal (R1): the register it read and the question that blocks it, nothing of the
trace beyond counts and registers."""
import gzip
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent.parent / "tools" / "fwsim"))
import fwsim  # noqa: E402
import kept  # noqa: E402
import kick  # noqa: E402
import test_sgx_boot as tb  # noqa: E402

DATA, FW = kept.data_dir(), fwsim.find_fw()
pytestmark = [
    *tb.pytestmark,
    pytest.mark.skipif(FW is None, reason="no sgx545_ukernel.fw in the private data repository"),
    pytest.mark.skipif(DATA is None, reason="no resgx545-data"),
]

SLOT0 = 6                                       # PDS #13 slot 0's start index (E146)
K = 2                                           # the count byte after the arm (E768)
CACHE_CTRL, EVENT_STATUS, EVENT_HOST_CLEAR = 0x0804 // 4, 0x012C // 4, 0x0134 // 4
SESSION = kick.SESSIONS["r9-c-off"]


@pytest.fixture(scope="module")
def built():
    try:
        return kick.build(SESSION, DATA)
    except kick.Unavailable as e:
        pytest.skip(f"SKIPPED, NOT PASSED: {e}")


@pytest.fixture(scope="module")
def kicked(built):
    r = fwsim.Run(FW, DATA, trace="memory")
    r.boot()
    r.arm()
    r.tick()
    r.map_render(built)
    n = len(r.events())
    with pytest.raises(Exception) as stop:
        r.kick_render()
    return r, r.events()[n:], stop.value


def test_the_placed_context_reads_back_as_built(built):
    r = fwsim.Run(FW, DATA)
    r.map_render(built)
    a, j = built["addr"], built["job"]
    for name, space in (("ctx", "ctx"), ("rtds", "rtds"), ("pbdesc", "pb"), ("rd", "rd"),
                        ("access", "kw"), ("ccb", "ta"), ("ccb_ctl", "ctl")):
        assert [r.s.load32(a[name] + 4 * i) for i in sorted(j[space])] == [j[space][i] for i in sorted(j[space])]


def test_the_render_kick_is_one_slot_0_entry_with_the_count_and_the_kick_bit(kicked):
    """The TA command's kick, like any kernel CCB kick, is one slot 0 entry with pa0 0 and
    pa1 = (K << 24) | 0x100 (E746, E768, E819)."""
    _, evs, _ = kicked
    assert [(e["pc"], e["pa"][:2]) for e in fwsim.entries(evs)] == [
        (SLOT0, ["0x00000000", f"0x{K << 24 | 0x100:08x}"])]


def test_the_kick_reads_cache_ctrl_writes_bit_28_then_stops_on_event_status(kicked):
    """The kernel's cache control on a render kick carries INVAL_DATA (bit 3); the firmware reads
    CR_CACHE_CTRL after the kick and writes it `| 0x10000000` (E013). The hardware reads 0x0000ffff
    after a reset and 0x1000ffff from one change to the reset (E1120), a change that follows the
    kick pass's BIF write (E1122, E1123): the read before the run's write answers the reset word,
    so the write is 0x1000ffff, the word the hardware then reads. What CR_EVENT_STATUS reads
    after it while the invalidation runs is a unit's reading no kept job gives (R1, R2; Q111): the
    run stops there, refused; E1115's idle word answers it only until a kick is served."""
    r, evs, stop = kicked
    writes = [int(e["value"], 16) for e in evs
              if e["ev"] == "wr" and not e["host"] and int(e["reg"], 16) == CACHE_CTRL * 4]
    assert writes == [0x1000FFFF]
    assert r.s.hw_answered().get("rule:E1122", 0) >= 1
    assert "0x012c" in str(stop) and "E1115" in str(stop)
    assert r.s.hw_refused() == {EVENT_STATUS: 1}


def test_the_kick_scenario_writes_its_run_directory_without_instruction_text(tmp_path, built):
    private = tmp_path / "private"
    (private / "firmware" / "fwsim").mkdir(parents=True)
    out = private / "firmware" / "fwsim" / "m2-test"
    log = fwsim.render_kick("r9-c-off", 1, out, DATA, FW, private)
    assert sorted(p.name for p in out.iterdir()) == ["facts.txt", "output.txt", "run.toml", "trace.jsonl.gz"]
    assert log[:5] == ["boot: ok", "arm: ok", "ticks x1: ok", "map: ok", "render kick: stopped"]
    text = (out / "facts.txt").read_text()
    assert "refused reads: 0x012c x1" in text and "job render/closing-r9-k1 c-off" in text
    mnemonics = {"mov", "ldr", "str", "stad", "ldad", "emitpds", "nop", "wdf", "movs", "halt", "lapc"}
    for src in (text, gzip.open(out / "trace.jsonl.gz", "rt").read()):
        words = set(src.replace('"', " ").replace(",", " ").split())
        assert not words & mnemonics, words & mnemonics


@pytest.fixture(scope="module")
def replayed(built):
    r = fwsim.Run(FW, DATA, trace="memory", replay=fwsim.load_replay())
    r.boot()
    r.arm()
    r.tick()
    r.map_render(built)
    n = len(r.events())
    with pytest.raises(Exception) as stop:
        r.kick_render()
    return r, r.events()[n:], stop.value


def test_without_replay_the_strict_rule_is_the_default(kicked):
    """Replay is explicit per run: the run above (no replay) stops on the 0x012c read."""
    r, _, _ = kicked
    assert "replay" not in r.s.hw_answered() and r.s.hw_replay_log() == []


def test_under_replay_the_kick_pass_spins_on_event_status_then_reads_bit_26_and_clears_it(replayed):
    """E1130 (fwsim, replay of E1115, E1120, E1123): after its CR_CACHE_CTRL write the kick pass
    reads CR_EVENT_STATUS with its state unchanged between reads while the word is 0x20000000 (a
    spin, so how long the hardware holds the word changes nothing), reads 0x24000000 when the kept
    order moves on, and writes bit 26 to CR_EVENT_HOST_CLEAR; no 0x012c read is refused."""
    r, evs, stop = replayed
    reads = [int(e["value"], 16) for e in evs if e["ev"] == "rd" and int(e["reg"], 16) == EVENT_STATUS * 4]
    assert reads[0] == 0x20000000 and reads[-1] == 0x24000000 and set(reads) == {0x20000000, 0x24000000}
    assert r.s.hw_replay_log() == [
        "0x012c: a spin on word 0 moved to word 1 0x24000000 (E1115, E1120, E1123)"]
    writes = [(int(e["reg"], 16), int(e["value"], 16)) for e in evs if e["ev"] == "wr" and not e["host"]]
    assert (EVENT_HOST_CLEAR * 4, 0x04000000) in writes
    assert EVENT_STATUS not in r.s.hw_refused() and "0x012c" not in str(stop)


def replay_run(built, emit_tim):
    r = fwsim.Run(FW, DATA, trace="memory", replay=fwsim.load_replay(), emit_tim=emit_tim)
    r.boot()
    r.arm()
    r.tick()
    r.map_render(built)
    n = len(r.events())
    with pytest.raises(Exception) as stop:
        r.kick_render()
    return r, r.events()[n:], stop.value


def test_without_a_running_count_the_next_stop_is_the_counter_of_a_program_the_pass_emits(built):
    """E1130: the pass then emits a PDS program that reads the counter tim, which no run input
    gives for a program a task emits (R1, R3): the run stops there, not on a register read."""
    r, evs, stop = replay_run(built, None)
    assert "tim is not known" in str(stop)
    assert r.s.hw_refused() == {}


def test_the_seeded_count_is_a_running_count_by_e1133():
    """E1133: through a kick pass the timer keeps bit 24 alone in 31:24 and bits 23:0 at most
    400000 (no write or stop), at a phase no row gives: the seed is one such count, marked
    [time], and a count outside the rule is refused."""
    e = fwsim.load_seeds()["events"]
    assert e["emit_tim"] >> 24 == 1 and e["emit_tim"] & 0xFFFFFF <= 400000
    for bad in (0x01061A81, 0x00020000, 0x03000000):
        with pytest.raises(ValueError):
            fwsim.Run(FW, DATA, emit_tim=bad)


def test_with_a_running_count_the_pass_gets_past_the_counter(replayed):
    """With E1133's running count (seeds.toml [events] emit_tim) the emitted program's tim read
    is answered: the run no longer stops on it. PDS #14 starts one task, the second entry of the
    kick (E146's second group), and the run stops on a memory fault at 0x0002007c, an address no
    placed page holds; no register read is refused."""
    r, evs, stop = replayed
    assert "tim is not known" not in str(stop)
    assert [e["addr"] for e in evs if e["ev"] == "pds"] == ["0x30010000", "0x30011000"]
    assert len(fwsim.entries(evs)) == 2
    assert "fault at 0x0002007c" in str(stop).lower() and r.s.hw_refused() == {}


@pytest.mark.parametrize("count", [0x01000000, 0x01061A80])
def test_the_next_stop_does_not_depend_on_the_count(built, count):
    """E1133 leaves the phase open: the run reaches the same stop, with the same firmware
    register writes, at both ends of the running counts."""
    r, evs, stop = replay_run(built, count)
    _, evs0, stop0 = replay_run(built, fwsim.load_seeds()["events"]["emit_tim"])
    w = lambda es: [(e["reg"], e["value"]) for e in es if e["ev"] == "wr" and not e["host"]]
    assert str(stop) == str(stop0) and w(evs) == w(evs0)
