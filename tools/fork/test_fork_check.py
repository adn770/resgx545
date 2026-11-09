# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""fork-check.sh: the linux fork's per-commit check (build gma500 for i686 with W=1, run its KUnit
suites under qemu, debug group off and, from the commit that adds it, on). The real run needs
cachix (docker, the laptop's config); these tests run its dry-run mode against a toy repository
and its log summaries against sample logs."""
import pathlib
import subprocess

import pytest

CHECK = pathlib.Path(__file__).resolve().parent / "fork-check.sh"
KCONFIG = "drivers/gpu/drm/gma500/Kconfig"


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                          text=True).stdout.strip()


def commit(repo, msg, files):
    for path, text in files.items():
        (repo / path).parent.mkdir(parents=True, exist_ok=True)
        (repo / path).write_text(text)
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", msg)
    return git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path):
    """base, one commit without the debug option, one that adds it."""
    r = tmp_path / "linux"
    r.mkdir()
    git(r, "init", "-q", "-b", "work")
    base = commit(r, "Linux 7.3", {KCONFIG: "config DRM_GMA500\n\ttristate\n"})
    plain = commit(r, "drm/gma500: add a parser", {"drivers/gpu/drm/gma500/a.c": "int a;\n"})
    debug = commit(r, "drm/gma500: add a debug group", {
        KCONFIG: "config DRM_GMA500\n\ttristate\n\nconfig DRM_GMA500_SGXFIVE_DEBUG\n\tbool\n"})
    return r, base, plain, debug


def run(args, cwd, **env):
    import os
    e = {**os.environ, "CHECK_CONFIG": "/cfg/laptop.config", "CHECK_WORK": "/w",
         "CHECK_JOBS": "8", **env}
    return subprocess.run(["sh", str(CHECK), *args], cwd=cwd, capture_output=True, text=True,
                          env=e)


def dry(repo, *args):
    r = run(list(args), repo, CHECK_DRY_RUN="1")
    assert r.returncode == 0, r.stderr
    return r.stdout.splitlines()


def blocks(lines):
    """{(short hash, config): the commands printed for it}, from the '# <hash> debug=X' marks."""
    out, key = {}, None
    for ln in lines:
        if ln.startswith("# ") and " debug=" in ln:
            h, cfg = ln[2:].split()[:2]
            key = (h, cfg.split("=")[1])
            out[key] = []
        elif key is not None and ln.startswith("$ "):
            out[key].append(ln[2:])
    return out


def test_usage_without_a_base(repo):
    r, *_ = repo
    p = run([], r)
    assert p.returncode == 2
    assert "usage" in p.stderr


@pytest.mark.parametrize("dry_run", ["", "1"])
def test_chroot_without_a_work_directory_is_refused(repo, dry_run):
    r, base, *_ = repo
    p = run([base], r, CHECK_RUNNER="chroot", CHECK_WORK="", CHECK_DRY_RUN=dry_run)
    assert p.returncode == 2
    assert "CHECK_WORK" in p.stderr
    assert p.stdout == ""


def test_chroot_with_a_work_directory_is_accepted(repo):
    r, base, *_ = repo
    p = run([base], r, CHECK_RUNNER="chroot", CHECK_WORK="/w", CHECK_DRY_RUN="1")
    assert p.returncode == 0, p.stderr


def test_one_line_per_commit_and_config(repo):
    r, base, plain, debug = repo
    lines = dry(r, base)
    marks = [ln for ln in lines if ln.startswith("DRY ")]
    assert marks == [f"DRY {plain[:12]} debug=off drm/gma500: add a parser",
                     f"DRY {debug[:12]} debug=off drm/gma500: add a debug group",
                     f"DRY {debug[:12]} debug=on drm/gma500: add a debug group"]


def test_debug_on_only_once_the_option_exists(repo):
    r, base, plain, debug = repo
    b = blocks(dry(r, base))
    assert set(b) == {(plain[:12], "off"), (debug[:12], "off"), (debug[:12], "on")}


def test_build_is_the_laptops(repo):
    r, base, plain, debug = repo
    b = blocks(dry(r, base))
    for (h, cfg), cmds in b.items():
        text = "\n".join(cmds)
        assert "resgx545/arch32:kernel" in text            # gcc 15, i686 userland
        assert f"cp /cfg/laptop.config /w/build-{cfg}/.config" in text
        assert "ARCH=i386 olddefconfig" in text
        assert "-e DRM_GMA500_KUNIT_TEST" in text
        flag = "-e" if cfg == "on" else "-d"
        assert f"{flag} DRM_GMA500_SGXFIVE_DEBUG" in text
        # the x86 decoder self-test (a single-threaded awk pass, ~20 min a config on the
        # laptop) checks nothing of gma500's: off under both runners
        assert "-d X86_DECODER_SELFTEST" in text
        assert text.index("-d X86_DECODER_SELFTEST") < text.index("olddefconfig")
        # W=1 over gma500 only (a W=1 modules build would rebuild the kernel), then modpost
        assert "-j8 W=1 drivers/gpu/drm/gma500/" in text
        # then everything, modules included: a fresh build directory has no vmlinux, and
        # modpost needs its symbols (32-bit zstd -22 runs out of memory: zstd-kernel)
        assert text.index("W=1 drivers/gpu/drm/gma500/") < text.index(
            "make O=/b ARCH=i386 ZSTD=zstd-kernel -j8 &&")


def test_kunit_runs_under_qemu_i386(repo):
    r, base, plain, debug = repo
    b = blocks(dry(r, base))
    for (h, cfg), cmds in b.items():
        text = "\n".join(cmds)
        assert "resgx545/arch32:kunit" in text                # gcc 15 too, plus qemu
        assert "tools/testing/kunit/kunit.py run --arch=i386" in text
        assert f"--build_dir=/kb" in text and f"/w/kunit-{cfg}:/kb" in text
        for opt in ("CONFIG_KUNIT=y", "CONFIG_PCI=y", "CONFIG_DRM=y", "CONFIG_DRM_GMA500=y",
                    "CONFIG_DRM_GMA500_KUNIT_TEST=y"):
            assert opt in text
        on = "CONFIG_DRM_GMA500_SGXFIVE_DEBUG=y" in text and "CONFIG_DEBUG_FS=y" in text
        assert on == (cfg == "on")


def test_each_commit_is_checked_out_in_order_then_head_restored(repo):
    r, base, plain, debug = repo
    lines = dry(r, base)
    cos = [ln[2:] for ln in lines if ln.startswith("$ git checkout")]
    assert cos == [f"git checkout -q --detach {plain}", f"git checkout -q --detach {debug}",
                   "git checkout -q work"]


def test_kunit_image_is_built_when_missing(repo):
    r, base, *_ = repo
    text = "\n".join(dry(r, base))
    assert "docker image inspect resgx545/arch32:kunit" in text
    assert "qemu-system-x86" in text


def test_dry_run_touches_nothing(repo, tmp_path):
    r, base, plain, debug = repo
    work = tmp_path / "work"
    p = run([base], r, CHECK_DRY_RUN="1", CHECK_WORK=str(work))
    assert p.returncode == 0
    assert git(r, "rev-parse", "HEAD") == debug
    assert git(r, "symbolic-ref", "--short", "HEAD") == "work"
    assert not work.exists()


def test_range_end(repo):
    r, base, plain, debug = repo
    marks = [ln for ln in dry(r, base, plain) if ln.startswith("DRY ")]
    assert marks == [f"DRY {plain[:12]} debug=off drm/gma500: add a parser"]


KUNIT_LOG = """\
[13:31:56] =============== gma500_sgx_fw (16 subtests) ================
[13:31:56] [PASSED] sgx_fw_test_crc32
[13:31:56] ================== [PASSED] gma500_sgx_fw ==================
[13:31:56] =============== gma500_sgx_mmu (2 subtests) ================
[13:31:56] ================= [PASSED] gma500_sgx_mmu ==================
[13:31:56] ============================================================
[13:31:56] Testing complete. Ran 18 tests: passed: 18
"""


def test_kunit_summary(tmp_path):
    log = tmp_path / "k.log"
    log.write_text(KUNIT_LOG)
    p = subprocess.run(["sh", str(CHECK), "--kunit-summary", str(log)], capture_output=True,
                       text=True)
    assert p.returncode == 0
    assert p.stdout.strip() == "kunit 18/18 (gma500_sgx_fw:16 gma500_sgx_mmu:2)"


def test_kunit_summary_fails_on_a_failure(tmp_path):
    log = tmp_path / "k.log"
    log.write_text(KUNIT_LOG.replace("Ran 18 tests: passed: 18",
                                     "Ran 18 tests: passed: 17, failed: 1"))
    p = subprocess.run(["sh", str(CHECK), "--kunit-summary", str(log)], capture_output=True,
                       text=True)
    assert p.returncode == 1
    assert "17/18" in p.stdout


def test_kunit_summary_fails_without_the_gma500_suites(tmp_path):
    log = tmp_path / "k.log"
    log.write_text("[1] Testing complete. Ran 3 tests: passed: 3\n")
    p = subprocess.run(["sh", str(CHECK), "--kunit-summary", str(log)], capture_output=True,
                       text=True)
    assert p.returncode == 1


def test_warnings_in_gma500_only(tmp_path):
    log = tmp_path / "b.log"
    log.write_text(
        "/k/drivers/gpu/drm/amd/x.c:1:1: warning: the frame size is larger\n"
        "  CC [M]  drivers/gpu/drm/gma500/sgxfive/sgxfive.o\n")
    p = subprocess.run(["sh", str(CHECK), "--gma500-warnings", str(log)],
                       capture_output=True, text=True)
    assert (p.returncode, p.stdout.strip()) == (0, "0")
    log.write_text(log.read_text()
                   + "/k/drivers/gpu/drm/gma500/sgxfive/sgxfive.c:9:5: warning: no previous"
                   " prototype\n"
                   + "/k/drivers/gpu/drm/gma500/gma_sgx.c:3:1: error: unknown type\n")
    p = subprocess.run(["sh", str(CHECK), "--gma500-warnings", str(log)],
                       capture_output=True, text=True)
    assert (p.returncode, p.stdout.strip()) == (1, "2")


def test_kunit_image_is_the_build_image_with_qemu(repo):
    r, base, *_ = repo
    first = dry(r, base)[0]
    assert "FROM resgx545/arch32:kernel" in first and "qemu-system-x86" in first


def test_the_chroot_runner_uses_the_laptops_build_root(repo):
    r, base, plain, debug = repo
    p = run([base], r, CHECK_DRY_RUN="1", CHECK_RUNNER="chroot", CHECK_ROOT="/var/lib/x")
    assert p.returncode == 0, p.stderr
    text = p.stdout
    assert "docker" not in text
    # the build root is under /var/lib/machines (mode 0700): only root can look inside
    assert "sudo -n test -x /var/lib/x/usr/bin/qemu-system-i386" in text
    b = blocks(text.splitlines())
    for (h, cfg), cmds in b.items():
        build, kunit = [c for c in cmds if "systemd-nspawn" in c]
        for c in (build, kunit):
            assert c.startswith("sudo systemd-nspawn -q -D /var/lib/x --user=")
            assert f"--bind-ro={r}:/k" in c and "--chdir=/k" in c
        assert f"--bind=/w/build-{cfg}:/b" in build and "W=1 drivers/gpu/drm/gma500/" in build
        assert f"--bind=/w/kunit-{cfg}:/kb" in kunit and "kunit.py run --arch=i386" in kunit


def test_both_runners_mount_the_same_paths(repo):
    # objects record /k, /b, /kb: a work directory built by one runner stays valid in the other
    r, base, *_ = repo
    d = blocks(dry(r, base))
    c = blocks(run([base], r, CHECK_DRY_RUN="1", CHECK_RUNNER="chroot").stdout.splitlines())
    import re
    def mounts(cmds):
        return sorted(set(re.findall(r":(/k[bc]?|/b)\b", " ".join(cmds))))
    assert all(mounts(d[k]) == mounts(c[k]) for k in d)


def test_an_unknown_runner_is_refused(repo):
    r, base, *_ = repo
    p = run([base], r, CHECK_DRY_RUN="1", CHECK_RUNNER="vm")
    assert p.returncode == 2 and "CHECK_RUNNER" in p.stderr


def test_the_chroot_runner_stops_without_qemu(repo):
    r, base, plain, debug = repo
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=r, capture_output=True,
                          text=True).stdout
    p = run([base], r, CHECK_RUNNER="chroot", CHECK_ROOT="/nonexistent-root")
    assert p.returncode == 1
    assert "no qemu in /nonexistent-root" in p.stderr
    assert "PASS" not in p.stdout and "FAIL" not in p.stdout       # nothing was built
    assert subprocess.run(["git", "rev-parse", "HEAD"], cwd=r, capture_output=True,
                          text=True).stdout == head


# ---- one build directory per config, and the fast path ------------------------------------
# Flipping the debug option in one build directory changed the embedded .config (IKCONFIG):
# vmlinux linked again, modpost walked every module and the image was recompressed, ~25 min a
# config on the laptop. Each config now keeps its own directory, and a commit that changes
# only gma500's sources (not its Kconfig) is built as gma500 alone (W=1, its own modpost
# against the directory's Module.symvers, ~2 min).

FAST = "M=/k/drivers/gpu/drm/gma500 MO=/b/drivers/gpu/drm/gma500"


@pytest.fixture
def series(tmp_path):
    """base; plain (gma500 source); debug (Kconfig adds the option); inner (gma500 source and
    the UAPI header); wide (a file outside gma500)."""
    r = tmp_path / "linux"
    r.mkdir()
    git(r, "init", "-q", "-b", "work")
    c = {}
    c["base"] = commit(r, "Linux 7.3", {KCONFIG: "config DRM_GMA500\n\ttristate\n"})
    c["plain"] = commit(r, "drm/gma500: a", {"drivers/gpu/drm/gma500/a.c": "int a;\n"})
    c["debug"] = commit(r, "drm/gma500: debug", {
        KCONFIG: "config DRM_GMA500\n\ttristate\n\nconfig DRM_GMA500_SGXFIVE_DEBUG\n\tbool\n"})
    c["inner"] = commit(r, "drm/gma500: inner", {
        "drivers/gpu/drm/gma500/sgxfive/b.c": "int b;\n",
        "include/uapi/drm/sgxfive_drm.h": "#define X 1\n"})
    c["wide"] = commit(r, "drm/gma500: wide", {"drivers/gpu/drm/x.c": "int x;\n"})
    return r, c


def kind(cmds):
    text = "\n".join(cmds)
    full = "olddefconfig" in text and "make O=/b ARCH=i386 ZSTD=zstd-kernel" in text
    fast = FAST in text
    assert full != fast, text
    return "full" if full else "fast"


def test_each_config_builds_in_its_own_directory(repo):
    r, base, plain, debug = repo
    for (h, cfg), cmds in blocks(dry(r, base)).items():
        text = "\n".join(cmds)
        assert f"-v /w/build-{cfg}:/b" in text
        assert "/w/build:" not in text and "/w/build/" not in text


def test_only_gma500_source_changes_take_the_fast_path(series):
    r, c = series
    b = blocks(dry(r, c["base"]))
    s = {k: kind(v) for k, v in b.items()}
    h = {n: c[n][:12] for n in c}
    assert s == {(h["plain"], "off"): "full",      # a fresh directory
                 (h["debug"], "off"): "full",      # Kconfig changed
                 (h["debug"], "on"): "full",       # the on directory's first build
                 (h["inner"], "off"): "fast",      # gma500 and its UAPI header only
                 (h["inner"], "on"): "fast",
                 (h["wide"], "off"): "full",       # a file outside gma500
                 (h["wide"], "on"): "full"}


def test_the_fast_path_builds_gma500_with_w1_and_its_modpost(series):
    r, c = series
    cmds = blocks(dry(r, c["base"]))[(c["inner"][:12], "off")]
    text = "\n".join(cmds)
    assert f"make O=/b ARCH=i386 -j8 W=1 {FAST} && echo build done" in text
    assert "-v /w/build-off:/b" in text


def test_a_built_commit_is_recorded_per_config(series):
    r, c = series
    b = blocks(dry(r, c["base"]))
    for (h, cfg), cmds in b.items():
        full = next(c[n] for n in c if c[n].startswith(h))
        rec = f"echo {full} > /w/build-{cfg}.built"
        kunit = next(i for i, x in enumerate(cmds) if "kunit.py run" in x)
        assert rec in cmds and cmds.index(rec) > kunit, cmds


def test_a_later_run_continues_from_the_recorded_build(series, tmp_path):
    r, c = series
    work = tmp_path / "w"
    work.mkdir()
    (work / "build-off.built").write_text(c["debug"] + "\n")
    out = run([c["debug"]], r, CHECK_DRY_RUN="1", CHECK_WORK=str(work)).stdout.splitlines()
    b = blocks(out)
    assert kind(b[(c["inner"][:12], "off")]) == "fast"
    assert kind(b[(c["inner"][:12], "on")]) == "full"     # no recorded on build


def test_a_fast_build_counts_every_warning(tmp_path):
    log = tmp_path / "b.log"
    log.write_text("sgxfive/sgxfive.c:12:3: warning: unused variable 'x'\n"
                   "/k/drivers/gpu/drm/gma500/psb_drv.c:9:1: error: oops\n")
    p = subprocess.run(["sh", str(CHECK), "--gma500-warnings", str(log), "all"],
                       capture_output=True, text=True)
    assert p.returncode == 1 and p.stdout.strip() == "2"


# A config's first build in an empty directory starts from the other config's directory: on
# the laptop a from-scratch kernel build takes most of a day, the debug flip about half an
# hour. The other directory's record is not copied (its .config differs), so the build is full.
SEED = "[ -e /w/build-on/.config ] || [ ! -e /w/build-off/.config ] || cp -a /w/build-off/. /w/build-on/"


def test_an_empty_directory_is_seeded_from_the_other_config(series):
    r, c = series
    b = blocks(dry(r, c["base"]))
    cmds = b[(c["debug"][:12], "on")]
    build = next(i for i, x in enumerate(cmds) if "olddefconfig" in x)
    assert SEED in cmds and cmds.index(SEED) < build, cmds
    assert not any("build-off.built" in x and "build-on" in x for x in cmds)
    fast = b[(c["inner"][:12], "on")]
    assert SEED not in fast
