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


# ---- round 41 (N3f §3.1): a row of several jobs, a sleep before a job, the gate's order, its
# full outputs and the devcoredump around it -----------------------------------------------------
def run_setup(monkeypatch, calls):
    monkeypatch.setattr(FR, "dmesg_len", lambda: 0)
    monkeypatch.setattr(FR, "dmesg_new", lambda n0: [])
    monkeypatch.setattr(FR, "kreg_all", lambda: {o: 0 for o in FR.REGS_WRITABLE})
    monkeypatch.setattr(FR, "alive", lambda: {"advancing": True})
    monkeypatch.setattr(FR, "health", lambda: {"ok": True})
    tick = iter(range(1000, 100000, 1000))
    monkeypatch.setattr(FR, "regs", lambda: ({}, {12: next(tick)}))
    monkeypatch.setattr(FR.time, "sleep", lambda s: calls.append(("sleep", s)))
    out = []
    monkeypatch.setattr(FR, "emit", lambda obj: out.append(obj))

    class ClosingRes(FakeRes):
        def close(self):
            pass
    monkeypatch.setattr(FR, "Res", lambda: ClosingRes())

    def one(res, n, params, runid, regs, timeout_ms=FR.DONE_MS, **k):
        calls.append(("job", n, runid, k.get("extra"), k.get("kick")))
        return {"done": True}
    monkeypatch.setattr(FR, "one_cmd", one)
    return out


def test_a_job_list_runs_in_order_with_its_sleeps_slots_and_kicks(monkeypatch):
    """Row LC: job 1, then job 2 at once, then job 3 after sleep_ms; each job's slots go to
    one_cmd as its extra result slots; the sleep is recorded with the ticks it spanned (slept)."""
    calls = []
    out = run_setup(monkeypatch, calls)
    jobs = [{"n": 1, "runid": 1}, {"n": 6, "runid": 2, "slots": [40, 41], "kick": "miscinfo"},
            {"n": 6, "runid": 3, "slots": [40], "sleep_ms": 2000}]
    assert FR.cmd_run({"name": "o1", "outdir": "/nonexistent", "jobs": jobs}) == 0
    assert [c for c in calls if c[0] == "job"] == [("job", 1, 1, (), None),
                                                   ("job", 6, 2, [40, 41], "miscinfo"),
                                                   ("job", 6, 3, [40], None)]
    i = calls.index(("job", 6, 3, [40], None))
    assert calls[i - 1] == ("sleep", 2.0)
    assert ("sleep", 2.0) not in calls[:calls.index(("job", 6, 2, [40, 41], "miscinfo"))]
    recs = out[0]["records"]
    assert "slept" not in recs[0] and "slept" not in recs[1]
    assert recs[2]["slept"] == {"ms": 2000, "ticks": 1000}


def test_the_runner_refuses_a_bad_sleep(monkeypatch):
    calls = []
    out = run_setup(monkeypatch, calls)
    for bad in (-1, "2000", True, 1.5):
        out.clear()
        assert FR.cmd_run({"name": "o1", "outdir": "/nonexistent",
                           "jobs": [{"n": 1, "sleep_ms": bad}]}) == 1
        assert "sleep_ms" in out[0]["stop"] and not [c for c in calls if c[0] == "job"]


def gate_setup(tmp_path, monkeypatch, outs=None, pending=(), new=()):
    """A health tool by name and a devcoredump class directory: `pending` dumps before the gate,
    `new` ones appear once the first tool ran. Calls are logged."""
    calls = []
    outs = outs or {"fill": "job: ok\ndiff: 0 of 2048 pixels\nfill: ok, 64x32\n",
                    "tri": "tri: ok\njob: ok\ndiff: 0 of 4096 pixels\ntri 64x64 ok\n"}
    cd = tmp_path / "devcoredump"
    cd.mkdir()

    def dump(name, text):
        (cd / name).mkdir()
        (cd / name / "data").write_text(text)
    for n, t in pending:
        dump(n, t)

    def sh(cmd, check=True):
        calls.append(cmd)
        name = cmd.split()[1]
        if len([c for c in calls if " fill" in c or " tri" in c]) == 1:
            for n, t in new:
                dump(n, t)
        return outs[name]
    monkeypatch.setenv("FWTASK_HEALTH_TOOL", "/home/u/t30")
    monkeypatch.setattr(FR, "sh", sh)
    monkeypatch.setattr(FR, "DEVCD", str(cd))

    def free(path):                     # the kernel drops a dump once its data is written
        calls.append(("free", path))
        import shutil
        shutil.rmtree(pathlib.Path(path).parent)
    monkeypatch.setattr(FR, "devcd_free", free)
    return calls, cd


def test_the_gate_keeps_the_full_outputs_in_its_order(tmp_path, monkeypatch):
    """Default order fill then tri; tri,fill the other way; each tool's whole output (its job:
    line and stderr) in OUTDIR/gate-fill.txt and gate-tri.txt; the JSON summary as before."""
    calls, _ = gate_setup(tmp_path, monkeypatch)
    out = FR.gate(outdir=str(tmp_path / "g"))
    tools = [c for c in calls if isinstance(c, str)]
    assert [c.split()[1] for c in tools] == ["fill", "tri"]
    assert all(c.startswith("/home/u/t30 ") and c.endswith(" 2>&1") for c in tools), tools
    assert out["ok"] and out["order"] == "fill,tri"
    assert out["fill"] == "diff: 0 of 2048 pixels" and out["tri"] == "diff: 0 of 4096 pixels\ntri 64x64 ok"
    assert (tmp_path / "g/gate-fill.txt").read_text().startswith("job: ok\n")
    assert "tri 64x64 ok" in (tmp_path / "g/gate-tri.txt").read_text()
    (tmp_path / "b").mkdir()
    calls, _ = gate_setup(tmp_path / "b", monkeypatch)
    out = FR.gate(order="tri,fill", outdir=str(tmp_path / "b/g"))
    assert [c.split()[1] for c in calls if isinstance(c, str)] == ["tri", "fill"]
    assert out["order"] == "tri,fill" and out["ok"]


def test_a_failed_gate_keeps_both_outputs(tmp_path, monkeypatch):
    calls, _ = gate_setup(tmp_path, monkeypatch, outs={
        "fill": "job: faulted, context lost (Input/output error)\nFAIL fill\n",
        "tri": "job: ok\ndiff: 0 of 4096 pixels\ntri 64x64 ok\n"})
    out = FR.gate(outdir=str(tmp_path / "g"))
    assert not out["ok"] and "FAIL" in out["fill"]
    assert "job: faulted" in (tmp_path / "g/gate-fill.txt").read_text()
    assert (tmp_path / "g/gate-tri.txt").exists()


def test_the_gate_takes_only_the_two_orders(tmp_path, monkeypatch):
    import pytest
    gate_setup(tmp_path, monkeypatch)
    for bad in ("fill", "tri,tri", "fill,tri,fill", ""):
        with pytest.raises(ValueError):
            FR.gate(order=bad)


def test_the_devcoredump_around_the_gate(tmp_path, monkeypatch):
    """Before the tools every pending dump is saved to devcd-pre.txt and freed; after them the
    new one is saved to devcd.txt (and freed); none: a line that says so."""
    calls, cd = gate_setup(tmp_path, monkeypatch, pending=[("devcd3", "old dump\n")],
                           new=[("devcd4", "BIF_INT_STAT: 0x000d0400\nBIF_FAULT: 0x0004300f\n")])
    out = FR.gate(outdir=str(tmp_path / "g"))
    pre = (tmp_path / "g/devcd-pre.txt").read_text()
    post = (tmp_path / "g/devcd.txt").read_text()
    assert "devcd3" in pre and "old dump" in pre and "BIF_FAULT" not in pre
    assert "devcd4" in post and "BIF_FAULT: 0x0004300f" in post and "old dump" not in post
    frees = [c for c in calls if isinstance(c, tuple)]
    first_tool = next(i for i, c in enumerate(calls) if isinstance(c, str))
    assert calls.index(("free", str(cd / "devcd3/data"))) < first_tool
    assert ("free", str(cd / "devcd4/data")) in frees
    assert out["devcd_pre"] == ["devcd3"] and out["devcd"] == ["devcd4"]
    (tmp_path / "n").mkdir()
    calls, cd = gate_setup(tmp_path / "n", monkeypatch)
    out = FR.gate(outdir=str(tmp_path / "n/g"))
    assert (tmp_path / "n/g/devcd-pre.txt").read_text() == "devcd: none pending\n"
    assert (tmp_path / "n/g/devcd.txt").read_text() == "devcd: none pending\n"
    assert out["devcd_pre"] == [] and out["devcd"] == []


def test_a_gate_without_an_outdir_touches_no_devcoredump(tmp_path, monkeypatch):
    calls, cd = gate_setup(tmp_path, monkeypatch, pending=[("devcd3", "old dump\n")])
    out = FR.gate()
    assert out["ok"] and not [c for c in calls if isinstance(c, tuple)]
    assert (cd / "devcd3/data").exists()


def test_cmd_gate_passes_the_order_and_outdir(tmp_path, monkeypatch):
    seen = {}
    monkeypatch.setattr(FR, "gate", lambda **k: seen.update(k) or {"ok": True})
    monkeypatch.setattr(FR, "emit", lambda obj: None)
    FR.cmd_gate({"order": "tri,fill", "outdir": str(tmp_path)})
    assert seen == {"order": "tri,fill", "outdir": str(tmp_path)}
    seen.clear()
    FR.cmd_gate({})
    assert seen == {}


# ---- round 42 (N3g §4, K5): each job's BIF words before its command and after its poll ----------
def bif_setup(monkeypatch, calls, words, ticks_from=100):
    """regs() as the laptop's: BIF_INT_STAT (0x0c04) and BIF_FAULT (0x0c08) from `words` in turn
    (a raised OSError for an Exception item), HostCtl dword 12 counting."""
    seq, tick = iter(words), iter(range(ticks_from, 10000, 7))

    def regs():
        calls.append(("regs",))
        w = next(seq)
        if isinstance(w, Exception):
            raise w
        return {0xc04: w[0], 0xc08: w[1], 0x118: 0x400}, {12: next(tick)}
    monkeypatch.setattr(FR, "regs", regs)
    monkeypatch.setattr(FR.time, "sleep", lambda s: None)


class PollRes(KickRes):
    """KickRes whose task reports done at its first poll (state 2 when the poll reads it)."""

    def r(self, dword, n=1):
        if dword == FR.STATE and self.page[FR.CMD]:
            self.page[FR.STATE] = 2
        return super().r(dword, n)


def test_a_job_keeps_the_bif_words_before_its_command_and_after_its_poll(monkeypatch):
    """K5: one regs() read right before the cmd write (the one ticks takes tk0 from) and one after
    the poll; the record's bif is {pre, post}, each [BIF_INT_STAT, BIF_FAULT]. Nothing written."""
    calls = []
    res = PollRes(calls)
    bif_setup(monkeypatch, calls, [(0, 0), (0xD0400, 0x4300F), (0xD0400, 0x4300F)])
    out = FR.one_cmd(res, 1, {}, 1, {}, ticks=True)
    i_cmd = calls.index(("w", FR.CMD))
    i_poll = calls.index(("r", FR.STATE, 1))
    regs_at = [i for i, c in enumerate(calls) if c == ("regs",)]
    assert regs_at[0] < i_cmd and regs_at[1] > i_poll and len(regs_at) == 3, calls
    assert out["bif"] == {"pre": [0, 0], "post": [0xD0400, 0x4300F]}
    assert out["ticks"] == 14                           # tk0 is the pre read's, tk1 the third
    assert not [c for c in calls if c[0] == "w" and c[1] not in
                (FR.RESULTS + 4, FR.OVERLAP, FR.STATE, FR.RUNID, FR.CMD)]


def test_a_job_without_ticks_keeps_its_bif_words_too(monkeypatch):
    calls = []
    res = PollRes(calls)
    bif_setup(monkeypatch, calls, [(0x10000, 0), (0, 0)])
    out = FR.one_cmd(res, 1, {}, 1, {})
    assert out["bif"] == {"pre": [0x10000, 0], "post": [0, 0]} and "ticks" not in out
    assert calls.count(("regs",)) == 2


def test_a_bif_read_that_fails_is_kept_and_the_job_goes_on(monkeypatch):
    """A dead regs file is itself a reading: kept as an error, never a stop (K5 is printed only)."""
    calls = []
    res = PollRes(calls)
    bif_setup(monkeypatch, calls, [(0, 0), OSError(5, "Input/output error")])
    out = FR.one_cmd(res, 1, {}, 1, {})
    assert out["done"] and out["bif"]["pre"] == [0, 0]
    assert "Input/output error" in out["bif"]["post"]["error"]


def test_a_kick_job_keeps_its_bif_words_around_the_kick(monkeypatch):
    """With a kick the pre read is before the cmd write and the kick, the post after the poll."""
    calls = []
    res = KickRes(calls)
    kick_setup(monkeypatch, calls, res)
    out = FR.one_cmd(res, 1, {}, 1, {}, ticks=True, kick="miscinfo")
    assert set(out["bif"]) == {"pre", "post"}
    i_kick = calls.index(("rd", "miscinfo"))
    regs_at = [i for i, c in enumerate(calls) if c == ("regs",)]
    assert regs_at[0] < calls.index(("w", FR.CMD)) and regs_at[2] > i_kick
