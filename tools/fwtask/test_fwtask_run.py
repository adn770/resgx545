"""The laptop runner's kernel-log helpers: a marker in /dev/kmsg, not a line count (a full ring
buffer keeps its line count constant), and the one informational reset line that is not bad."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fwtask_run as FR  # noqa: E402


class FakeRing:
    """A kernel ring buffer of fixed capacity: writing a line drops the oldest one."""

    def __init__(self, cap, lines, tmp_path):
        self.cap, self.lines = cap, list(lines)
        self.kmsg = tmp_path / "kmsg"
        self.kmsg.write_text("")

    def dmesg(self, cmd, check=True):
        assert cmd == "dmesg"
        if True:                                    # the marker the code wrote lands in the ring
            for ln in self.kmsg.read_text().splitlines():
                self.push(f"[ 1.0] {ln}")
            self.kmsg.write_text("")
        return "\n".join(self.lines) + "\n"

    def push(self, ln):
        self.lines = (self.lines + [ln])[-self.cap:]


def setup(tmp_path, monkeypatch, cap=5):
    ring = FakeRing(cap, [f"[ 0.{i}] old {i}" for i in range(cap)], tmp_path)
    monkeypatch.setattr(FR, "sh", ring.dmesg)
    monkeypatch.setattr(FR, "KMSG", str(ring.kmsg))
    return ring


def test_a_wrapped_ring_still_returns_the_new_lines(tmp_path, monkeypatch):
    ring = setup(tmp_path, monkeypatch)
    n0 = FR.dmesg_len()
    ring.dmesg("dmesg")                             # reading lets the marker in
    ring.push("[ 2.0] new one")
    ring.push("[ 2.1] new two")
    assert len(ring.lines) == 5                     # the line count did not change
    assert FR.dmesg_new(n0) == ["[ 2.0] new one", "[ 2.1] new two"]


def test_the_last_marker_counts(tmp_path, monkeypatch):
    ring = setup(tmp_path, monkeypatch, cap=20)
    n0 = FR.dmesg_len()
    ring.dmesg("dmesg")
    ring.push("[ 2.0] after")
    assert FR.dmesg_new(n0) == ["[ 2.0] after"]


def test_a_missing_marker_returns_the_whole_buffer_and_says_so(tmp_path, monkeypatch):
    ring = setup(tmp_path, monkeypatch)
    n0 = FR.dmesg_len()
    ring.dmesg("dmesg")
    for i in range(5):                              # the marker itself wraps out
        ring.push(f"[ 3.{i}] flood {i}")
    got = FR.dmesg_new(n0)
    assert got[0].startswith("(kernel log marker not found")
    assert got[1:] == ring.lines


def test_the_reset_info_line_is_not_bad_but_a_hang_is():
    info = "[  9.1] gma500 0000:00:02.0: [drm] SGX reset: after the fault clear BIF_FAULT 0x0 BIF_INT_STAT 0x0"
    old = "[  9.0] gma500 0000:00:02.0: [drm] SGX reset: BIF_FAULT 0x0 BIF_INT_STAT 0x0"
    assert not FR.is_bad_log(info)
    assert not FR.is_bad_log(old)
    assert FR.is_bad_log("[ 9.2] gma500: [drm] SGX hung, recovering")
    assert FR.is_bad_log("[ 9.3] SGX reset: after the fault clear BIF_FAULT 0x0 BIF_INT_STAT 0x0 extra: page fault")
    assert FR.is_bad_log("[ 9.4] some fault happened")


def test_every_result_is_flagged_when_the_marker_was_missing(tmp_path, monkeypatch, capsys):
    ring = setup(tmp_path, monkeypatch)
    n0 = FR.dmesg_len()
    ring.dmesg("dmesg")
    for i in range(5):
        ring.push(f"[ 3.{i}] flood {i}")
    FR.dmesg_new(n0)
    FR.emit({"ok": True})
    assert '"log_whole_buffer": true' in capsys.readouterr().out
    n1 = FR.dmesg_len()                             # a new marker clears the flag
    ring.dmesg("dmesg")
    FR.dmesg_new(n1)
    FR.emit({"ok": True})
    assert "log_whole_buffer" not in capsys.readouterr().out


class FakeRes:
    """The results page with a task behind it: writing cmd n runs it (state = done, result slots
    filled with n << 8 | slot << 4 | dword)."""

    def __init__(self, fill=(1, 2, 3, 4)):
        self.page = [0] * 1024
        self.fill = fill

    def r(self, dword, n=1):
        return self.page[dword:dword + n]

    def w(self, dword, vals):
        vals = [vals] if isinstance(vals, int) else vals
        self.page[dword:dword + len(vals)] = vals
        if dword == FR.CMD and vals[0]:
            for s in self.fill:
                base = FR.RESULTS + 4 * s
                self.page[base:base + 4] = [vals[0] << 8 | s << 4 | k for k in range(4)]
            self.page[FR.STATE] = 2


def test_a_job_reads_the_extra_result_slots_it_names_after_filling_them():
    """emitsa (round 33): cmd 1 leaves its results in slots 1 to 4; the job names 2 to 4 beside
    its own slot, and each is initfilled first so a slot the task never wrote reads 0xdeadc0de."""
    res = FakeRes(fill=(1, 2, 4))
    out = FR.one_cmd(res, 1, {}, 7, {}, extra=(2, 3, 4))
    assert out["done"] and out["slot"] == [0x110, 0x111, 0x112, 0x113]
    assert out["slots"] == {"2": [0x120, 0x121, 0x122, 0x123], "3": [FR.INITFILL] * 4,
                            "4": [0x140, 0x141, 0x142, 0x143]}
    out = FR.one_cmd(FakeRes(), 1, {}, 8, {})
    assert "slots" not in out


def test_the_gate_runs_the_health_tool_the_environment_names(monkeypatch):
    # the kit passes its session's pinned health tool; the runner must not fall back to its own
    calls = []
    monkeypatch.setenv("FWTASK_HEALTH_TOOL", "/home/u/sgxfive-test-t30")
    monkeypatch.setattr(FR, "sh", lambda cmd, check=True: calls.append(cmd) or "")
    FR.gate()
    assert calls and all(c.startswith("/home/u/sgxfive-test-t30 ") for c in calls), calls


def test_every_health_tool_call_goes_through_the_one_name():
    src = (pathlib.Path(FR.__file__)).read_text()
    assert src.count("/home/jtorra/sgxfive-test") == 1, "a call names the tool past health_tool()"
