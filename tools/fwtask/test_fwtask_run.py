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


def stopped_run(tmp_path, monkeypatch, advancing):
    """cmd_run with a job that never reports done; alive() after the stop says `advancing`."""
    import json as _json
    monkeypatch.setattr(FR, "dmesg_len", lambda: 0)
    monkeypatch.setattr(FR, "dmesg_new", lambda n0: [])
    monkeypatch.setattr(FR, "kreg_all", lambda: {o: 0 for o in FR.REGS_WRITABLE})
    monkeypatch.setattr(FR, "hang_dump", lambda outdir, tag: None)
    class ClosingRes(FakeRes):
        def close(self):
            pass
    monkeypatch.setattr(FR, "Res", lambda: ClosingRes(fill=()))
    monkeypatch.setattr(FR, "one_cmd", lambda *a, **k: {"done": False})
    ticks = [2467, 2467, 2467] if not advancing else [10, 20, 30]
    monkeypatch.setattr(FR, "alive", lambda: {"ticks": ticks, "serv_event": [1, 1, 1],
                                              "advancing": advancing, "serv_moves": False})
    lines = []
    monkeypatch.setattr(FR, "emit", lambda obj: lines.append(_json.dumps(obj)))
    rc = FR.cmd_run({"name": "o1", "outdir": str(tmp_path), "jobs": [{"n": 1}]})
    return rc, lines[0], _json.loads(lines[0])


def test_a_stop_reads_the_tick_and_names_a_stopped_firmware_hung(tmp_path, monkeypatch):
    # r36-n3: no done, the EDM tick frozen; the kit classes a job by the word `hung` in its output
    rc, text, out = stopped_run(tmp_path, monkeypatch, advancing=False)
    assert rc == 1 and out["alive_at_stop"]["ticks"] == [2467, 2467, 2467]
    assert "firmware hung" in out["stop"] and "no done" in out["stop"]


def test_a_stop_with_the_tick_advancing_is_not_called_hung(tmp_path, monkeypatch):
    rc, text, out = stopped_run(tmp_path, monkeypatch, advancing=True)
    assert rc == 1 and out["alive_at_stop"]["advancing"] is True
    assert "hung" not in text


def test_a_stop_whose_tick_cannot_be_read_says_so(tmp_path, monkeypatch):
    rc, text, out = stopped_run(tmp_path, monkeypatch, advancing=False)
    def dead():
        raise OSError("debugfs gone")
    monkeypatch.setattr(FR, "alive", dead)
    lines = []
    monkeypatch.setattr(FR, "emit", lambda obj: lines.append(obj))
    assert FR.cmd_run({"name": "o1", "outdir": str(tmp_path), "jobs": [{"n": 1}]}) == 1
    assert "debugfs gone" in lines[0]["alive_at_stop"]["error"]


# ---- the kick (round 39, N3d row K) -------------------------------------------------------------
class KickRes(FakeRes):
    """A results page whose task runs only at a kick: the command write leaves state 0 (the ticks
    tail-call), the miscinfo read runs it. Every access is logged in `calls`."""

    def __init__(self, calls):
        super().__init__(fill=(1,))
        self.calls = calls
        self.kicked = False

    def r(self, dword, n=1):
        self.calls.append(("r", dword, n))
        return super().r(dword, n)

    def w(self, dword, vals):
        self.calls.append(("w", dword))
        vals = [vals] if isinstance(vals, int) else vals
        self.page[dword:dword + len(vals)] = vals          # no task run at the write


def kick_setup(monkeypatch, calls, res, reply="ok"):
    tick = iter(range(100, 10000, 7))

    def regs():
        calls.append(("regs",))
        return {}, {12: next(tick)}

    def rd(name):
        calls.append(("rd", name))
        assert name == "miscinfo"
        if reply == "error":
            raise OSError(110, "Connection timed out")
        base = FR.RESULTS + 4
        res.page[base:base + 4] = [0x5a5a3301, 1, 0x5a5a3303, 0]
        res.page[FR.CMD], res.page[FR.STATE] = 0, 2
        return "sgx misc info: ok\n"
    monkeypatch.setattr(FR, "regs", regs)
    monkeypatch.setattr(FR, "rd", rd)
    monkeypatch.setattr(FR.time, "sleep", lambda s: None)


def test_a_kick_job_writes_the_command_reads_k0_then_kicks_then_polls(monkeypatch):
    """N3d K: fill, the command write, K0 (HostCtl dword 12, cmd and the job's slot), the one
    miscinfo read, then the poll for state 2; the ticks are counted from the command write and
    from the kick."""
    calls = []
    res = KickRes(calls)
    kick_setup(monkeypatch, calls, res)
    out = FR.one_cmd(res, 1, {}, 1, {}, ticks=True, kick="miscinfo")
    i_cmd = calls.index(("w", FR.CMD))
    i_kick = calls.index(("rd", "miscinfo"))
    k0 = calls[i_cmd + 1:i_kick]
    assert ("regs",) in k0 and ("r", FR.CMD, 1) in k0 and ("r", FR.RESULTS + 4, 4) in k0, k0
    assert calls.index(("w", FR.RESULTS + 4)) < i_cmd                  # the fill first
    assert ("r", FR.STATE, 1) in calls[i_kick:]                         # the poll after the kick
    assert not [c for c in calls[:i_kick] if c == ("r", FR.STATE, 1)]   # no poll before it
    assert out["done"] and out["k0"]["cmd"] == 1 and out["k0"]["slot"] == [FR.INITFILL] * 4
    assert out["k0"]["tick"] == 107 and out["ticks"] == (out["k0"]["tick"] - 100) + \
        out["ticks_from_kick"]
    assert out["kick"] == {"kind": "miscinfo", "reply": out["kick"]["reply"]}
    assert out["kick"]["reply"]["text"].startswith("sgx misc info")


def test_a_kick_whose_reply_fails_is_kept_and_the_poll_goes_on(monkeypatch):
    calls = []
    res = KickRes(calls)
    kick_setup(monkeypatch, calls, res, reply="error")
    out = FR.one_cmd(res, 1, {}, 1, {}, timeout_ms=5, ticks=True, kick="miscinfo")
    assert not out["done"] and "error" in out["kick"]["reply"]
    assert "Connection timed out" in out["kick"]["reply"]["error"]


def test_a_job_without_a_kick_reads_no_miscinfo(monkeypatch):
    calls = []
    res = KickRes(calls)
    kick_setup(monkeypatch, calls, res)
    out = FR.one_cmd(res, 1, {}, 1, {}, timeout_ms=5, ticks=True)
    assert ("rd", "miscinfo") not in calls and "k0" not in out and "kick" not in out


def test_the_runner_refuses_another_kick(monkeypatch):
    import pytest
    with pytest.raises(ValueError):
        FR.one_cmd(FakeRes(), 1, {}, 1, {}, kick="fill")


def test_cmd_run_passes_the_job_s_kick(monkeypatch):
    seen = {}
    monkeypatch.setattr(FR, "dmesg_len", lambda: 0)
    monkeypatch.setattr(FR, "dmesg_new", lambda n0: [])
    monkeypatch.setattr(FR, "kreg_all", lambda: {o: 0 for o in FR.REGS_WRITABLE})
    monkeypatch.setattr(FR, "alive", lambda: {"advancing": True})
    monkeypatch.setattr(FR, "health", lambda: {"ok": True})
    monkeypatch.setattr(FR, "emit", lambda obj: None)

    class ClosingRes(FakeRes):
        def close(self):
            pass
    monkeypatch.setattr(FR, "Res", lambda: ClosingRes())

    def one(*a, **k):
        seen.update(k)
        return {"done": True}
    monkeypatch.setattr(FR, "one_cmd", one)
    FR.cmd_run({"name": "o1", "outdir": "/nonexistent", "jobs": [{"n": 1, "kick": "miscinfo"}]})
    assert seen.get("kick") == "miscinfo"
