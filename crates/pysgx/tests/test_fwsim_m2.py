# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""fwsim M2, first package (P3, the kick builder): one kept render job as our kernel built it
(tools/fwsim/kick.py, held to the kept words by tools/fwsim/test_kick.py), placed at its device
addresses and kicked through the kernel CCB into the stock microkernel under the hardware model.
Skipped without the private firmware, the public data, the linux fork's commit or a C compiler.

The checks assert only what landed records state: the kick's slot 0 entry and its event words
(E146, E746, E768, E819), and that a command with the data cache-control bit makes the firmware
write CR_CACHE_CTRL (edm_dataflow.md, E013). Where the run stops is a refusal (R1): the register
it read and the question that blocks it, nothing of the trace beyond counts and registers."""
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
CACHE_CTRL, EVENT_STATUS = 0x0804 // 4, 0x012C // 4
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


def test_the_kick_stops_on_its_cache_ctrl_read_before_the_write(kicked):
    """The kernel's cache control on a render kick carries INVAL_DATA (bit 3); in this run the
    firmware reads CR_CACHE_CTRL after the kick, before it writes it (E013 places the write).
    The hardware reads 0x0000ffff after a reset and 0x1000ffff from a change before bit 26
    until a reset (E1120); whether a read after the kick and before the firmware's write sees
    the change is a unit's reading no kept job gives (R1, R2), so the run stops there, refused,
    before CR_EVENT_STATUS (whose idle word E1115 gives outside a job only). Before E1120 the
    boot's write answered it: a read-back the hardware does not give after a kick."""
    r, evs, stop = kicked
    assert not any(e["ev"] == "wr" and not e["host"] and int(e["reg"], 16) == CACHE_CTRL * 4 for e in evs)
    assert "0x0804" in str(stop) and "E1120" in str(stop)
    assert r.s.hw_refused() == {CACHE_CTRL: 1}


def test_the_kick_scenario_writes_its_run_directory_without_instruction_text(tmp_path, built):
    private = tmp_path / "private"
    (private / "firmware" / "fwsim").mkdir(parents=True)
    out = private / "firmware" / "fwsim" / "m2-test"
    log = fwsim.render_kick("r9-c-off", 1, out, DATA, FW, private)
    assert sorted(p.name for p in out.iterdir()) == ["facts.txt", "output.txt", "run.toml", "trace.jsonl.gz"]
    assert log[:5] == ["boot: ok", "arm: ok", "ticks x1: ok", "map: ok", "render kick: stopped"]
    text = (out / "facts.txt").read_text()
    assert "refused reads: 0x0804 x1" in text and "job render/closing-r9-k1 c-off" in text
    mnemonics = {"mov", "ldr", "str", "stad", "ldad", "emitpds", "nop", "wdf", "movs", "halt", "lapc"}
    for src in (text, gzip.open(out / "trace.jsonl.gz", "rt").read()):
        words = set(src.replace('"', " ").replace(",", " ").split())
        assert not words & mnemonics, words & mnemonics
