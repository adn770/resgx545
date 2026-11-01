# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The campaign runner: runs the probe tables,
probes/<unit>/<feature>.toml, one probe at a time on a clean GPU, and writes each table's
data and its dataset manifest.

A table is one of three kinds, or holds several of them (sweeps, then a script, then probes). A
probe table ([[probe]], tools/usse-asm/probe.py) runs probe
by probe as below. A sweep ([[range]], tools/sweep/sweep.py), named <unit>-<feature>, runs
with its own unpoked baseline per case into the table's directory; a table of several sweeps
([[sweep]], each with its own name, host and [[sweep.range]]) runs each into a directory of its
own, named by the tail of the sweep's name. A script table
(kind = "script", named <unit>-<feature>) runs its script, from the table's templates/, on
the laptop (or, with --target local, in the repository root with $OUT the table's directory;
local has no GPU, so only with baseline = "none") and keeps its output; the mock cannot run
one. A failing script (nonzero exit, ssh or scp error), a sweep that stopped or ran fewer cases
than it has, and a table the target cannot run are CampaignErrors: no manifest.
A script table that runs before the render path exists (a boot-only kernel) says `baseline = "none"`: no triangle baseline
before or after it, and no fence. A capture table (kind = "capture",
under captures/<unit>/, always for the private data repository) runs the closed stack without
the GPU: its script, from the table's templates/, runs on a capture host (--target local, or
--target build: $RESGX545_BUILD_HOST over ssh) with the table's `files` copied into its work
directory, and writes what it captures into $OUT.

For every probe of a table: the baseline triangle must draw clean ("diff: 0"), else the
target is fenced (a probe that hangs the GPU, whose recovery resets it) up to three times;
the probe runs (probe.py builds its cases, one process per case); its raw output, report and
assembled cases go to DATA/<unit>/<feature>/<probe>/, and the baseline after it into the
table's env.toml with the target's environment (kernel, firmware, tool). Then the table's
manifest, DATASETS/<unit>-<feature>.toml: the repository that holds the bytes (data or
data-private), the paths, files, size and sha256, and the table as its recipe.

Two table fields (top level, before the first [[probe]]/[[range]]):

    needs = ["kpoke", "render"]   what the target must offer, checked before anything runs:
                                  a name is a file of the laptop's debugfs dri/N/sgx/
                                  (kpoke, kreg, regs, timer_clock, ...), or "render", the
                                  render node (/dev/dri/renderD*). A missing one refuses the
                                  table, naming it. Targets without ssh (mock, local, build)
                                  are not checked.
    open = ["<probe name>", ...]  kept probes no earlier run recorded. In a probe table they
                                  run last, and the GPU is checked (fenced if dirty) after
                                  the last. Both lists go into the table's env.toml and its
                                  dataset manifest (after the recipe, needs then open).

    campaign.py [--target mock|laptop|local|build] --data DIR --datasets DIR [--plan FILE]
                [--repo REPO] PHASE|TABLE...
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools" / "usse-asm"))
sys.path.insert(0, str(ROOT / "tools" / "records"))
sys.path.insert(0, str(ROOT / "tools" / "sweep"))
import datasets  # noqa: E402
import probe  # noqa: E402
import sweep  # noqa: E402

# the hardware units: a table's directory
UNITS = ("platform", "firmware", "bif", "edm", "dpm", "vdm", "ta", "mte", "isp", "tsp", "pds",
         "usse", "texture", "pbe", "zls", "transfer", "render")
FENCES = 3
# Extra checks of every probe name, question, label and case, and of every sweep or script
# table: each takes the text and returns a complaint, or None. Empty here; a caller adds its own
# (tools/rewrite/kit_campaign.py plugs in the old-spelling scan).
CHECKS: list = []
FENCE_PROBE = "pbe-sideband-0000-32x16"
FIELDS = ("needs", "open")
_LIST_NEEDS = ("sudo -n sh -c 'ls /sys/kernel/debug/dri/*/sgx/' 2>/dev/null | sed 's|^|sgx/|'; "
               "ls /dev/dri 2>/dev/null | sed 's|^|dev/|'")


class CampaignError(Exception):
    pass


def _clean(line: str) -> bool:
    return line.startswith("diff: 0 ")


def _sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MockTarget:
    """A local sgxfive-test against its in-process mock."""
    name = "mock"

    def __init__(self, tool: pathlib.Path):
        self.tool = pathlib.Path(tool)

    def baseline(self) -> str:
        out = subprocess.run([str(self.tool), "--mock", "tri"], capture_output=True,
                             text=True).stdout
        return next((l for l in out.splitlines() if l.startswith("diff:")), "diff: none")

    def fence(self) -> None:
        pass

    def run(self, probes: list, work: pathlib.Path, src_dir: pathlib.Path) -> str:
        return probe.run_local(probes, [str(self.tool), "--mock"], work, src_dir)

    def sweep_exec(self):
        return sweep.LocalExec(self.tool, mock=True)

    def script(self, text: str, bins: pathlib.Path | None = None) -> str:
        raise CampaignError("script tables run on the laptop only")

    def environment(self) -> dict:
        return {"target": "mock", "tool_sha256": _sha(self.tool)}


STAGE = "sgxprobes-stage"      # the laptop directory a script's staged programs go to


def with_bins(text: str, rdir: str) -> str:
    """A script that finds its staged programs in $HOME/rdir as $SGXFIVE_PROBE_BINS."""
    return f'SGXFIVE_PROBE_BINS="$HOME/{rdir}"; export SGXFIVE_PROBE_BINS\n' + text


class LaptopTarget:
    """The laptop over ssh (probe.py's target: SGX_TARGET_HOST, SGX_TARGET_SSH_OPTS)."""
    name = "laptop"
    tool = "./sgxfive-test"

    def __init__(self):
        self.host, self.opts = probe.target()

    def _ssh(self, cmd: str) -> str:
        return subprocess.run(["ssh", *self.opts, self.host, cmd], capture_output=True,
                              text=True, timeout=600).stdout

    def baseline(self) -> str:
        out = self._ssh(f"sudo -n {self.tool} tri 2>&1 | grep '^diff'").strip()
        return out or "diff: none"

    def fence(self) -> None:
        (fp,) = [p for p in probe.load() if p.name == FENCE_PROBE]
        with tempfile.TemporaryDirectory() as d:
            try:
                probe.run_remote([fp], pathlib.Path(d))
            except probe.ProbeError:
                pass                # the fence hangs on purpose

    def run(self, probes: list, work: pathlib.Path, src_dir: pathlib.Path) -> str:
        return probe.run_remote(probes, work, src_dir)

    def sweep_exec(self):
        return sweep.SshExec()

    def script(self, text: str, bins: pathlib.Path | None = None) -> str:
        """Run a script in the laptop's home directory (as the hand-run scripts do); the
        programs in bins, if any, are copied to STAGE first and the script finds them there."""
        try:
            if bins is not None:
                for cmd in (["ssh", *self.opts, self.host, f"rm -rf {STAGE} && mkdir {STAGE}"],
                            ["scp", "-q", *self.opts, *map(str, sorted(bins.iterdir())),
                             f"{self.host}:{STAGE}/"]):
                    subprocess.run(cmd, check=True)
                text = with_bins(text, STAGE)
            r = subprocess.run(["ssh", *self.opts, self.host, "sh -s"], input=text,
                               capture_output=True, text=True, timeout=7200)
        except subprocess.CalledProcessError as err:
            raise CampaignError(f"{err.cmd[0]} to {self.host} failed (exit {err.returncode})")
        except subprocess.TimeoutExpired:
            raise CampaignError(f"script on {self.host} timed out")
        if r.returncode:
            tail = (r.stdout + r.stderr).strip().splitlines()[-5:]
            raise CampaignError(f"script on {self.host} failed (exit {r.returncode}): "
                                + " | ".join(tail))
        return r.stdout + r.stderr

    def environment(self) -> dict:
        q = shlex.quote
        cmds = {"kernel": "uname -r",
                "module_srcversion": "modinfo -F srcversion gma500_gfx",
                "debug_option": "sudo -n sh -c 'ls /sys/kernel/debug/dri/*/sgx/regs' "
                                ">/dev/null 2>&1 && echo yes || echo no",
                "tool_sha256": f"sha256sum {q(self.tool)} 2>/dev/null | cut -d' ' -f1",
                "firmware_sha256": "sha256sum /lib/firmware/sgx545_ukernel.fw 2>/dev/null | "
                                   "cut -d' ' -f1",
                "board": "cat /sys/class/dmi/id/product_name"}
        # the kernel fork's branch commit the module was built from: the operator states it
        env = {"target": "laptop", "host": self.host,
               "kernel_commit": os.environ.get("RESGX545_KERNEL_COMMIT", "")}
        for k, c in cmds.items():
            env[k] = self._ssh(c).strip()
        return env


class LocalHost:
    """Runs a capture script on this machine (cutting the firmware from the user's copy)."""
    name = "local"
    in_repository = True        # a script table runs here, in the repository root

    def script(self, text: str, root: pathlib.Path, out: pathlib.Path) -> str:
        """Run a script table's script in the repository root, its extra files going to the
        table's directory ($OUT)."""
        r = subprocess.run(["sh", "-s"], input=text, cwd=root, capture_output=True, text=True,
                           timeout=7200,
                           env={**os.environ, "OUT": str(pathlib.Path(out).resolve())})
        if r.returncode:
            raise CampaignError(f"script failed (exit {r.returncode}): {r.stderr.strip()}")
        return r.stdout

    def capture(self, script: str, files: list[str], root: pathlib.Path,
                out: pathlib.Path) -> str:
        _unique_names(files, "capture")
        with tempfile.TemporaryDirectory() as d:
            work = pathlib.Path(d)
            for f in files:
                shutil.copy2(root / f, work / pathlib.Path(f).name)
            r = subprocess.run(["sh", "-s"], input=script, cwd=work, capture_output=True,
                               text=True, timeout=7200,
                               env={**os.environ, "OUT": str(pathlib.Path(out).resolve())})
        if r.returncode:
            raise CampaignError(f"capture failed (exit {r.returncode}): {r.stderr.strip()}")
        return r.stdout

    def environment(self) -> dict:
        return {"target": "local", "uname": " ".join(os.uname())}


class BuildHost:
    """Runs a capture script on the build machine over ssh (x86-64 Linux with 32-bit
    userspace, or the i686 laptop, for the closed i386 libraries under the harness);
    $RESGX545_BUILD_HOST, with $RESGX545_BUILD_SSH_OPTS (e.g. a host-key alias)."""
    name = "build"

    def __init__(self, host: str | None = None):
        self.host = host or os.environ.get("RESGX545_BUILD_HOST", "")
        self.opts = shlex.split(os.environ.get("RESGX545_BUILD_SSH_OPTS", ""))
        if not self.host:
            raise CampaignError("no build host: set RESGX545_BUILD_HOST")

    def _run(self, cmd: list[str], **kw) -> subprocess.CompletedProcess:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=7200, **kw)

    def _scp(self, cmd: list[str], what: str) -> None:
        r = self._run(cmd)
        if r.returncode:
            raise CampaignError(f"{what} on {self.host} failed (exit {r.returncode}): "
                                f"{r.stderr.strip()}")

    def _sh(self, cmd: str, **kw) -> subprocess.CompletedProcess:
        """A command on the build host, under sh whatever its login shell."""
        return self._run(["ssh", *self.opts, self.host, f"sh -c {shlex.quote(cmd)}"], **kw)

    def capture(self, script: str, files: list[str], root: pathlib.Path,
                out: pathlib.Path) -> str:
        _unique_names(files, "capture")
        w = self._sh("mktemp -d").stdout.strip()
        if not w.startswith("/"):
            raise CampaignError(f"{self.host}: no work directory")
        try:
            if files:
                self._scp(["scp", *self.opts, "-q", *[str(root / f) for f in files],
                           f"{self.host}:{w}/"], "upload")
            r = self._sh(f"cd {shlex.quote(w)} && mkdir -p out && OUT={shlex.quote(w)}/out sh -s",
                         input=script)
            if r.returncode:
                raise CampaignError(f"capture failed on {self.host} (exit {r.returncode}): "
                                    f"{r.stderr.strip()}")
            pathlib.Path(out).mkdir(parents=True, exist_ok=True)
            self._scp(["scp", *self.opts, "-q", "-r", f"{self.host}:{w}/out/.", str(out)],
                      "download")
            return r.stdout
        finally:
            self._sh(f"rm -rf {shlex.quote(w)}")

    def environment(self) -> dict:
        return {"target": "build", "host": self.host,
                "uname": self._sh("uname -srm").stdout.strip()}


def _unique_names(files: list[str], where: str) -> None:
    """A capture's files are copied by basename: two with one name would collide."""
    names = [pathlib.Path(f).name for f in files]
    dup = sorted({n for n in names if names.count(n) > 1})
    if dup:
        raise CampaignError(f"{where}: files share the name {', '.join(dup)}")


def _local_tool() -> pathlib.Path:
    """The local sgxfive-test: its sizes of each job's spaces (the sweep cases)."""
    return ROOT / "userspace/libsgxfive/build/sgxfive-test"


def _check(path: pathlib.Path, root: pathlib.Path, table: list) -> tuple[str, str]:
    rel = path.relative_to(root).as_posix()
    m = re.fullmatch(r"(probes|captures)/([^/]+)/([^/]+)\.toml", rel)
    if not m:
        raise CampaignError(f"{rel}: not probes/<unit>/<feature>.toml or captures/...")
    _top, unit, feature = m.groups()
    if unit not in UNITS:
        raise CampaignError(f"{rel}: unit {unit} is not one of {', '.join(UNITS)}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", feature):
        raise CampaignError(f"{rel}: feature {feature} is not lowercase words and hyphens")
    for p in table:
        if not re.fullmatch(rf"{unit}-{feature}-[a-z0-9]+(-[a-z0-9]+)*", p.name):
            raise CampaignError(f"{rel}: probe {p.name} is not named {unit}-{feature}-<case>")
        for text in (p.name, p.question, *p.labels, *(str(c) for c in p.cases)):
            _extra(f"{rel}: probe {p.name}", text)
    return unit, feature


def _extra(where: str, text: str) -> None:
    for check in CHECKS:
        msg = check(text)
        if msg:
            raise CampaignError(f"{where}: {msg}")


def _toml_value(v) -> str:
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, list):
        return "[" + ", ".join(_toml_value(x) for x in v) + "]"
    return str(v)


def _write_env(path: pathlib.Path, env: dict, probes: dict) -> None:
    lines = [f"{k} = {_toml_value(v)}" for k, v in env.items()]
    for name, rec in probes.items():
        lines += ["", f'[probes."{name}"]'] + [f"{k} = {_toml_value(v)}" for k, v in rec.items()]
    path.write_text("\n".join(lines) + "\n")


def table_fields(spec: dict, name: str) -> dict:
    """{needs: [...], open: [...]} of a table (only the fields it has)."""
    out = {}
    for k in FIELDS:
        if k in spec:
            v = spec[k]
            if not (isinstance(v, list) and all(isinstance(x, str) for x in v)):
                raise CampaignError(f"{name}: {k} is a list of names, not {v!r}")
            out[k] = v
    return out


def check_needs(target, needs: list, where: str) -> None:
    """Refuse a table whose needs the target lacks (targets with an ssh executor only)."""
    if not needs or not hasattr(target, "_ssh"):
        return
    debugfs, nodes = set(), set()
    for line in target._ssh(_LIST_NEEDS).split():
        kind, _, name = line.partition("/")
        (debugfs if kind == "sgx" else nodes).add(name)
    missing = [n for n in needs
               if not (any(x.startswith("renderD") for x in nodes) if n == "render"
                       else n in debugfs)]
    if missing:
        raise CampaignError(
            f"{where}: needs {', '.join(missing)}, which the {target.name} target lacks "
            f"(debugfs there: {', '.join(sorted(debugfs)) or 'none'}; "
            f"nodes: {', '.join(sorted(nodes)) or 'none'})")


def _ready(target) -> str:
    """The baseline line once clean, fencing a dirty target up to FENCES times."""
    line = target.baseline()
    for _ in range(FENCES):
        if _clean(line):
            return line
        target.fence()
        line = target.baseline()
    if not _clean(line):
        raise CampaignError(f"baseline still dirty after {FENCES} fences: {line}")
    return line


def run_table(path: pathlib.Path, target, data: pathlib.Path, ds_dir: pathlib.Path,
              repo: str, root: pathlib.Path | None = None) -> dict:
    """Run every probe of one table; returns (and writes) its dataset manifest."""
    path = pathlib.Path(path).resolve()
    root = pathlib.Path(root).resolve() if root else path.parents[2]
    text = path.read_text()
    spec = tomllib.loads(text)
    kind = spec.get("kind") if spec.get("kind") == "capture" else None
    has_probe = "probe" in spec
    has_sweep = kind != "capture" and ("range" in spec or "sweep" in spec)
    has_script = kind != "capture" and ("script" in spec or spec.get("kind") == "script")
    if kind is None and not (has_probe or has_sweep or has_script):
        raise CampaignError(f"{path}: not a probe, sweep, script or capture table")
    if (has_script or kind == "capture") and "script" not in spec:
        raise CampaignError(f"{path.name}: a script or capture table names its `script`")
    if not hasattr(target, "baseline") and (
            has_probe or has_sweep or (has_script and spec.get("baseline", "tri") == "tri")):
        raise CampaignError(f"{path.name}: the {target.name} target has no GPU; only a "
                            "script table with baseline = \"none\" or a capture runs there")
    if ("captures" in path.relative_to(root).parts[:1]) != (kind == "capture") \
            or (kind == "capture" and repo != "data-private"):
        raise CampaignError(f"{path.name}: captures (of the closed stack) are private: "
                            "captures/<unit>/, repo data-private")
    table = probe.load(path) if has_probe else []
    fields = table_fields(spec, path.name)
    opened = fields.get("open", [])
    absent = [n for n in opened if has_probe and n not in {p.name for p in table}]
    if absent:
        raise CampaignError(f"{path.name}: open names no probe of the table: "
                            f"{', '.join(absent)}")
    # the open probes (kept, never run by the notebook) run last
    table = [p for p in table if p.name not in opened] + [p for p in table if p.name in opened]
    unit, feature = _check(path, root, table)
    check_needs(target, fields.get("needs", []), path.name)
    if kind == "capture" or has_sweep or has_script:
        name = spec.get("name", "")
        if name != f"{unit}-{feature}":
            raise CampaignError(f"{path.name}: a table of sweeps, a script or a capture is "
                                f"named {unit}-{feature}, not {name!r}")
        _extra(path.name, text)
    src_dir = path.parent / "templates"
    src_dir = src_dir if src_dir.is_dir() else probe.PROBES_DIR
    tdir = pathlib.Path(data) / unit / feature
    tdir.mkdir(parents=True, exist_ok=True)
    env = {**target.environment(), **fields, "table": path.relative_to(root).as_posix(),
           "date": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
    log: dict = {}
    if kind == "capture":
        if not hasattr(target, "capture"):
            raise CampaignError(f"{path.name}: a capture runs on a capture host "
                                "(local or build), not a GPU target")
        script = spec["script"]
        body = (path.parent / "templates" / script).read_text()
        (tdir / "output.txt").write_text(target.capture(body, spec.get("files", []), root,
                                                        tdir))
        (tdir / script).write_text(body)
        _write_env(tdir / "env.toml", env, {spec["name"]: {}})
    if has_sweep:
        sweeps = sweep.load_all(path)
        for s in sweeps:
            # one sweep: the table's directory; several: one directory each (the name's tail)
            sdir = tdir if len(sweeps) == 1 else tdir / s.name.removeprefix(f"{unit}-{feature}-")
            before = _ready(target)
            res = sweep.run(s, target.sweep_exec(), sdir, sweep.tool_size_of(_local_tool()))
            if res.stopped or res.done < res.total:
                raise CampaignError(f"{path.name}: sweep {s.name} did not finish "
                                    f"({res.done} of {res.total} cases"
                                    f"{'; ' + res.stopped if res.stopped else ''}); "
                                    "no manifest")
            log[s.name] = {"before": before, "after": target.baseline()}
            _write_env(tdir / "env.toml", env, log)
        (tdir / "table.toml").write_text(text)
    if has_script:
        baseline = spec.get("baseline", "tri")
        if baseline not in ("tri", "none"):
            raise CampaignError(f"{path.name}: baseline is \"tri\" (the default) or "
                                f"\"none\", not {baseline!r}")
        before = _ready(target) if baseline == "tri" else None
        body = (path.parent / "templates" / spec["script"]).read_text()
        with tempfile.TemporaryDirectory() as bins:
            staged = _stage(table, spec.get("stage", []), root, src_dir, pathlib.Path(bins))
            if getattr(target, "in_repository", False):
                out = target.script(body, root, tdir)
            elif staged:
                out = target.script(body, bins=pathlib.Path(bins))
            else:
                out = target.script(body)
        (tdir / "output.txt").write_text(out)
        (tdir / spec["script"]).write_text(body)
        log[spec["name"]] = ({"before": before, "after": target.baseline()}
                             if baseline == "tri" else {"baseline": "none"})
        _write_env(tdir / "env.toml", env, log)
    for p in table:
        before = _ready(target)
        with tempfile.TemporaryDirectory() as d:
            work = pathlib.Path(d)
            out = target.run([p], work, src_dir)
            pdir = tdir / p.name
            pdir.mkdir(parents=True, exist_ok=True)
            (pdir / "raw.txt").write_text(out)
            (pdir / "report.txt").write_text(probe.report([p], out))
            probe.save_bins(work, pdir)
            probe.save_dumps(work, pdir)
        log[p.name] = {"before": before, "after": target.baseline()}
        _write_env(tdir / "env.toml", env, log)
    if opened and has_probe:
        _ready(target)              # the last open probe may have wedged the GPU
    rel = f"{unit}/{feature}/"
    files, size, sha = datasets.digest([rel], pathlib.Path(data))
    kinds = [k for k, on in (("capture", kind == "capture"), ("sweep", has_sweep),
                             ("script", has_script), ("probe", has_probe)) if on]
    title = " and ".join(filter(None, (", ".join(kinds[:-1]), kinds[-1])))
    rec = {"title": f"{title} table {unit}/{feature}", "repo": repo, "paths": [rel],
           "method": f"campaign runner on the {target.name} target (tools/campaign)",
           "date": env["date"][:10], "files": files, "size": size, "sha256": sha,
           "recipe": path.relative_to(root).as_posix(), **fields}
    pathlib.Path(ds_dir).mkdir(parents=True, exist_ok=True)
    (pathlib.Path(ds_dir) / f"{unit}-{feature}.toml").write_text(
        "\n".join(f"{k} = {_toml_value(v)}" for k, v in rec.items()) + "\n")
    return rec


def _stage(table: list, stage: list, root: pathlib.Path, src_dir: pathlib.Path,
           out: pathlib.Path) -> bool:
    """Build, for a script that runs probe programs by hand, the programs of its own table's
    probes and of the tables it names in `stage` ("<unit>/<feature>"), with their helpers,
    into out; whether there was anything to build."""
    groups = [(table, src_dir)]
    for name in stage:
        t = root / "probes" / f"{name}.toml"
        groups.append((probe.load(t), t.parent / "templates"))
    for ps, src in groups:
        for p in ps:
            probe.build(p, out, src)
            probe.build_helpers([p], out, src)
    return any(out.iterdir())


def load_plan(path: pathlib.Path) -> list[tuple[int, str]]:
    """campaign.toml: [[phase]] number = N, tables = [...] -> [(phase, table)] in phase order."""
    t = tomllib.loads(pathlib.Path(path).read_text())
    return [(ph["number"], tb) for ph in sorted(t.get("phase", []), key=lambda x: x["number"])
            for tb in ph["tables"]]


def select(plan: list, args: list[str]) -> list[tuple[int, str]]:
    """The plan's entries named by phase numbers or table paths."""
    return [(n, t) for n, t in plan if str(n) in args or t in args]


def unknown(plan: list, args: list[str]) -> list[str]:
    """The arguments that name no phase and no table of the plan."""
    return [a for a in args if not any(str(n) == a or t == a for n, t in plan)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", default="mock", choices=("mock", "laptop", "local", "build"))
    ap.add_argument("--tool", default=str(ROOT / "userspace/libsgxfive/build/sgxfive-test"))
    ap.add_argument("--data", required=True)
    ap.add_argument("--datasets", required=True)
    ap.add_argument("--plan", default=None)
    ap.add_argument("--repo", default="data", choices=("data", "data-private"))
    ap.add_argument("what", nargs="+")
    a = ap.parse_args(argv)
    target = {"mock": lambda: MockTarget(pathlib.Path(a.tool)), "local": LocalHost,
              "build": BuildHost, "laptop": LaptopTarget}[a.target]
    root = pathlib.Path(a.plan).resolve().parent if a.plan else None
    t = None
    try:
        target = target()
        if a.plan:
            plan = load_plan(pathlib.Path(a.plan))
            if unknown(plan, a.what):
                raise CampaignError("nothing in the plan is named "
                                    + ", ".join(unknown(plan, a.what)))
            tables = [t for _, t in select(plan, a.what)]
        else:
            tables = a.what
        for t in tables:
            p = (root / t) if root else pathlib.Path(t)
            rec = run_table(p, target, pathlib.Path(a.data), pathlib.Path(a.datasets), a.repo,
                            root)
            print(f"{rec['recipe']}: {rec['files']} files, {rec['size']} bytes")
    except CampaignError as err:
        print(f"campaign.py: {err}", file=sys.stderr)
        return 1
    except (probe.ProbeError, sweep.SweepError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired, tomllib.TOMLDecodeError, OSError) as err:
        # a table that fails stops the run: the tables after it would sit on its state
        print(f"campaign.py: {t}: {type(err).__name__}: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
