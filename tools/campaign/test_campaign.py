# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The campaign runner: it runs the probe tables
(probes/<unit>/<feature>.toml) one probe at a time on a clean GPU, records the environment,
and writes each table's data (<unit>/<feature>/<probe>/) and its dataset manifest."""
import pathlib
import tomllib

import pytest

import campaign
import probe

ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOL = ROOT / "userspace/libsgxfive/build/sgxfive-test"

TABLE = '''[[probe]]
name = "usse-demo-value"
question = "the pixel is the value moved"
source = "value.s"
params = { A = 0, B = 0, C = 0, D = 0 }
inputs = ["OP", "OUT"]
labels = ["mov 7"]
cases = [["mov r20, #0x00000007", "r20"]]
'''


def table(root: pathlib.Path, unit="usse", feature="demo", text=TABLE) -> pathlib.Path:
    p = root / "probes" / unit / f"{feature}.toml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


class FakeTarget:
    """A target whose baseline is dirty for the first `dirty` checks."""
    name = "fake"

    def __init__(self, dirty=0):
        self.dirty, self.fences, self.ran = dirty, 0, []

    def baseline(self):
        if self.dirty:
            self.dirty -= 1
            return "diff: 12 of 4096 pixels"
        return "diff: 0 of 4096 pixels"

    def fence(self):
        self.fences += 1

    def run(self, probes, work, src_dir):
        self.ran += [p.name for p in probes]
        return "".join(f"probe {p.name}__0: o0 0x00000007\n" for p in probes)

    def environment(self):
        return {"target": "fake"}


@pytest.mark.skipif(not TOOL.exists(), reason="sgxfive-test not built")
def test_a_table_on_the_mock(tmp_path):
    t = table(tmp_path)
    data, ds = tmp_path / "data", tmp_path / "datasets"
    m = campaign.run_table(t, campaign.MockTarget(TOOL), data, ds, repo="data")
    run = data / "usse" / "demo" / "usse-demo-value"
    assert "probe usse-demo-value__0: o0 " in (run / "raw.txt").read_text()
    assert (run / "report.txt").exists() and list((run / "bins").glob("*.bin"))
    env = tomllib.loads((data / "usse" / "demo" / "env.toml").read_text())
    assert env["target"] == "mock" and env["table"] == "probes/usse/demo.toml"
    assert env["probes"]["usse-demo-value"]["after"] == "diff: 0 of 4096 pixels"
    rec = tomllib.loads((ds / "usse-demo.toml").read_text())
    assert rec == m
    assert rec["repo"] == "data" and rec["paths"] == ["usse/demo/"]
    assert rec["recipe"] == "probes/usse/demo.toml" and rec["files"] >= 4 and rec["size"] > 0
    assert len(rec["sha256"]) == 64


def test_a_dirty_gpu_is_fenced_first(tmp_path):
    tgt = FakeTarget(dirty=1)
    campaign.run_table(table(tmp_path), tgt, tmp_path / "d", tmp_path / "ds", repo="data")
    assert tgt.fences == 1 and tgt.ran == ["usse-demo-value"]


def test_a_gpu_that_stays_dirty_stops_the_campaign(tmp_path):
    tgt = FakeTarget(dirty=99)
    with pytest.raises(campaign.CampaignError, match="still dirty"):
        campaign.run_table(table(tmp_path), tgt, tmp_path / "d", tmp_path / "ds", repo="data")
    assert tgt.ran == []


@pytest.mark.parametrize("unit, feature, text, msg", [
    ("gpu", "demo", TABLE, "unit gpu"),
    ("usse", "demo", TABLE.replace("usse-demo-value", "x-value"), "named usse-demo-"),
    ("usse", "Demo", TABLE, "feature Demo"),
])
def test_tables_are_checked(tmp_path, unit, feature, text, msg):
    with pytest.raises(campaign.CampaignError, match=msg):
        campaign.run_table(table(tmp_path, unit, feature, text), FakeTarget(), tmp_path / "d",
                           tmp_path / "ds", repo="data")


def test_extra_checks_see_every_name_and_table(tmp_path, monkeypatch):
    # a caller adds its own checks (a word list, say): each returns a complaint or None
    seen = []
    monkeypatch.setattr(campaign, "CHECKS", [lambda s: seen.append(s) or (
        "says forbidden" if "value" in s else None)])
    with pytest.raises(campaign.CampaignError, match="usse-demo-value: says forbidden"):
        campaign.run_table(table(tmp_path), FakeTarget(), tmp_path / "d", tmp_path / "ds",
                           repo="data")
    assert "usse-demo-value" in seen


def test_the_plan_runs_phases_in_order(tmp_path):
    (tmp_path / "campaign.toml").write_text(
        '[[phase]]\nnumber = 6\ntables = ["probes/usse/b.toml"]\n'
        '[[phase]]\nnumber = 2\ntables = ["probes/usse/a.toml", "probes/pds/c.toml"]\n')
    plan = campaign.load_plan(tmp_path / "campaign.toml")
    assert plan == [(2, "probes/usse/a.toml"), (2, "probes/pds/c.toml"), (6, "probes/usse/b.toml")]
    assert [t for _, t in campaign.select(plan, ["6"])] == ["probes/usse/b.toml"]
    assert [t for _, t in campaign.select(plan, ["probes/pds/c.toml"])] == ["probes/pds/c.toml"]


SWEEP = '''name = "transfer-xfer-words"
about = "two words of a fill's transfer command"
host = "fill"
bits = [0]

[[range]]
space = "xfer"
indices = [12, 13]
'''


@pytest.mark.skipif(not TOOL.exists(), reason="sgxfive-test not built")
def test_a_sweep_table_on_the_mock(tmp_path):
    # a table with [[range]] is a sweep (tools/sweep/sweep.py), named <unit>-<feature>
    t = table(tmp_path, "transfer", "xfer-words", SWEEP)
    rec = campaign.run_table(t, campaign.MockTarget(TOOL), tmp_path / "d", tmp_path / "ds",
                             repo="data")
    run = tmp_path / "d" / "transfer" / "xfer-words"
    assert "baseline" in (run / "raw.txt").read_text()
    assert (run / "report.txt").exists() and (run / "table.toml").read_text() == SWEEP
    assert rec["recipe"] == "probes/transfer/xfer-words.toml"


def test_a_sweep_must_be_named_after_its_table(tmp_path):
    t = table(tmp_path, "transfer", "xfer-words", SWEEP.replace("transfer-xfer-words", "s1-x"))
    with pytest.raises(campaign.CampaignError, match="named transfer-xfer-words"):
        campaign.run_table(t, FakeTarget(), tmp_path / "d", tmp_path / "ds", repo="data")


SCRIPT = '''kind = "script"
name = "isp-msaa-modes"
about = "0x042c bits 1:0 with the multisample words"
script = "msaa-modes.sh"
'''


def test_a_script_table(tmp_path):
    # kind = "script": a hand-run experiment, its script in the table's templates/
    t = table(tmp_path, "isp", "msaa-modes", SCRIPT)
    (t.parent / "templates").mkdir()
    (t.parent / "templates" / "msaa-modes.sh").write_text("echo hello\n")

    class ScriptTarget(FakeTarget):
        def script(self, text):
            return f"ran {len(text)} bytes\n"
    campaign.run_table(t, ScriptTarget(), tmp_path / "d", tmp_path / "ds", repo="data")
    run = tmp_path / "d" / "isp" / "msaa-modes"
    assert (run / "output.txt").read_text() == "ran 11 bytes\n"
    assert (run / "msaa-modes.sh").read_text() == "echo hello\n"


@pytest.mark.skipif(not TOOL.exists(), reason="sgxfive-test not built")
def test_scripts_do_not_run_on_the_mock(tmp_path):
    t = table(tmp_path, "isp", "msaa-modes", SCRIPT)
    (t.parent / "templates").mkdir()
    (t.parent / "templates" / "msaa-modes.sh").write_text("echo hello\n")
    with pytest.raises(campaign.CampaignError, match="laptop"):
        campaign.run_table(t, campaign.MockTarget(TOOL), tmp_path / "d", tmp_path / "ds",
                           repo="data")


def test_a_script_table_runs_locally_in_the_repository_keeping_its_files(tmp_path):
    # LocalHost: the script runs in the repository root with $OUT = the table's directory
    t = table(tmp_path, "isp", "msaa-modes", SCRIPT.replace("\n", "\nbaseline = \"none\"\n", 1))
    (t.parent / "templates").mkdir()
    (t.parent / "templates" / "msaa-modes.sh").write_text(
        'pwd > "$OUT/cwd.txt"; echo hello > "$OUT/extra.tsv"; echo done\n')
    rec = campaign.run_table(t, campaign.LocalHost(), tmp_path / "d", tmp_path / "ds",
                             repo="data", root=tmp_path)
    run = tmp_path / "d" / "isp" / "msaa-modes"
    assert (run / "output.txt").read_text() == "done\n"
    assert (run / "extra.tsv").read_text() == "hello\n"
    assert pathlib.Path((run / "cwd.txt").read_text().strip()).samefile(tmp_path)
    names = sorted(f.name for f in run.iterdir())
    assert names == ["cwd.txt", "env.toml", "extra.tsv", "msaa-modes.sh", "output.txt"]
    assert rec["files"] == len(names)


def test_a_local_script_that_fails_is_an_error(tmp_path):
    t = table(tmp_path, "isp", "msaa-modes", SCRIPT.replace("\n", "\nbaseline = \"none\"\n", 1))
    (t.parent / "templates").mkdir()
    (t.parent / "templates" / "msaa-modes.sh").write_text("echo bad >&2; exit 3\n")
    with pytest.raises(campaign.CampaignError, match="exit 3"):
        campaign.run_table(t, campaign.LocalHost(), tmp_path / "d", tmp_path / "ds",
                           repo="data", root=tmp_path)


CAPTURE = '''kind = "capture"
name = "firmware-layout"
host = "local"
script = "layout.sh"
files = ["src/a.txt"]
'''


def capture(root, text=CAPTURE, body='cat a.txt > "$OUT/copy.txt"; echo done\n'):
    p = root / "captures" / "firmware" / "layout.toml"
    (p.parent / "templates").mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    (p.parent / "templates" / "layout.sh").write_text(body)
    (root / "src").mkdir(exist_ok=True)
    (root / "src" / "a.txt").write_text("from the repository\n")
    return p


def test_a_capture_table_runs_locally_with_its_files(tmp_path):
    # kind = "capture": the closed stack under the harness, no GPU; the script sees its
    # files in its work directory and writes what it captures into $OUT
    t = capture(tmp_path)
    rec = campaign.run_table(t, campaign.LocalHost(), tmp_path / "d", tmp_path / "ds",
                             repo="data-private", root=tmp_path)
    run = tmp_path / "d" / "firmware" / "layout"
    assert (run / "copy.txt").read_text() == "from the repository\n"
    assert (run / "output.txt").read_text() == "done\n"
    assert (run / "layout.sh").exists() and (run / "env.toml").exists()
    assert rec["repo"] == "data-private" and rec["recipe"] == "captures/firmware/layout.toml"
    assert (tmp_path / "ds" / "firmware-layout.toml").exists()


def test_a_capture_is_private(tmp_path):
    t = capture(tmp_path)
    with pytest.raises(campaign.CampaignError, match="private"):
        campaign.run_table(t, campaign.LocalHost(), tmp_path / "d", tmp_path / "ds",
                           repo="data", root=tmp_path)


def test_a_failing_capture_stops_the_campaign(tmp_path):
    t = capture(tmp_path, body="echo broken >&2; exit 3\n")
    with pytest.raises(campaign.CampaignError, match="exit 3"):
        campaign.run_table(t, campaign.LocalHost(), tmp_path / "d", tmp_path / "ds",
                           repo="data-private", root=tmp_path)


def test_a_capture_on_the_build_host_goes_over_ssh(tmp_path, monkeypatch):
    t = capture(tmp_path, CAPTURE.replace('"local"', '"build"'))
    calls = []

    def run(cmd, **kw):
        calls.append(cmd)
        out = "/tmp/w\n" if "mktemp" in " ".join(cmd) else "done\n"
        return campaign.subprocess.CompletedProcess(cmd, 0, out, "")
    monkeypatch.setattr(campaign.subprocess, "run", run)
    host = campaign.BuildHost("builder")
    campaign.run_table(t, host, tmp_path / "d", tmp_path / "ds", repo="data-private",
                       root=tmp_path)
    flat = [" ".join(c) for c in calls]
    assert any(c.startswith("ssh builder") and "mktemp -d" in c for c in flat)
    assert any(c.startswith("scp") and "builder:/tmp/w/" in c for c in flat)  # files out
    assert any("builder:/tmp/w/out/." in c for c in flat)                       # results back
    assert any("rm -rf /tmp/w" in c for c in flat)                              # cleaned up


def test_a_capture_needs_a_capture_host(tmp_path):
    t = capture(tmp_path)
    with pytest.raises(campaign.CampaignError, match="capture host"):
        campaign.run_table(t, FakeTarget(), tmp_path / "d", tmp_path / "ds",
                           repo="data-private", root=tmp_path)


# ---- tables that run before the render path exists (phase 3: a boot-only kernel) --------

BOOT_SCRIPT = '''kind = "script"
name = "platform-boot"
about = "load and boot the firmware"
script = "boot.sh"
baseline = "none"
'''


class NoRenderTarget(FakeTarget):
    """A laptop whose kernel has no render node: the triangle baseline cannot run."""

    def baseline(self):
        raise AssertionError("no triangle on a boot-only kernel")

    def script(self, text):
        return "booted\n"


def test_a_script_table_may_run_without_the_triangle_baseline(tmp_path):
    t = table(tmp_path, "platform", "boot", BOOT_SCRIPT)
    (t.parent / "templates").mkdir()
    (t.parent / "templates" / "boot.sh").write_text("echo boot\n")
    target = NoRenderTarget()
    rec = campaign.run_table(t, target, tmp_path / "d", tmp_path / "ds", repo="data")
    assert target.fences == 0 and rec["files"] == 3
    env = tomllib.loads((tmp_path / "d/platform/boot/env.toml").read_text())
    assert env["probes"]["platform-boot"] == {"baseline": "none"}


def test_a_baseline_is_none_or_the_triangle(tmp_path):
    t = table(tmp_path, "platform", "boot", BOOT_SCRIPT.replace('"none"', '"tri2"'))
    (t.parent / "templates").mkdir()
    (t.parent / "templates" / "boot.sh").write_text("echo boot\n")
    with pytest.raises(campaign.CampaignError, match="baseline"):
        campaign.run_table(t, NoRenderTarget(), tmp_path / "d", tmp_path / "ds", repo="data")


def test_the_laptop_records_the_kernel_commit_firmware_and_debug_option(monkeypatch):
    monkeypatch.setattr(campaign.probe, "target", lambda: ("me@laptop", []))
    monkeypatch.setenv("RESGX545_KERNEL_COMMIT", "0123abcd")
    seen = []

    def ssh(self, cmd):
        seen.append(cmd)
        return "yes\n" if "sgx/regs" in cmd else "x\n"
    monkeypatch.setattr(campaign.LaptopTarget, "_ssh", ssh)
    env = campaign.LaptopTarget().environment()
    assert env["kernel_commit"] == "0123abcd"
    assert env["debug_option"] == "yes"
    assert any("sgx545_ukernel.fw" in c for c in seen)


def test_the_laptop_runs_the_tool_the_sweeps_run(monkeypatch):
    monkeypatch.setattr(campaign.probe, "target", lambda: ("me@laptop", []))
    seen = []
    monkeypatch.setattr(campaign.LaptopTarget, "_ssh",
                        lambda self, cmd: seen.append(cmd) or "diff: 0 of 4096 pixels\n")
    monkeypatch.delenv("SGX_SWEEP_TOOL", raising=False)
    assert campaign.LaptopTarget().tool == "./sgxfive-test"
    monkeypatch.setenv("SGX_SWEEP_TOOL", "./sgxfive-test-1115")
    t = campaign.LaptopTarget()
    t.baseline()
    t.environment()
    assert "sudo -n ./sgxfive-test-1115 tri" in seen[0]
    assert any("sha256sum ./sgxfive-test-1115 " in c for c in seen)


def test_the_build_host_takes_ssh_options(tmp_path, monkeypatch):
    # the laptop as the capture host: its host key goes by an alias
    t = capture(tmp_path, CAPTURE.replace('"local"', '"build"'))
    calls = []

    def run(cmd, **kw):
        calls.append(cmd)
        out = "/tmp/w\n" if "mktemp" in " ".join(cmd) else "done\n"
        return campaign.subprocess.CompletedProcess(cmd, 0, out, "")
    monkeypatch.setattr(campaign.subprocess, "run", run)
    monkeypatch.setenv("RESGX545_BUILD_SSH_OPTS", "-o HostKeyAlias=cedar")
    campaign.run_table(t, campaign.BuildHost("me@laptop"), tmp_path / "d", tmp_path / "ds",
                       repo="data-private", root=tmp_path)
    assert all(c[:3] in (["ssh", "-o", "HostKeyAlias=cedar"], ["scp", "-o", "HostKeyAlias=cedar"])
               for c in calls)


def _build_capture_calls(tmp_path, monkeypatch, libs=None):
    t = capture(tmp_path, CAPTURE.replace('"local"', '"build"'))
    calls = []

    def run(cmd, **kw):
        calls.append(cmd)
        out = "/tmp/w\n" if "mktemp" in " ".join(cmd) else "done\n"
        return campaign.subprocess.CompletedProcess(cmd, 0, out, "")
    monkeypatch.setattr(campaign.subprocess, "run", run)
    if libs is None:
        monkeypatch.delenv("RESGX545_BUILD_CDV_LIBS", raising=False)
    else:
        monkeypatch.setenv("RESGX545_BUILD_CDV_LIBS", libs)
    campaign.run_table(t, campaign.BuildHost("me@laptop"), tmp_path / "d", tmp_path / "ds",
                       repo="data-private", root=tmp_path)
    # the remote command, as the build host's sh -c receives it
    return [campaign.shlex.split(c[-1])[2] for c in calls
            if c[0] == "ssh" and "sh -s" in c[-1]]


def test_the_build_host_gets_the_closed_libraries_path(tmp_path, monkeypatch):
    # the closed usr/lib on the capture host is named on this side: the capture script reads
    # it as $RESGX545_CDV_LIBS there (an environment variable does not cross ssh)
    run = _build_capture_calls(tmp_path, monkeypatch, "/home/me/uk3d lib")
    assert len(run) == 1 and "RESGX545_CDV_LIBS='/home/me/uk3d lib'" in run[0]


def test_without_the_libraries_path_the_script_keeps_its_default(tmp_path, monkeypatch):
    run = _build_capture_calls(tmp_path, monkeypatch)
    assert len(run) == 1 and "RESGX545_CDV_LIBS" not in run[0]


# ---- tables of several kinds -------------------------------------------------------------

MULTI = '''name = "transfer-words"
[[sweep]]
name = "transfer-words-copy"
host = "copy"
[[sweep.range]]
space = "xfer"
[[sweep]]
name = "transfer-words-fill"
host = "fill"
[[sweep.range]]
space = "xfer"
'''


class SweepTarget(FakeTarget):
    def sweep_exec(self):
        return None


def test_a_table_of_several_sweeps_runs_each_into_its_own_directory(tmp_path, monkeypatch):
    ran = []
    monkeypatch.setattr(campaign.sweep, "run",
                        lambda s, execu, out, size_of, **kw: ran.append((s.name, out)) or
                        campaign.sweep.RunResult(1, 1))
    monkeypatch.setattr(campaign.sweep, "tool_size_of", lambda tool: None)
    t = table(tmp_path, "transfer", "words", MULTI)
    target = SweepTarget()
    rec = campaign.run_table(t, target, tmp_path / "d", tmp_path / "ds", repo="data")
    run = tmp_path / "d" / "transfer" / "words"
    assert ran == [("transfer-words-copy", run / "copy"), ("transfer-words-fill", run / "fill")]
    assert (run / "table.toml").read_text() == MULTI
    env = tomllib.loads((run / "env.toml").read_text())
    assert set(env["probes"]) == {"transfer-words-copy", "transfer-words-fill"}
    assert rec["recipe"] == "probes/transfer/words.toml"


def test_a_table_of_several_sweeps_is_named_after_its_table(tmp_path):
    t = table(tmp_path, "transfer", "words",
              MULTI.replace('name = "transfer-words"', 'name = "x"', 1))
    with pytest.raises(campaign.CampaignError, match="named transfer-words"):
        campaign.run_table(t, SweepTarget(), tmp_path / "d", tmp_path / "ds", repo="data")


MIXED = '''name = "isp-mixed"
script = "mixed.sh"
baseline = "none"
needs = ["kpoke"]

''' + TABLE.replace("usse-demo", "isp-mixed")


def test_a_table_may_run_a_script_and_probes(tmp_path):
    t = table(tmp_path, "isp", "mixed", MIXED)
    (t.parent / "templates").mkdir()
    (t.parent / "templates" / "mixed.sh").write_text("echo hello\n")
    (t.parent / "templates" / "value.s").write_text("; none\n")

    class Both(FakeTarget):
        def script(self, text, bins=None):
            self.bins = sorted(p.name for p in pathlib.Path(bins).iterdir())
            return "script ran\n"
    target = Both()
    campaign.run_table(t, target, tmp_path / "d", tmp_path / "ds", repo="data")
    assert target.bins == ["isp-mixed-value__0.bin"]     # the script finds the table's own
    run = tmp_path / "d" / "isp" / "mixed"
    assert (run / "output.txt").read_text() == "script ran\n"
    assert target.ran == ["isp-mixed-value"]
    assert (run / "isp-mixed-value" / "raw.txt").exists()
    rec = tomllib.loads((tmp_path / "ds" / "isp-mixed.toml").read_text())
    assert rec["title"] == "script and probe table isp/mixed"


def test_a_probe_table_is_titled_by_its_kind(tmp_path):
    m = campaign.run_table(table(tmp_path), FakeTarget(), tmp_path / "d", tmp_path / "ds",
                           repo="data")
    assert m["title"] == "probe table usse/demo"


STAGED = '''name = "isp-staged"
script = "staged.sh"
baseline = "none"
needs = ["kpoke"]
stage = ["usse/demo"]

''' + TABLE.replace("usse-demo", "isp-staged")


def test_a_script_gets_the_programs_of_its_table_and_the_tables_it_stages(tmp_path):
    # a script that runs probe programs by hand finds them, built, in the directory the
    # target passes it (SGXFIVE_PROBE_BINS on the laptop)
    table(tmp_path)                                   # probes/usse/demo.toml
    t = table(tmp_path, "isp", "staged", STAGED)
    for d in (t.parent / "templates", tmp_path / "probes" / "usse" / "templates"):
        d.mkdir(exist_ok=True)
        (d / "value.s").write_text("{OP}\nmov.skipinv.end o0, {OUT}\n")
    (t.parent / "templates" / "staged.sh").write_text("ls \"$SGXFIVE_PROBE_BINS\"\n")

    class Staging(FakeTarget):
        def script(self, text, bins=None):
            self.bins = sorted(p.name for p in pathlib.Path(bins).iterdir())
            return "ok\n"
    target = Staging()
    campaign.run_table(t, target, tmp_path / "d", tmp_path / "ds", repo="data")
    assert target.bins == ["isp-staged-value__0.bin", "usse-demo-value__0.bin"]


def test_a_script_with_nothing_to_stage_is_called_as_before(tmp_path):
    t = table(tmp_path, "isp", "msaa-modes", SCRIPT)
    (t.parent / "templates").mkdir()
    (t.parent / "templates" / "msaa-modes.sh").write_text("echo hello\n")

    class Plain(FakeTarget):
        def script(self, text):
            return "plain\n"
    campaign.run_table(t, Plain(), tmp_path / "d", tmp_path / "ds", repo="data")
    assert (tmp_path / "d" / "isp" / "msaa-modes" / "output.txt").read_text() == "plain\n"


def test_the_laptop_script_finds_its_staged_programs():
    body = campaign.with_bins("echo $SGXFIVE_PROBE_BINS\n", "sgxprobes-stage")
    want = 'SGXFIVE_PROBE_BINS="$HOME/sgxprobes-stage"; export SGXFIVE_PROBE_BINS\n'
    assert body.startswith(want)
    assert body.endswith("echo $SGXFIVE_PROBE_BINS\n")


# ---- per-table `needs` and `open` -----------------------------------------------------------

def probe_table(root, names, head=""):
    return table(root, text=head + "\n".join(TABLE.replace("usse-demo-value", f"usse-demo-{n}")
                                             for n in names))


class SshFake(FakeTarget):
    """A target with the laptop's ssh executor: _ssh(cmd) -> stdout."""

    def __init__(self, debugfs=("kpoke", "regs"), dev=("card0",)):
        super().__init__()
        self.debugfs, self.dev, self.cmds = debugfs, dev, []

    def _ssh(self, cmd):
        self.cmds.append(cmd)
        if cmd == "sudo -n dmesg":                  # holds the table's mark, if it wrote one
            return "".join(f"[1.0] {m}\n" for m in self.marks())
        ok = f"{campaign.OK}\n" if campaign.OK in cmd else ""      # a command that succeeds
        return "".join(f"sgx/{f}\n" for f in self.debugfs) + \
            "".join(f"dev/{d}\n" for d in self.dev) + ok


def _marks(self):
    import re
    return [re.search(r"resgx545 campaign \S+ \S+ \S+", c).group(0)
            for c in self.cmds if "/dev/kmsg" in c]


SshFake.marks = _marks


def run(path, target, tmp):
    return campaign.run_table(path, target, tmp / "d", tmp / "ds", repo="data")


def test_open_probes_run_last_in_their_table(tmp_path):
    t = probe_table(tmp_path, ["a", "b", "c"], head='open = ["usse-demo-a"]\n')
    tg = FakeTarget()
    rec = run(t, tg, tmp_path)
    assert tg.ran == ["usse-demo-b", "usse-demo-c", "usse-demo-a"]
    assert rec["open"] == ["usse-demo-a"]


def test_the_fields_are_in_the_manifest_after_the_recipe_and_in_the_environment(tmp_path):
    t = probe_table(tmp_path, ["a", "b"], head='open = ["usse-demo-b"]\nneeds = []\n')
    rec = run(t, FakeTarget(), tmp_path)
    man = tomllib.loads((tmp_path / "ds" / "usse-demo.toml").read_text())
    assert man["open"] == ["usse-demo-b"] and man == rec
    assert list(man)[-3:] == ["recipe", "needs", "open"]
    env = tomllib.loads((tmp_path / "d" / "usse" / "demo" / "env.toml").read_text())
    assert env["open"] == ["usse-demo-b"] and "usse-demo-a" in env["probes"]
    assert list(env)[:3] == ["target", "needs", "open"]


def test_an_open_probe_that_is_not_in_the_table_is_an_error(tmp_path):
    t = probe_table(tmp_path, ["a"], head='open = ["usse-demo-zz"]\n')
    with pytest.raises(campaign.CampaignError, match="usse-demo-zz"):
        run(t, FakeTarget(), tmp_path)


def test_a_dirty_gpu_after_the_last_open_probe_is_fenced(tmp_path):
    class Wedge(FakeTarget):
        def run(self, probes, work, src_dir):
            if probes[0].name == "usse-demo-o":
                self.dirty = 2      # the after-baseline sees one, the final check the other
            return super().run(probes, work, src_dir)
    t = probe_table(tmp_path, ["o", "b"], head='open = ["usse-demo-o"]\n')
    tg = Wedge()
    run(t, tg, tmp_path)
    assert tg.ran[-1] == "usse-demo-o" and tg.fences == 1 and tg.dirty == 0


def test_tables_without_the_fields_have_neither_key(tmp_path):
    rec = run(probe_table(tmp_path, ["a", "b"]), FakeTarget(), tmp_path)
    assert "open" not in rec and "needs" not in rec


def test_needs_are_checked_against_the_targets_debugfs(tmp_path):
    t = probe_table(tmp_path, ["a"], head='needs = ["kpoke", "timer_clock"]\n')
    tg = SshFake(debugfs=("kpoke", "regs"))
    with pytest.raises(campaign.CampaignError, match="timer_clock") as e:
        run(t, tg, tmp_path)
    assert "needs timer_clock" in str(e.value) and "needs kpoke" not in str(e.value)
    assert tg.ran == [] and not (tmp_path / "d").exists()
    assert any("dri" in c for c in tg.cmds)


def test_needs_met_run_and_are_recorded(tmp_path):
    t = probe_table(tmp_path, ["a"], head='needs = ["kpoke", "render"]\n')
    tg = SshFake(debugfs=("kpoke",), dev=("card0", "renderD128"))
    rec = run(t, tg, tmp_path)
    assert tg.ran == ["usse-demo-a"] and rec["needs"] == ["kpoke", "render"]


def test_render_is_the_render_node(tmp_path):
    t = probe_table(tmp_path, ["a"], head='needs = ["render"]\n')
    with pytest.raises(campaign.CampaignError, match="render"):
        run(t, SshFake(dev=("card0",)), tmp_path)


def test_targets_without_a_debugfs_are_not_checked(tmp_path):
    t = probe_table(tmp_path, ["a"], head='needs = ["kpoke"]\n')
    assert run(t, FakeTarget(), tmp_path)["needs"] == ["kpoke"]


def test_the_fields_must_be_lists_of_names(tmp_path):
    t = probe_table(tmp_path, ["a"], head='needs = "kpoke"\n')
    with pytest.raises(campaign.CampaignError, match="needs"):
        run(t, FakeTarget(), tmp_path)


def test_the_debugfs_glob_is_expanded_as_root():
    # /sys/kernel/debug is root's: a glob the user's shell expands matches nothing
    assert "sudo -n sh -c 'ls /sys/kernel/debug/dri/*/sgx/'" in campaign._LIST_NEEDS


@pytest.mark.skipif(not TOOL.exists(), reason="sgxfive-test not built")
def test_a_sweep_table_may_carry_the_fields(tmp_path):
    t = table(tmp_path, "transfer", "xfer-words",
              SWEEP.replace("host =", 'needs = ["kpoke"]\nopen = ["transfer-xfer-words-x"]\n'
                                      'host ='))
    rec = campaign.run_table(t, campaign.MockTarget(TOOL), tmp_path / "d", tmp_path / "ds",
                             repo="data")
    assert rec["open"] == ["transfer-xfer-words-x"] and rec["needs"] == ["kpoke"]


# ---- a table that did not finish gets no manifest -------------------------------------------

def test_a_stopped_sweep_gets_no_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(campaign.sweep, "run", lambda *a, **kw: campaign.sweep.RunResult(
        3, 10, "stopped: 5 errors in a row, the last c7"))
    monkeypatch.setattr(campaign.sweep, "tool_size_of", lambda tool: None)
    t = table(tmp_path, "transfer", "words", MULTI)
    with pytest.raises(campaign.CampaignError, match="transfer-words-copy.*stopped"):
        campaign.run_table(t, SweepTarget(), tmp_path / "d", tmp_path / "ds", repo="data")
    assert not (tmp_path / "ds" / "transfer-words.toml").exists()


def test_a_sweep_that_ran_fewer_cases_than_it_has_gets_no_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(campaign.sweep, "run",
                        lambda *a, **kw: campaign.sweep.RunResult(3, 10))
    monkeypatch.setattr(campaign.sweep, "tool_size_of", lambda tool: None)
    t = table(tmp_path, "transfer", "words", MULTI)
    with pytest.raises(campaign.CampaignError, match="3 of 10"):
        campaign.run_table(t, SweepTarget(), tmp_path / "d", tmp_path / "ds", repo="data")


# ---- the laptop's script -------------------------------------------------------------------

class Calls:
    """subprocess.run stand-in: records the commands, answers by a function."""

    def __init__(self, answer=None):
        self.calls, self.answer = [], answer or (lambda cmd, kw: (0, "out\n", ""))

    def __call__(self, cmd, **kw):
        self.calls.append((cmd, kw))
        rc, out, err = self.answer(cmd, kw)
        return campaign.subprocess.CompletedProcess(cmd, rc, out, err)


@pytest.fixture
def laptop(monkeypatch):
    monkeypatch.setattr(campaign.probe, "target", lambda: ("me@cedar", ["-o", "X=1"]))
    return campaign.LaptopTarget()


def test_the_laptop_script_stages_the_programs_and_prefixes_the_bins_line(
        laptop, monkeypatch, tmp_path):
    (tmp_path / "b.bin").write_text("b")
    (tmp_path / "a.bin").write_text("a")
    run = Calls()
    monkeypatch.setattr(campaign.subprocess, "run", run)
    assert laptop.script("echo hi\n", bins=tmp_path) == "out\n"
    flat = [" ".join(c) for c, _ in run.calls]
    assert "rm -rf sgxprobes-stage && mkdir sgxprobes-stage" in flat[0]
    assert flat[1].startswith("scp -q -o X=1") and flat[1].index("a.bin") < flat[1].index("b.bin")
    assert flat[1].endswith("me@cedar:sgxprobes-stage/")
    cmd, kw = run.calls[2]
    assert cmd[-1] == "sh -s" and kw["input"].startswith("SGXFIVE_PROBE_BINS=")
    assert kw["input"].endswith("echo hi\n")


def test_a_laptop_script_that_exits_nonzero_is_an_error(laptop, monkeypatch):
    monkeypatch.setattr(campaign.subprocess, "run",
                        Calls(lambda c, k: (1, "no sgx debugfs directory\n", "sudo: bad\n")))
    with pytest.raises(campaign.CampaignError, match="exit 1.*no sgx debugfs directory"):
        laptop.script("exit 1\n")


def test_a_failing_staging_is_a_campaign_error(laptop, monkeypatch, tmp_path):
    (tmp_path / "a.bin").write_text("a")

    def boom(cmd, **kw):
        raise campaign.subprocess.CalledProcessError(255, cmd)
    monkeypatch.setattr(campaign.subprocess, "run", boom)
    with pytest.raises(campaign.CampaignError, match="ssh|scp"):
        laptop.script("echo\n", bins=tmp_path)


def test_a_laptop_script_that_times_out_is_a_campaign_error(laptop, monkeypatch):
    def slow(cmd, **kw):
        raise campaign.subprocess.TimeoutExpired(cmd, 1)
    monkeypatch.setattr(campaign.subprocess, "run", slow)
    with pytest.raises(campaign.CampaignError, match="timed out"):
        laptop.script("echo\n")


# ---- the build host's copies ---------------------------------------------------------------

def test_a_failed_download_of_a_capture_is_an_error(tmp_path, monkeypatch):
    t = capture(tmp_path, CAPTURE.replace('"local"', '"build"'))

    def answer(cmd, kw):
        flat = " ".join(cmd)
        if "mktemp" in flat:
            return 0, "/tmp/w\n", ""
        if cmd[0] == "scp" and "/out/." in flat:
            return 1, "", "scp: connection lost\n"
        return 0, "done\n", ""
    monkeypatch.setattr(campaign.subprocess, "run", Calls(answer))
    with pytest.raises(campaign.CampaignError, match="connection lost"):
        campaign.run_table(t, campaign.BuildHost("builder"), tmp_path / "d", tmp_path / "ds",
                           repo="data-private", root=tmp_path)


def test_a_failed_upload_of_a_capture_is_an_error(tmp_path, monkeypatch):
    t = capture(tmp_path, CAPTURE.replace('"local"', '"build"'))

    def answer(cmd, kw):
        if "mktemp" in " ".join(cmd):
            return 0, "/tmp/w\n", ""
        return (1, "", "scp: no route\n") if cmd[0] == "scp" else (0, "", "")
    monkeypatch.setattr(campaign.subprocess, "run", Calls(answer))
    with pytest.raises(campaign.CampaignError, match="no route"):
        campaign.run_table(t, campaign.BuildHost("builder"), tmp_path / "d", tmp_path / "ds",
                           repo="data-private", root=tmp_path)


def test_two_files_of_a_capture_may_not_share_a_name(tmp_path):
    t = capture(tmp_path, CAPTURE.replace('["src/a.txt"]', '["src/a.txt", "other/a.txt"]'))
    with pytest.raises(campaign.CampaignError, match="a.txt"):
        campaign.run_table(t, campaign.LocalHost(), tmp_path / "d", tmp_path / "ds",
                           repo="data-private", root=tmp_path)


# ---- main --------------------------------------------------------------------------------

def test_main_reports_a_sweep_error_in_one_line(tmp_path, capsys, monkeypatch):
    t = table(tmp_path, "transfer", "xfer-words")

    def bad(*a, **kw):
        raise campaign.sweep.SweepError("host 'zz' is not one of the hosts")
    monkeypatch.setattr(campaign, "run_table", bad)
    rc = campaign.main(["--data", str(tmp_path / "d"), "--datasets", str(tmp_path / "ds"),
                        str(t)])
    err = capsys.readouterr().err
    assert rc == 1 and "xfer-words.toml" in err and "zz" in err and "Traceback" not in err


def test_main_reports_a_subprocess_error_naming_the_table(tmp_path, capsys, monkeypatch):
    t = table(tmp_path)

    def boom(*a, **kw):
        raise campaign.subprocess.CalledProcessError(255, ["ssh", "h"])
    monkeypatch.setattr(campaign, "run_table", boom)
    rc = campaign.main(["--data", str(tmp_path / "d"), "--datasets", str(tmp_path / "ds"),
                        str(t)])
    err = capsys.readouterr().err
    assert rc == 1 and "demo.toml" in err and "255" in err and "Traceback" not in err


def test_an_unknown_target_is_refused(tmp_path):
    with pytest.raises(SystemExit):
        campaign.main(["--target", "labtop", "--data", "d", "--datasets", "s", "t.toml"])


def test_an_argument_that_names_nothing_in_the_plan_is_reported(tmp_path, capsys):
    (tmp_path / "campaign.toml").write_text(
        '[[phase]]\nnumber = 2\ntables = ["probes/usse/a.toml"]\n')
    rc = campaign.main(["--plan", str(tmp_path / "campaign.toml"), "--data", "d",
                        "--datasets", "s", "7x"])
    assert rc == 1 and "7x" in capsys.readouterr().err


# ---- the kind of a table; which target runs what --------------------------------------------

def test_a_comment_that_says_probe_does_not_make_a_probe_table(tmp_path):
    t = table(tmp_path, "isp", "msaa-modes", SCRIPT + "# one [[probe]] later\n")
    (t.parent / "templates").mkdir()
    (t.parent / "templates" / "msaa-modes.sh").write_text("echo hello\n")

    class Plain(FakeTarget):
        def script(self, text):
            return "plain\n"
    rec = campaign.run_table(t, Plain(), tmp_path / "d", tmp_path / "ds", repo="data")
    assert rec["title"] == "script table isp/msaa-modes"


def test_a_script_table_without_a_script_is_an_error(tmp_path):
    t = table(tmp_path, "isp", "msaa-modes", SCRIPT.replace('script = "msaa-modes.sh"\n', ""))
    with pytest.raises(campaign.CampaignError, match="script"):
        campaign.run_table(t, FakeTarget(), tmp_path / "d", tmp_path / "ds", repo="data")


def test_a_capture_with_a_range_runs_no_sweep(tmp_path):
    t = capture(tmp_path, CAPTURE + '[[range]]\nspace = "xfer"\n')
    campaign.run_table(t, campaign.LocalHost(), tmp_path / "d", tmp_path / "ds",
                       repo="data-private", root=tmp_path)
    assert not (tmp_path / "d" / "firmware" / "layout" / "table.toml").exists()


def test_a_script_with_programs_on_the_mock_is_a_campaign_error(tmp_path):
    with pytest.raises(campaign.CampaignError, match="laptop"):
        campaign.MockTarget(TOOL).script("echo\n", bins=tmp_path)


def test_a_local_run_of_a_table_that_needs_the_gpu_is_a_campaign_error(tmp_path):
    with pytest.raises(campaign.CampaignError, match="local"):
        campaign.run_table(table(tmp_path), campaign.LocalHost(), tmp_path / "d",
                           tmp_path / "ds", repo="data")
    t = table(tmp_path, "isp", "msaa-modes", SCRIPT)          # baseline "tri" by default
    (t.parent / "templates").mkdir()
    (t.parent / "templates" / "msaa-modes.sh").write_text("echo\n")
    with pytest.raises(campaign.CampaignError, match='baseline = "none"'):
        campaign.run_table(t, campaign.LocalHost(), tmp_path / "d", tmp_path / "ds",
                           repo="data", root=tmp_path)


class KnobFake(SshFake):
    """Records the order of the knob writes and the probe runs; vm_low starts as `was`."""

    def __init__(self, fail=False, was="N", fail_write=None):
        super().__init__(debugfs=("vm_low",), dev=("card0", "renderD128"))
        self.fail, self.log, self.state = fail, [], was
        self.fail_write = fail_write          # "on" / "off": that write exits non-zero

    def _ssh(self, cmd):
        if "vm_low" in cmd and "cat" in cmd:
            return self.state + "\n"
        if "vm_low" in cmd and ">" in cmd:
            val = "Y" if "echo Y" in cmd else "N"
            self.log.append("on" if val == "Y" else "off")
            if self.fail_write == self.log[-1]:
                self.cmds.append(cmd)
                return ""
            self.state = val
        return super()._ssh(cmd)

    def run(self, probes, work, src_dir):
        self.log.append("probe")
        if self.fail:
            raise campaign.probe.ProbeError("sgxfive-test failed")
        return super().run(probes, work, src_dir)


VM_LOW = 'needs = ["render", "vm_low"]\n'


def test_a_table_that_needs_vm_low_turns_it_on_for_its_probes_and_off_after(tmp_path):
    # the low mappings of the PDS memory probes need the kernel's sgx/vm_low switched on
    tg = KnobFake()
    run(probe_table(tmp_path, ["a"], head=VM_LOW), tg, tmp_path)
    assert tg.log == ["on", "probe", "off"]
    tg = KnobFake(fail=True)
    with pytest.raises(campaign.probe.ProbeError):
        run(probe_table(tmp_path / "x", ["a"], head=VM_LOW), tg, tmp_path / "x")
    assert tg.log == ["on", "probe", "off"]


def test_the_switch_goes_back_to_its_previous_value(tmp_path):
    tg = KnobFake(was="Y")
    run(probe_table(tmp_path, ["a"], head=VM_LOW), tg, tmp_path)
    assert tg.state == "Y"


def test_a_table_without_a_knob_need_writes_no_switch(tmp_path):
    tg = KnobFake()
    run(probe_table(tmp_path, ["a"], head='needs = ["render"]\n'), tg, tmp_path)
    assert tg.log == ["probe"]


def test_the_switch_goes_off_when_the_table_is_refused_after_it_went_on(tmp_path):
    tg = KnobFake()
    t = probe_table(tmp_path, ["a"], head=VM_LOW + 'open = ["usse-demo-zz"]\n')
    with pytest.raises(campaign.CampaignError, match="usse-demo-zz"):
        run(t, tg, tmp_path)
    assert tg.log[-1] == "off" and "probe" not in tg.log


def test_a_switch_write_that_fails_is_a_campaign_error_and_no_probe_runs(tmp_path):
    tg = KnobFake(fail_write="on")
    with pytest.raises(campaign.CampaignError, match="vm_low"):
        run(probe_table(tmp_path, ["a"], head=VM_LOW), tg, tmp_path)
    assert "probe" not in tg.log


def test_a_restore_that_fails_does_not_mask_the_error_that_stopped_the_table(tmp_path):
    tg = KnobFake(fail=True, fail_write="off")
    with pytest.raises(campaign.probe.ProbeError):
        run(probe_table(tmp_path, ["a"], head=VM_LOW), tg, tmp_path)
    tg = KnobFake(fail_write="off")             # a table that went well: the failure shows
    with pytest.raises(campaign.CampaignError, match="not restored"):
        run(probe_table(tmp_path / "y", ["a"], head=VM_LOW), tg, tmp_path / "y")


class LogFake(SshFake):
    """A laptop whose kernel log holds a line before the table's mark and some after."""

    def __init__(self, *a, mark_ok=True, lines=None, **kw):
        super().__init__(*a, **kw)
        self.mark_ok, self.lines = mark_ok, lines

    def mark(self):
        return self.marks()[-1]

    def _ssh(self, cmd):
        self.cmds.append(cmd)
        if cmd == "sudo -n dmesg":         # the kernel log is root's on the laptop
            if not self.mark_ok:
                return "[1.0] gma500 0000:00:02.0: [drm] sgxfive: earlier\n"
            tail = self.lines or (
                "[3.0] gma500 0000:00:02.0: [drm] sgxfive: BIF fault 0x90020 at 0x0\n"
                "[4.0] gma500 0000:00:02.0: [drm] sgxfive: EDM up\n")
            return ("[1.0] gma500 0000:00:02.0: [drm] sgxfive: earlier\n"
                    f"[2.0] {self.mark()}\n" + tail)
        if "/dev/kmsg" in cmd and not self.mark_ok:
            return ""                      # tee failed
        return super()._ssh(cmd)


def kernel_log(tmp_path):
    return (tmp_path / "d" / "usse" / "demo" / "kernel.log").read_text()


def test_the_kernel_log_of_a_tables_run_is_kept_with_its_data(tmp_path):
    # faults and recoveries are reported only in the kernel log: a table keeps the lines the
    # driver logged during its run, after a mark written when it starts; the mark line is the
    # first line, so a reader can tell a clean run from a lost mark
    t = probe_table(tmp_path, ["a"], head='needs = ["render"]\n')
    tg = LogFake(debugfs=(), dev=("card0", "renderD128"))
    rec = run(t, tg, tmp_path)
    log = kernel_log(tmp_path)
    assert "BIF fault 0x90020" in log and "EDM up" in log and "earlier" not in log
    assert tg.mark() in log.splitlines()[0]
    files = [f for f in (tmp_path / "d" / "usse" / "demo").rglob("*") if f.is_file()]
    assert rec["files"] == len(files) and "kernel.log" in {f.name for f in files}


def test_a_mark_that_is_not_in_the_log_is_a_campaign_error_with_no_manifest(tmp_path):
    t = probe_table(tmp_path, ["a"], head='needs = ["render"]\n')
    tg = LogFake(debugfs=(), dev=("card0", "renderD128"))
    tg.lines = None
    orig = tg._ssh
    tg._ssh = lambda cmd: ("[1.0] gma500 other\n" if cmd == "sudo -n dmesg" else orig(cmd))
    with pytest.raises(campaign.CampaignError, match="mark"):
        run(t, tg, tmp_path)
    assert not (tmp_path / "ds" / "usse-demo.toml").exists()


JOURNAL = "sudo -n journalctl -k -b -o short-monotonic --no-pager"


def test_a_mark_the_ring_lost_is_read_from_the_journal(tmp_path):
    # a long run (thousands of kreg writes) wraps the kernel ring: dmesg no longer holds the
    # mark, the journal still does, and the table keeps the journal's lines, not an error
    t = probe_table(tmp_path, ["a"], head='needs = ["render"]\n')
    tg = LogFake(debugfs=(), dev=("card0", "renderD128"))
    orig = tg._ssh

    def ssh(cmd):
        if cmd == "sudo -n dmesg":
            return "[9.0] gma500 0000:00:02.0: [drm] sgxfive: late line only\n"
        if cmd == JOURNAL:
            return ("[1.0] cedar kernel: gma500 0000:00:02.0: [drm] sgxfive: earlier\n"
                    f"[2.0] cedar kernel: {tg.mark()}\n"
                    "[3.0] cedar kernel: gma500 0000:00:02.0: [drm] sgxfive: kreg 0x0818\n"
                    "[3.1] cedar kernel: usb 1-1: unrelated\n")
        return orig(cmd)
    tg._ssh = ssh
    run(t, tg, tmp_path)
    log = kernel_log(tmp_path)
    assert tg.mark() in log.splitlines()[0] and "kreg 0x0818" in log
    assert "earlier" not in log and "unrelated" not in log and "late line only" not in log


def test_the_journal_copy_keeps_the_continuation_lines_of_an_oops_trace(tmp_path):
    # the journal prefixes each line of a trace with the host and "kernel:" and keeps the
    # message's own leading blank: those lines follow their Call Trace, an unrelated line ends it
    t = probe_table(tmp_path, ["a"], head='needs = ["render"]\n')
    tg = LogFake(debugfs=(), dev=("card0", "renderD128"))
    orig = tg._ssh

    def ssh(cmd):
        if cmd == "sudo -n dmesg":
            return "[9.0] gma500 0000:00:02.0: [drm] sgxfive: late line only\n"
        if cmd == JOURNAL:
            return (f"[2.0] cedar unknown: {tg.mark()}\n"
                    "[3.0] cedar kernel: Call Trace:\n"
                    "[3.0] cedar kernel:  <TASK>\n"
                    "[3.0] cedar kernel:  ? sgx_job_run+0x1c/0x40 [gma500_gfx]\n"
                    "[3.0] cedar kernel:  </TASK>\n"
                    "[3.1] cedar kernel: usb 1-1: unrelated\n"
                    "[3.2] cedar kernel:  ? not part of the trace\n")
        return orig(cmd)
    tg._ssh = ssh
    run(t, tg, tmp_path)
    log = kernel_log(tmp_path)
    assert "<TASK>" in log and "sgx_job_run+0x1c/0x40" in log and "</TASK>" in log
    assert "unrelated" not in log and "not part of the trace" not in log


def test_the_journal_is_read_for_the_current_boot_only():
    assert " -b " in campaign.JOURNAL


def test_a_mark_in_neither_the_ring_nor_the_journal_is_a_campaign_error(tmp_path):
    t = probe_table(tmp_path, ["a"], head='needs = ["render"]\n')
    tg = LogFake(debugfs=(), dev=("card0", "renderD128"))
    orig = tg._ssh
    tg._ssh = lambda cmd: ("[1.0] x\n" if cmd in ("sudo -n dmesg", JOURNAL) else orig(cmd))
    with pytest.raises(campaign.CampaignError, match="journal"):
        run(t, tg, tmp_path)


def test_a_mark_write_that_fails_is_a_campaign_error(tmp_path):
    t = probe_table(tmp_path, ["a"], head='needs = ["render"]\n')
    tg = LogFake(debugfs=(), dev=("card0", "renderD128"), mark_ok=False)
    with pytest.raises(campaign.CampaignError, match="mark"):
        run(t, tg, tmp_path)


def test_oops_bug_and_trace_lines_are_kept(tmp_path):
    t = probe_table(tmp_path, ["a"], head='needs = ["render"]\n')
    tg = LogFake(debugfs=(), dev=("card0", "renderD128"), lines=(
        "[3.0] BUG: unable to handle kernel paging request at 0\n"
        "[3.1] Oops: 0000 [#1] SMP\n"
        "[3.2] Call Trace:\n"
        "[3.3]  ? sgxfive_irq+0x10/0x20\n"
        "[3.4]  worker_thread+0x1/0x2\n"
        "[3.5] usb 1-1: unrelated\n"
        "[3.6]  indented but not a trace\n"
        "[3.7] WARNING: CPU: 0 PID: 1 at foo\n"))
    run(t, tg, tmp_path)
    log = kernel_log(tmp_path)
    for kept in ("BUG:", "Oops:", "Call Trace", "sgxfive_irq", "worker_thread", "WARNING"):
        assert kept in log
    assert "unrelated" not in log and "not a trace" not in log


def test_a_scripts_case_marks_are_kept(tmp_path):
    # a script marks the kernel log at each of its cases ("resgx545 case NAME ..."), so a
    # reader can tell which case the driver's lines follow (render_words.py log)
    t = probe_table(tmp_path, ["a"], head='needs = ["render"]\n')
    tg = LogFake(debugfs=(), dev=("card0", "renderD128"), lines=(
        "[4.0] resgx545 case fault 1700000000-42\n"
        "[4.1] gma500 0000:00:02.0: [drm] sgxfive: job 7 hung, recovery held\n"
        "[4.2] resgx545 other words\n"))
    run(t, tg, tmp_path)
    log = kernel_log(tmp_path)
    assert "resgx545 case fault 1700000000-42" in log and "recovery held" in log
    assert "other words" not in log


def test_the_kernel_log_is_kept_when_the_table_fails(tmp_path):
    tg = LogFake(debugfs=("vm_low",), dev=("card0", "renderD128"))
    tg.run = lambda *a: (_ for _ in ()).throw(campaign.probe.ProbeError("boom"))
    with pytest.raises(campaign.probe.ProbeError):
        run(probe_table(tmp_path, ["a"], head=VM_LOW), tg, tmp_path)
    assert "BIF fault 0x90020" in kernel_log(tmp_path)


def test_the_mark_is_shell_quoted_and_unique_per_run(tmp_path):
    marks = set()
    for i in range(2):
        tg = LogFake(debugfs=(), dev=("card0", "renderD128"))
        run(probe_table(tmp_path / str(i), ["a"], head='needs = ["render"]\n'), tg,
            tmp_path / str(i))
        marks.add(tg.mark())
    assert len(marks) == 2
    tg = LogFake(debugfs=())
    campaign._log_mark(tg, "a'b; rm x")
    assert campaign.shlex.quote("resgx545 campaign a'b; rm x") not in tg.cmds[0]  # has the time
    assert "'\"'\"'" in tg.cmds[0]          # the quote is escaped, not left open


def test_targets_without_ssh_keep_no_kernel_log(tmp_path):
    run(probe_table(tmp_path, ["a"]), FakeTarget(), tmp_path)
    assert not (tmp_path / "d" / "usse" / "demo" / "kernel.log").exists()


# ---- regwidth tables (regwidth.py, regwidth.c) ---------------------------------------------

REGWIDTH = '''kind = "regwidth"
name = "platform-register-widths"
needs = ["regs"]

[[register]]
offset = 0x0418
name = "CR_ISP_LINE_SAMPLE_POS"
batch = 1

[[readonly]]
offset = 0x0080
name = "CR_SOFT_RESET"
reason = "a write resets units"
'''

REGWIDTH_OUT = """#### batch 1
regwidth 0x0418 prior 0x00000001 ones 0x00000001 back 0x00000001 zero 0x00000000 restored 0x00000001
regval 0x0080 0x00000000
## check 1: ok
"""


class WidthTarget(FakeTarget):
    def script(self, text, bins=None):
        self.text = text
        self.bins = sorted(p.name for p in pathlib.Path(bins).iterdir())
        return REGWIDTH_OUT


def test_a_regwidth_table_runs_its_generated_script_with_the_program(tmp_path):
    t = table(tmp_path, "platform", "register-widths", REGWIDTH)
    target = WidthTarget()
    rec = campaign.run_table(t, target, tmp_path / "d", tmp_path / "ds", repo="data")
    assert target.bins == ["regwidth.c"]
    assert "#### batch 1" in target.text and "0x0418" in target.text
    run = tmp_path / "d" / "platform" / "register-widths"
    assert (run / "output.txt").read_text() == REGWIDTH_OUT
    widths = tomllib.loads((run / "widths.toml").read_text())
    assert widths["reg"]["0x0418"]["implemented"] == "0"
    assert widths["readonly"]["0x0080"]["values"] == ["0x00000000"]
    assert (run / "table.toml").read_text() == REGWIDTH
    assert rec["title"] == "regwidth table platform/register-widths"
    assert rec["needs"] == ["regs"]


def test_a_regwidth_table_that_writes_a_denied_register_is_refused_before_it_runs(tmp_path):
    t = table(tmp_path, "platform", "register-widths",
              REGWIDTH.replace("offset = 0x0418", "offset = 0x0c84"))

    class Never(FakeTarget):
        def script(self, text, bins=None):
            raise AssertionError("ran")
    with pytest.raises(campaign.CampaignError, match="deny"):
        campaign.run_table(t, Never(), tmp_path / "d", tmp_path / "ds", repo="data")


def test_a_regwidth_run_that_stops_keeps_its_output_and_writes_no_manifest(tmp_path):
    t = table(tmp_path, "platform", "register-widths", REGWIDTH)

    class Stops(FakeTarget):
        def script(self, text, bins=None):
            raise campaign.CampaignError("script failed (exit 1)", output="## check 1: FAILED\n")
    with pytest.raises(campaign.CampaignError):
        campaign.run_table(t, Stops(), tmp_path / "d", tmp_path / "ds", repo="data")
    run = tmp_path / "d" / "platform" / "register-widths"
    assert (run / "output.txt").read_text() == "## check 1: FAILED\n"
    assert not (tmp_path / "ds" / "platform-register-widths.toml").exists()


def test_a_regwidth_table_is_named_for_its_unit_and_feature(tmp_path):
    t = table(tmp_path, "platform", "widths", REGWIDTH)
    with pytest.raises(campaign.CampaignError, match="named platform-widths"):
        campaign.run_table(t, WidthTarget(), tmp_path / "d", tmp_path / "ds", repo="data")


def test_a_failed_laptop_script_carries_its_output(monkeypatch):
    class R:
        returncode, stdout, stderr = 1, "## check 1: FAILED\n", ""
    monkeypatch.setattr(campaign.subprocess, "run", lambda *a, **k: R())
    monkeypatch.setattr(campaign.probe, "target", lambda: ("host", []))
    with pytest.raises(campaign.CampaignError) as e:
        campaign.LaptopTarget().script("exit 1\n")
    assert e.value.output == "## check 1: FAILED\n"


def test_the_fence_builds_its_probe_from_its_own_table(monkeypatch, tmp_path):
    """11.14: the fence probe lives in probes/pbe/sideband.toml; it must be built from that
    table's templates (eot_plain.s, pix_op.s), not the default usse templates, or a dirty GPU
    stops every later table instead of being fenced."""
    got = {}

    def fake_run_remote(ps, work, src_dir=None):
        got["names"], got["src_dir"] = [p.name for p in ps], src_dir
        for p in ps:
            probe.build(p, tmp_path / "bins", src_dir)
            probe.build_helpers(ps, tmp_path / "bins", src_dir)
        raise probe.ProbeError("the fence hangs on purpose")

    monkeypatch.setattr(probe, "run_remote", fake_run_remote)
    monkeypatch.setattr(probe, "target", lambda: ("host", []))
    campaign.LaptopTarget.fence(campaign.LaptopTarget.__new__(campaign.LaptopTarget))
    assert got["names"] == [campaign.FENCE_PROBE]
    assert got["src_dir"] == probe.PROBES / "pbe" / "templates"
