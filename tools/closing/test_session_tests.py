# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""session_tests.sh: re-run a published closing session's own tests from a copy, laid out as
the session was run (siblings under scratch/resgx545/closing*, a fake HOME holding the pinned
resgx545 tree), without touching the data repository. Built on a toy tool repository and a toy
data repository."""
import hashlib
import os
import pathlib
import subprocess

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parent / "session_tests.sh"
V1, V2 = "VALUE = 1\n", "VALUE = 2\n"
GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def git(cwd, *args):
    return subprocess.run([*GIT, *args], cwd=cwd, check=True, capture_output=True,
                          text=True).stdout.strip()


RUN_ALL = """#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
[ -d debug ] || { echo "no debug dir"; exit 1; }
[ -n "$PY" ] || { echo "no PY"; exit 1; }
[ "$TOOL_SRC" = "$HOME/src/resgx545" ] || { echo "TOOL_SRC $TOOL_SRC"; exit 1; }
[ "$RESGX545_MAIN" = "$HOME/src/resgx545" ] || { echo "RESGX545_MAIN"; exit 1; }
[ "$RESGX545_DATA" = "$HOME/src/resgx545-data" ] || { echo "RESGX545_DATA"; exit 1; }
[ "$(cat "$HOME/src/resgx545/tools/x.py")" = "VALUE = 1" ] || { echo "tool not pinned"; exit 1; }
[ -f ../../closing/sib/marker ] || { echo "no sibling"; exit 1; }
[ -f "$HOME/src/scratch/resgx545/closing/sib/marker" ] || { echo "no sibling by HOME"; exit 1; }
for g in closing closing2 closing3; do
    [ -x ../../$g/pixel-faults/.venv/bin/python ] || { echo "no scratch python in $g"; exit 1; }
done
if [ -n "$DEMO_BUILT" ]; then
    [ -d "$HOME/src/resgx545/target" ] || { echo "no target"; exit 1; }
    echo session-build > "$HOME/src/resgx545/target/built-by-session"
    grep -q "$HOME/src/resgx545/crates/c" debug/demo/Cargo.toml \\
        || { echo "debug-src path"; exit 1; }
    [ -f debug/demo/src/main.rs ] || { echo "debug-src tree"; exit 1; }
fi
shasum -a 256 -c FROZEN.sha256 --quiet || { echo "freeze"; exit 1; }
echo "RUN_ALL PASSED"
exit ${DEMO_RC:-0}
"""


@pytest.fixture()
def world(tmp_path):
    tool = tmp_path / "tool"
    (tool / "tools").mkdir(parents=True)
    git(tool, "init", "-q")
    (tool / "tools/x.py").write_text(V1)
    git(tool, "add", ".")
    git(tool, "commit", "-qm", "v1")
    c1 = git(tool, "rev-parse", "HEAD")
    (tool / "tools/x.py").write_text(V2)
    git(tool, "commit", "-qam", "v2")
    (tool / ".gitignore").write_text("/target/\n")
    (tool / "target").mkdir()
    (tool / "target/marker").write_text("built")
    data = tmp_path / "data"
    s = data / "edm/closing-demo"
    (s / "tests").mkdir(parents=True)
    (s / "tests/run_all.sh").write_text(RUN_ALL)
    (s / "FROZEN.sha256").write_text(
        f"{sha(RUN_ALL)}  tests/run_all.sh\n"
        f"{sha(V1)}  /Users/someone/src/resgx545/tools/x.py\n")
    (s / "FROZEN.commits").write_text(
        "# header\n" f"{sha(V1)}  {c1}  tools/x.py\n")
    (s / "debug-src/demo/src").mkdir(parents=True)
    (s / "debug-src/demo/src/main.rs").write_text("fn main() {}\n")
    (s / "debug-src/demo/Cargo.toml").write_text(
        '[dependencies]\nc = { path = "/Users/someone/src/resgx545/crates/c" }\n')
    sib = data / "edm/closing-sib"
    sib.mkdir(parents=True)
    (sib / "marker").write_text("m")
    nt = data / "edm/closing-notests"
    nt.mkdir()
    (nt / "README.md").write_text("x")
    py = tmp_path / "py"
    py.write_text('#!/bin/sh\nexec python3 "$@"\n')
    py.chmod(0o755)
    return tool, data, py


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() if p.is_file() else None
            for p in sorted(root.rglob("*"))}


def run(world, session, **extra):
    tool, data, py = world
    env = {**os.environ, "RESGX545_TOOL": str(tool), "RESGX545_DATA": str(data), "PY": str(py),
           "RESGX545_SESSION_TARGET": str(tool.parent / "session-target")}
    env.update(extra)
    return subprocess.run(["bash", str(SCRIPT), session], env=env, capture_output=True,
                          text=True, timeout=120)


def test_script_is_valid_bash_and_executable():
    assert os.access(SCRIPT, os.X_OK)
    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)


def test_passing_session_reports_pass_and_exit_zero(world):
    r = run(world, "edm/closing-demo")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RUN_ALL PASSED" in r.stdout
    assert "session_tests: edm/closing-demo PASS (exit 0)" in r.stdout


def test_data_repository_is_never_modified(world):
    before = snapshot(world[1])
    run(world, "edm/closing-demo")
    assert snapshot(world[1]) == before


def test_failing_session_reports_its_exit_code(world):
    r = run(world, "edm/closing-demo", DEMO_RC="3")
    assert r.returncode == 3
    assert "session_tests: edm/closing-demo FAIL (exit 3)" in r.stdout


def test_scratch_is_removed_and_no_worktree_is_left(world):
    r = run(world, "edm/closing-demo")
    assert r.returncode == 0
    assert git(world[0], "worktree", "list").count("\n") == 0


def test_unknown_session_and_session_without_tests_exit_two(world):
    for name in ("edm/closing-nope", "edm/closing-notests"):
        r = run(world, name)
        assert r.returncode == 2, name
        assert "session_tests:" in r.stderr


def test_run_mock_is_the_entry_when_there_is_no_run_all(world):
    s = world[1] / "edm/closing-demo/tests"
    (s / "run_all.sh").rename(s / "run_mock.sh")
    (s.parent / "FROZEN.sha256").write_text(
        f"{sha(V1)}  /Users/someone/src/resgx545/tools/x.py\n")
    r = run(world, "edm/closing-demo")
    assert "RUN_ALL PASSED" in r.stdout


def test_build_products_and_debug_src_are_laid_out(world):
    r = run(world, "edm/closing-demo", DEMO_BUILT="1")
    assert r.returncode == 0, r.stdout + r.stderr
    assert not (world[0] / "target/debug").exists()


def test_builds_go_to_the_runner_target_never_the_main_checkout(world):
    """A pinned tool built into the main checkout's target/ replaces its binaries with old
    ones (and a library rewritten in place kills the next process that loads it on macOS):
    the worktree's target/ is the runner's own."""
    tool = world[0]
    before = snapshot(tool / "target")
    r = run(world, "edm/closing-demo", DEMO_BUILT="1")
    assert r.returncode == 0, r.stdout + r.stderr
    assert snapshot(tool / "target") == before
    assert (tool.parent / "session-target/built-by-session").read_text() == "session-build\n"


def test_the_simulator_is_built_from_the_pinned_tree(world, tmp_path):
    """The sessions' scripts run target/release/sgx-sim or target/debug/sgx-sim; the runner
    builds both from the pinned tree, in the runner's target, before the tests run."""
    tool, data = world[0], world[1]
    branch = git(tool, "rev-parse", "--abbrev-ref", "HEAD")
    pin = data / "edm/closing-demo/FROZEN.commits"
    c1 = pin.read_text().split()[-2]
    git(tool, "checkout", "-q", c1)
    (tool / "crates/sgx-sim").mkdir(parents=True)
    (tool / "crates/sgx-sim/Cargo.toml").write_text("[package]\n")
    git(tool, "add", "crates")
    git(tool, "commit", "-qm", "sim")
    pin.write_text(pin.read_text().replace(c1, git(tool, "rev-parse", "HEAD")))
    git(tool, "checkout", "-q", branch)
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    log = tmp_path / "cargo.log"
    (bin_ / "cargo").write_text(f'#!/bin/sh\necho "$PWD $*" >> {log}\n')
    (bin_ / "cargo").chmod(0o755)
    r = run(world, "edm/closing-demo", PATH=f"{bin_}:{os.environ['PATH']}")
    assert r.returncode == 0, r.stdout + r.stderr
    lines = log.read_text().splitlines()
    assert sorted(x.split(" ", 1)[1] for x in lines) == \
        ["build -q --release --workspace --bins", "build -q --workspace --bins"]
    assert all(x.split(" ", 1)[0].endswith("/src/resgx545") for x in lines)


def test_the_worktree_is_the_commit_of_the_frozen_tool_source(world):
    """A session's TOOLSRC.sha256 pins the tool source it deployed; the worktree is the newest
    commit holding exactly those files (the FROZEN.commits pins still overlaid on it)."""
    tool, data = world[0], world[1]
    src = tool / "userspace/t.c"
    src.parent.mkdir(parents=True)
    for v in ("one\n", "two\n", "three\n"):
        src.write_text(v)
        git(tool, "add", "userspace")
        git(tool, "commit", "-qm", v.strip())
    s = data / "edm/closing-demo"
    (s / "TOOLSRC.sha256").write_text(f"{sha('two' + chr(10))}  userspace/t.c\n")
    frozen = (s / "FROZEN.sha256").read_text()
    run_all = s / "tests/run_all.sh"
    run_all.write_text(run_all.read_text().replace(
        'echo "RUN_ALL PASSED"',
        '[ "$(cat "$HOME/src/resgx545/userspace/t.c")" = two ] || { echo "toolsrc"; exit 1; }\n'
        'echo "RUN_ALL PASSED"'))
    (s / "FROZEN.sha256").write_text(frozen.replace(sha(RUN_ALL), sha(run_all.read_text())))
    r = run(world, "edm/closing-demo")
    assert r.returncode == 0, r.stdout + r.stderr


def test_sibling_sources_are_put_beside_the_session(world):
    """Files a session read from scratch directories outside it are published in its
    sibling-src/<dir>/; the runner puts each <dir> beside the copy, where the tests read it."""
    s = world[1] / "edm/closing-demo"
    (s / "sibling-src/kernel").mkdir(parents=True)
    (s / "sibling-src/kernel/layout.out").write_text("sizes\n")
    run_all = s / "tests/run_all.sh"
    frozen = (s / "FROZEN.sha256").read_text()
    run_all.write_text(run_all.read_text().replace(
        'echo "RUN_ALL PASSED"',
        '[ "$(cat ../kernel/layout.out)" = sizes ] || { echo "sibling-src"; exit 1; }\n'
        'echo "RUN_ALL PASSED"'))
    (s / "FROZEN.sha256").write_text(frozen.replace(sha(RUN_ALL), sha(run_all.read_text())))
    r = run(world, "edm/closing-demo")
    assert r.returncode == 0, r.stdout + r.stderr


def test_pins_of_a_tree_under_scratch_are_pointed_at_the_pinned_tree(world):
    """A session frozen against an integration worktree under scratch/resgx545/ (round 4's
    closing4/lead/wt) pins its files by an absolute path whose first resgx545 component is
    the scratch tree, not the tool tree; FROZEN.commits names them relative to the tree. The
    runner points each such pin at the pinned worktree by its FROZEN.commits path."""
    s = world[1] / "edm/closing-demo"
    (s / "FROZEN.sha256").write_text(
        f"{sha(RUN_ALL)}  tests/run_all.sh\n"
        f"{sha(V1)}  /Users/someone/src/scratch/resgx545/closing4/lead/wt/tools/x.py\n")
    r = run(world, "edm/closing-demo")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RUN_ALL PASSED" in r.stdout


def test_a_frozen_list_of_the_freezes_own_paths_moves_with_them(world):
    """A session whose generator writes the list of the files it read outside the session (R4-G's
    gen/data/sources.lst: absolute resgx545 and resgx545-data paths, each also a line of the
    freeze) freezes that list too. The copy's freeze points those paths at the fake home, so the
    list is pointed there the same way and its hash line follows; the freeze still verifies and
    the list names the fake home's files."""
    s = world[1] / "edm/closing-demo"
    (world[1] / "edm/closing-sib/data.txt").write_text("D\n")
    lst = ("/Users/someone/src/resgx545-data/edm/closing-sib/data.txt\n"
           "/Users/someone/src/resgx545/tools/x.py\n")
    (s / "gen").mkdir()
    (s / "gen/sources.lst").write_text(lst)
    run_all = RUN_ALL.replace(
        'echo "RUN_ALL PASSED"',
        'while read -r p; do [ -f "$p" ] || { echo "listed $p"; exit 1; }\n'
        '    case "$p" in "$HOME"/src/*) ;; *) echo "not moved $p"; exit 1 ;; esac\n'
        'done < gen/sources.lst\necho "RUN_ALL PASSED"')
    (s / "tests/run_all.sh").write_text(run_all)
    (s / "FROZEN.sha256").write_text(
        f"{sha(run_all)}  tests/run_all.sh\n"
        f"{sha(lst)}  gen/sources.lst\n"
        f"{sha('D' + chr(10))}  /Users/someone/src/resgx545-data/edm/closing-sib/data.txt\n"
        f"{sha(V1)}  /Users/someone/src/resgx545/tools/x.py\n")
    r = run(world, "edm/closing-demo")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RUN_ALL PASSED" in r.stdout
    assert (s / "gen/sources.lst").read_text() == lst


def test_frozen_scratch_inputs_are_read_from_their_published_copies(world, tmp_path):
    """A session that froze inputs it read from scratch outside every tree (round 5's
    r5-events: the plan, the decisions, and readings of the firmware) names them by absolute
    path under scratch/resgx545/, with no FROZEN.commits pin. Each is published as
    cited/<path> of resgx545-data or, derived from the firmware, of resgx545-data-private: the
    runner puts the copy at its scratch place and points the freeze there."""
    s = world[1] / "edm/closing-demo"
    (world[1] / "cited/closing5/events").mkdir(parents=True)
    (world[1] / "cited/closing5/events/plan.md").write_text("P\n")
    priv = tmp_path / "data-private"
    (priv / "cited/closing5/r6").mkdir(parents=True)
    (priv / "cited/closing5/r6/reading.md").write_text("R\n")
    run_all = RUN_ALL.replace(
        'echo "RUN_ALL PASSED"',
        '[ "$(cat ../../closing5/events/plan.md)" = P ] || { echo "plan"; exit 1; }\n'
        'echo "RUN_ALL PASSED"')
    (s / "tests/run_all.sh").write_text(run_all)
    (s / "FROZEN.sha256").write_text(
        f"{sha(run_all)}  tests/run_all.sh\n"
        f"{sha(V1)}  /Users/someone/src/resgx545/tools/x.py\n"
        f"{sha('P' + chr(10))}  /Users/someone/src/scratch/resgx545/closing5/events/plan.md\n"
        f"{sha('R' + chr(10))}  /Users/someone/src/scratch/resgx545/closing5/r6/reading.md\n")
    r = run(world, "edm/closing-demo", RESGX545_DATA_PRIVATE=str(priv))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RUN_ALL PASSED" in r.stdout
    # without the private copy the freeze does not verify: no silent pass
    r = run(world, "edm/closing-demo", RESGX545_DATA_PRIVATE=str(tmp_path / "absent"))
    assert r.returncode != 0
    assert "freeze" in r.stdout


def test_lines_that_name_their_repository_pin_only_the_tool_tree(world):
    """R5-dpm's FROZEN.commits names the repository of each line (`resgx545:PATH`, and
    `linux:PATH`, `data:PATH` with commits of other repositories): the tool tree is pinned by
    its resgx545 lines, and the other lines neither choose the worktree's commit nor stop it."""
    tool, data = world[0], world[1]
    c1 = git(tool, "rev-list", "--max-parents=0", "HEAD")
    s = data / "edm/closing-demo"
    (s / "FROZEN.commits").write_text(
        "# header\n"
        f"{sha(V1)}  {c1}  resgx545:tools/x.py\n"
        f"{sha('k')}  {'a' * 40}  linux:drivers/k.c\n"
        f"{sha('d')}  {'b' * 40}  data:edm/closing-sib/marker\n")
    r = run(world, "edm/closing-demo")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RUN_ALL PASSED" in r.stdout


def test_a_data_view_shows_an_area_as_the_freeze_saw_it(world):
    """A session whose generator scans an area of the data repository (r5-render4x's twins: every
    kept row of render/closing-*) reads more once it and later sessions are published, and its
    check that the generated files are as frozen then fails. postrun/data-view.txt lists, for an
    area, the sessions the freeze saw; the fake home's data repository then holds only those in
    that area (the session's own directory left out too) and every other entry whole."""
    data = world[1]
    s = data / "edm/closing-demo"
    (data / "edm/closing-later").mkdir()
    (data / "edm/closing-later/marker").write_text("l")
    (data / "render/closing-other").mkdir(parents=True)
    (s / "postrun").mkdir()
    (s / "postrun/data-view.txt").write_text("# the edm sessions the freeze saw\nedm/closing-sib\n")
    run_all = RUN_ALL.replace(
        'echo "RUN_ALL PASSED"',
        'D=$RESGX545_DATA\n'
        '[ -d "$D/edm/closing-later" ] && { echo "later seen"; exit 1; }\n'
        '[ -d "$D/edm/closing-demo" ] && { echo "self seen"; exit 1; }\n'
        '[ -d "$D/edm/closing-notests" ] && { echo "unlisted seen"; exit 1; }\n'
        '[ -f "$D/edm/closing-sib/marker" ] || { echo "listed missing"; exit 1; }\n'
        '[ -d "$D/render/closing-other" ] || { echo "other area missing"; exit 1; }\n'
        'echo "RUN_ALL PASSED"')
    (s / "tests/run_all.sh").write_text(run_all)
    frozen = (s / "FROZEN.sha256").read_text()
    (s / "FROZEN.sha256").write_text(frozen.replace(sha(RUN_ALL), sha(run_all)))
    before = snapshot(data)
    r = run(world, "edm/closing-demo")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RUN_ALL PASSED" in r.stdout
    assert snapshot(data) == before
    # without the file the data repository is linked whole, as before
    (s / "postrun/data-view.txt").unlink()
    r = run(world, "edm/closing-demo")
    assert "later seen" in r.stdout


def test_a_data_view_still_shows_the_data_commits_its_freeze_pins(world):
    """R6-dpm's freeze checks its data: pins with `git -C $RESGX545_DATA show COMMIT:PATH`, and
    its offline rules scan render/closing-*, so it needs a view and git at once. The view reads
    the data repository's objects (any pinned commit, the session's own later sessions included)
    through a repository of its own, so that nothing git does there writes the data repository."""
    data = world[1]
    git(data, "init", "-q")
    git(data, "add", ".")
    git(data, "commit", "-qm", "data")
    c = git(data, "rev-parse", "HEAD")
    s = data / "edm/closing-demo"
    (s / "postrun").mkdir()
    (s / "postrun/data-view.txt").write_text("edm/closing-sib\n")
    run_all = RUN_ALL.replace(
        'echo "RUN_ALL PASSED"',
        'D=$RESGX545_DATA\n'
        '[ -d "$D/edm/closing-notests" ] && { echo "unlisted seen"; exit 1; }\n'
        f'[ "$(git -C "$D" show {c}:edm/closing-sib/marker)" = m ] || {{ echo "no git"; exit 1; }}\n'
        'git -C "$D" status >/dev/null 2>&1\n'
        'echo "RUN_ALL PASSED"')
    (s / "tests/run_all.sh").write_text(run_all)
    frozen = (s / "FROZEN.sha256").read_text()
    (s / "FROZEN.sha256").write_text(frozen.replace(sha(RUN_ALL), sha(run_all)))
    before = snapshot(data)
    r = run(world, "edm/closing-demo")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RUN_ALL PASSED" in r.stdout
    assert snapshot(data) == before


def test_sessions_of_later_rounds_find_their_siblings_by_group(world):
    """R6-dpm's scorer test rescores R5-dpm's kept attempt as closing5/r5-dpm beside its own
    group: every published session is linked in the groups of rounds 4 to 6 as well."""
    s = world[1] / "edm/closing-demo"
    run_all = RUN_ALL.replace(
        'echo "RUN_ALL PASSED"',
        'for g in closing4 closing5 closing6; do\n'
        '    [ -f ../../$g/sib/marker ] || { echo "no sibling in $g"; exit 1; }\n'
        'done\n'
        'echo "RUN_ALL PASSED"')
    (s / "tests/run_all.sh").write_text(run_all)
    frozen = (s / "FROZEN.sha256").read_text()
    (s / "FROZEN.sha256").write_text(frozen.replace(sha(RUN_ALL), sha(run_all)))
    r = run(world, "edm/closing-demo")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RUN_ALL PASSED" in r.stdout


def test_firmware_derived_files_of_the_session_come_from_the_private_copy(world, tmp_path):
    """r6-held froze its O3 oracle (private/o3/, derived from the firmware) by relative path;
    the published session leaves it out and resgx545-data-private holds it as
    cited/closingN/<name>/<path>. The runner puts the copy back in the session's place; without
    it the freeze fails."""
    s = world[1] / "edm/closing-demo"
    priv = tmp_path / "data-private"
    (priv / "cited/closing6/demo/private/o3").mkdir(parents=True)
    (priv / "cited/closing6/demo/private/o3/RESULT.md").write_text("O\n")
    frozen = (s / "FROZEN.sha256").read_text()
    (s / "FROZEN.sha256").write_text(frozen + f"{sha('O' + chr(10))}  private/o3/RESULT.md\n")
    r = run(world, "edm/closing-demo", RESGX545_DATA_PRIVATE=str(priv))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RUN_ALL PASSED" in r.stdout
    assert not (s / "private").exists()
    r = run(world, "edm/closing-demo", RESGX545_DATA_PRIVATE=str(tmp_path / "absent"))
    assert r.returncode != 0
    assert "freeze" in r.stdout


def test_a_part_with_its_own_freeze_is_pointed_like_the_session(world):
    """r6-held's part P (p/) has its own FROZEN.sha256 and FROZEN.commits, naming files of the
    tool tree and inputs read from scratch by absolute path: they are pinned and pointed at
    their copies as the session's own freeze is."""
    tool, data = world[0], world[1]
    c1 = git(tool, "rev-list", "--max-parents=0", "HEAD")
    s = data / "edm/closing-demo"
    (data / "cited/closing6").mkdir(parents=True)
    (data / "cited/closing6/plan.md").write_text("P\n")
    (s / "p").mkdir()
    (s / "p/FROZEN.sha256").write_text(
        f"{sha(V1)}  /Users/someone/src/resgx545/tools/x.py\n"
        f"{sha('P' + chr(10))}  /Users/someone/src/scratch/resgx545/closing6/plan.md\n")
    (s / "p/FROZEN.commits").write_text("# header\n" f"{sha(V1)}  {c1}  tools/x.py\n")
    run_all = RUN_ALL.replace(
        'echo "RUN_ALL PASSED"',
        '(cd p && shasum -a 256 -c FROZEN.sha256 --quiet) || { echo "part freeze"; exit 1; }\n'
        'echo "RUN_ALL PASSED"')
    (s / "tests/run_all.sh").write_text(run_all)
    frozen = (s / "FROZEN.sha256").read_text()
    (s / "FROZEN.sha256").write_text(frozen.replace(sha(RUN_ALL), sha(run_all)))
    r = run(world, "edm/closing-demo")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RUN_ALL PASSED" in r.stdout


def test_a_list_named_in_postrun_keeps_the_paths_as_frozen(world, tmp_path):
    """r6-held's generator writes its fixed data path into gen/data/sources.lst and checks the
    list against what it would write, and its freeze check wants every listed path in the
    freeze: moved to the fake home, neither holds. A list named in postrun/paths-as-frozen.txt
    keeps its bytes, and so do the freeze's lines of the paths it lists (they are read where the
    session read them)."""
    s = world[1] / "edm/closing-demo"
    kept = tmp_path / "author/resgx545-data/edm/closing-sib/data.txt"
    kept.parent.mkdir(parents=True)
    kept.write_text("D\n")
    lst = f"{kept}\n"
    (s / "gen").mkdir()
    (s / "gen/sources.lst").write_text(lst)
    (s / "postrun").mkdir()
    (s / "postrun/paths-as-frozen.txt").write_text("# kept as frozen\ngen/sources.lst\n")
    run_all = RUN_ALL.replace(
        'echo "RUN_ALL PASSED"',
        f'[ "$(cat gen/sources.lst)" = {kept} ] || {{ echo "moved"; exit 1; }}\n'
        f'grep -q " {kept}$" FROZEN.sha256 || {{ echo "freeze line moved"; exit 1; }}\n'
        'echo "RUN_ALL PASSED"')
    (s / "tests/run_all.sh").write_text(run_all)
    (s / "FROZEN.sha256").write_text(
        f"{sha(run_all)}  tests/run_all.sh\n"
        f"{sha(lst)}  gen/sources.lst\n"
        f"{sha('D' + chr(10))}  {kept}\n"
        f"{sha(V1)}  /Users/someone/src/resgx545/tools/x.py\n")
    r = run(world, "edm/closing-demo")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RUN_ALL PASSED" in r.stdout


def test_absolute_paths_in_the_tests_point_at_the_fake_home(world):
    """R6-dpm's tests/test_read.py scans render/ by the author's absolute data path, so it sees
    the session's own kept rows, published after its freeze, and not the data view. The copy's
    tests/ files that no freeze names have their absolute resgx545-data and resgx545 paths
    pointed at the fake home; other trees are left alone (scratch too: R6-misc's test_gen.py
    reads a ranking kept only in the author's scratch); a frozen file keeps the bytes that
    ran (R6-pixel's freeze verify wants every tests/*.py frozen as it is), and the data
    repository is never written."""
    data = world[1]
    s = data / "edm/closing-demo"
    (data / "edm/closing-later").mkdir()
    (s / "postrun").mkdir()
    (s / "postrun/data-view.txt").write_text("edm/closing-sib\n")
    paths = (
        'D=/Users/someone/src/resgx545-data/edm\n'
        '[ "$D" = "$HOME/src/resgx545-data/edm" ] || { echo "data path $D"; exit 1; }\n'
        '[ -d "$D/closing-later" ] && { echo "later seen"; exit 1; }\n'
        '[ -f "$D/closing-sib/marker" ] || { echo "listed missing"; exit 1; }\n'
        'T="/Users/someone/src/resgx545/tools/x.py"\n'
        '[ "$T" = "$HOME/src/resgx545/tools/x.py" ] || { echo "tool path $T"; exit 1; }\n'
        "X='/Users/someone/src/scratch/resgx545/closing/sib'\n"
        'case "$X" in "$HOME"/*) echo "scratch $X"; exit 1 ;; esac\n'
        'P=/Users/someone/src/resgx545-data-private/cited\n'
        'case "$P" in "$HOME"/*) echo "private $P"; exit 1 ;; esac\n'
        'L=/Volumes/linux/linux-sgx\n'
        'case "$L" in "$HOME"/*) echo "linux $L"; exit 1 ;; esac\n')
    (s / "tests/paths.sh").write_text(paths)
    frozen_py = 'D = "/Users/someone/src/resgx545-data/render"\n'
    (s / "tests/frozen.py").write_text(frozen_py)
    run_all = RUN_ALL.replace(
        'echo "RUN_ALL PASSED"',
        'bash tests/paths.sh || exit 1\n'
        f'[ "$(shasum -a 256 tests/frozen.py | cut -c1-64)" = {sha(frozen_py)} ] '
        '|| { echo "frozen moved"; exit 1; }\n'
        'grep -q "  tests/frozen.py$" FROZEN.sha256 || { echo "freeze line moved"; exit 1; }\n'
        'echo "RUN_ALL PASSED"')
    (s / "tests/run_all.sh").write_text(run_all)
    frozen = (s / "FROZEN.sha256").read_text()
    (s / "FROZEN.sha256").write_text(frozen.replace(sha(RUN_ALL), sha(run_all))
                                     + f"{sha(frozen_py)}  tests/frozen.py\n")
    before = snapshot(data)
    r = run(world, "edm/closing-demo")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RUN_ALL PASSED" in r.stdout
    assert snapshot(data) == before


def built_world(world, source=V1, recipe="data:edm/closing-demo/lead/build.sh"):
    """The demo session froze a binary it ran (bin/t/tool, by relative path) that the published
    copy does not hold, and binds it to its source in FROZEN.commits: tools/x.py at the first
    commit, built by a recipe published beside it."""
    tool, data, _ = world
    s = data / "edm/closing-demo"
    c1 = git(tool, "rev-list", "--max-parents=0", "HEAD")
    (s / "lead").mkdir()
    (s / "lead/build.sh").write_text("make\n")
    (s / "FROZEN.sha256").write_text((s / "FROZEN.sha256").read_text()
                                     + f"{sha('BIN')}  bin/t/tool\n")
    (s / "FROZEN.commits").write_text((s / "FROZEN.commits").read_text()
                                      + f"{sha('BIN')}  built  {c1}  tools/x.py  {sha(source)}"
                                      f"  {recipe}\n")
    return s


def test_a_built_binary_is_verified_by_its_source_not_its_bytes(world, tmp_path):
    """A FROZEN.commits built line stands for the binary: the runner checks the source blob at
    the commit and the recipe's place, drops the binary's line from the copy's freeze and never
    looks for the bytes (nor the private copy); the worktree stays at the tool tree's commit."""
    s = built_world(world)
    priv = tmp_path / "data-private"
    (priv / "cited/closing7/demo/bin/t").mkdir(parents=True)
    (priv / "cited/closing7/demo/bin/t/tool").write_text("NOT THE BINARY")
    r = run(world, "edm/closing-demo", RESGX545_DATA_PRIVATE=str(priv))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RUN_ALL PASSED" in r.stdout
    assert "built bin/t/tool" in r.stdout and "source verified" in r.stdout
    assert sha("BIN") in (s / "FROZEN.sha256").read_text()      # the published freeze is kept


def test_a_built_binary_whose_source_differs_fails(world):
    built_world(world, source=V2)
    r = run(world, "edm/closing-demo")
    assert r.returncode == 1 and "RUN_ALL PASSED" not in r.stdout
    assert "tools/x.py" in r.stdout and "FAIL" in r.stdout


def test_a_built_binary_whose_recipe_is_missing_fails(world):
    built_world(world, recipe="data:edm/closing-demo/lead/gone.sh")
    r = run(world, "edm/closing-demo")
    assert r.returncode == 1 and "RUN_ALL PASSED" not in r.stdout
    assert "gone.sh" in r.stdout and "FAIL" in r.stdout
