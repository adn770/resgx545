# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""sgxfive-test tri options of the 11.38 DPM and partial-render batch, against the mock:

  --keep-overflow --ctx2 [--close-first-early]: an overflowed first render does not stop the
      second context, and an overflowed second render is counted;
  --tadata-fill-render N:PAGE:VALUE[:ramp]: debugfs tadata_fill written just before render N, so
      that a page of the TA data can be changed between a geometry kick and the final render;
  --kept-copy DIR (tri --ctx2): debugfs render_kept copied to DIR/kept.N.bin after the second
      context's render N and before any close, and with --close-first-early to
      DIR/kept.closed.N.bin right after the first context's close (round 18, Q192);
  --kpoke-render N:rd:11=V: the render details' ZLS control word of render N's kick (Q088).
Run through `make check`, which builds the binary and sets SGXFIVE_TEST."""
from __future__ import annotations

import os
import pathlib
import subprocess

import pytest

HERE = pathlib.Path(__file__).resolve().parent
TOOL = os.environ.get("SGXFIVE_TEST", str(HERE.parent / "build" / "sgxfive-test"))


def run(*args: str, dbg: pathlib.Path | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    if dbg is not None:
        env["SGXFIVE_DEBUGFS"] = str(dbg)
    return subprocess.run([TOOL, *args], capture_output=True, text=True, timeout=60, env=env)


@pytest.fixture(scope="module", autouse=True)
def tool_exists():
    if not pathlib.Path(TOOL).exists():
        pytest.skip(f"{TOOL} not built (run make -C userspace/libsgxfive check)")


def test_keep_overflow_alone_still_counts():
    r = run("--mock", "--mock-pb-pages=0x28", "tri", "--width", "1024", "--height", "768", "--keep-overflow")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "1 overflowed" in r.stdout


def test_t2_second_context_after_an_overflowed_first_render():
    r = run("--mock", "--mock-pb-pages=0x28", "tri", "--width", "1024", "--height", "768",
            "--keep-overflow", "--ctx2", "--close-first-early")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "tri2 1024x768 #1: overflowed" in r.stdout, r.stdout


def test_t3_tadata_fill_before_render_n(tmp_path):
    (tmp_path / "tadata_fill").write_text("")
    r = run("--mock", "tri", "--width", "64", "--height", "64", "-n", "2", "--geometry", "1",
            "--tadata-fill-render", "2:6:0xa5000000:ramp", dbg=tmp_path)
    assert "tri: tadata_fill before render 2: 6 0xa5000000 ramp" in r.stdout, r.stdout + r.stderr
    assert (tmp_path / "tadata_fill").read_text() == "6 0xa5000000 ramp\n"


def test_t3_rejects_a_bad_spec():
    r = run("--mock", "tri", "--tadata-fill-render", "x")
    assert r.returncode != 0
    assert "bad --tadata-fill-render" in r.stderr


def test_t4_kept_copy_after_the_second_render(tmp_path):
    (tmp_path / "render_kept").write_bytes(bytes(range(256)) * 4)
    out = tmp_path / "out"
    out.mkdir()
    r = run("--mock", "tri", "--width", "64", "--height", "64", "--ctx2", "--close-first-early",
            "--kept-copy", str(out), dbg=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (out / "kept.1.bin").read_bytes() == bytes(range(256)) * 4


def test_t4_needs_ctx2():
    r = run("--mock", "tri", "--kept-copy", "/tmp")
    assert r.returncode == 2
    assert "--kept-copy is for tri --ctx2" in r.stderr


# ---- round 18 (I1): the 1024x768 partial owner and the render details' ZLS word ---------------
PARTIAL = ("--mock", "--mock-pb-pages=0x28", "tri", "--width", "1024", "--height", "768", "-n",
           "1", "--keep-overflow", "--ctx2", "--close-first-early")


def kept_pages(n: int) -> bytes:
    """n TA data pages, page i's dwords all i (a kept copy shows which pages it holds)."""
    return b"".join(i.to_bytes(4, "little") * 1024 for i in range(n))


def test_kept_copy_reaches_the_1024x768_partial_owner(tmp_path):
    """Q192: the kept first context rendered 1024x768 on 0x28 pages (a partial render), its state
    page is page 6 (E591). --kept-copy copies the whole kept TA data (pages 1 to 6 and on) after
    the second context's render, which overflowed too and is counted, and before that context is
    closed."""
    (tmp_path / "render_kept").write_bytes(kept_pages(12))
    out = tmp_path / "out"
    out.mkdir()
    r = run(*PARTIAL, "--kept-copy", str(out), dbg=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (out / "kept.1.bin").read_bytes() == kept_pages(12)
    lines = r.stdout.splitlines()
    at = {k: next(i for i, ln in enumerate(lines) if ln.startswith(k)) for k in (
        "tri: closed the first context", "tri2 1024x768 #1: overflowed",
        "tri: render_kept after the second context's render 1:", "tri: closing the second")}
    assert list(at.values()) == sorted(at.values()), r.stdout


def test_kept_copy_also_after_the_early_close_before_the_second_render(tmp_path):
    """Q192 asks whether the zero in the partial owner's state page is the store after the second
    context's render, not the close of the first: with --close-first-early, --kept-copy also
    copies render_kept to DIR/kept.closed.N.bin right after that close and before the second
    context's render N, so the two copies part the close from the render."""
    (tmp_path / "render_kept").write_bytes(kept_pages(7))
    out = tmp_path / "out"
    out.mkdir()
    r = run(*PARTIAL, "--kept-copy", str(out), dbg=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (out / "kept.closed.1.bin").read_bytes() == kept_pages(7)
    assert (out / "kept.1.bin").read_bytes() == kept_pages(7)
    lines = r.stdout.splitlines()
    closed = next(i for i, ln in enumerate(lines) if ln.startswith("tri: closed the first"))
    copy = next(i for i, ln in enumerate(lines) if ln.startswith(
        "tri: render_kept after closing the first context, before the second context's "
        "render 1: "))
    second = next(i for i, ln in enumerate(lines) if ln.startswith("tri2 1024x768 #1"))
    assert closed < copy < second, r.stdout
    assert f"{out}/kept.closed.1.bin (28672 bytes)" in lines[copy]


def test_kept_copy_without_the_early_close_makes_no_closed_copy(tmp_path):
    (tmp_path / "render_kept").write_bytes(kept_pages(1))
    out = tmp_path / "out"
    out.mkdir()
    r = run("--mock", "tri", "--width", "64", "--height", "64", "--ctx2", "--kept-copy", str(out),
            dbg=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert sorted(p.name for p in out.iterdir()) == ["kept.1.bin"]
    assert "after closing the first context" not in r.stdout


CLOSED_LINE = ("tri: render_kept after closing the first context, before the second context's "
               "render 1: ")


def test_kept_copy_after_the_close_reads_again_while_render_kept_is_empty(tmp_path):
    """E1085: render_kept read 0 bytes right after the early close (the context parked later,
    a race [infer]). The copy after the close reads again while it is empty, up to 10 reads 10 ms
    apart, and says how many it took; --mock-park-ms=N is the mock's park N ms after the close."""
    (tmp_path / "render_kept").write_bytes(kept_pages(7))
    out = tmp_path / "out"
    out.mkdir()
    r = run(PARTIAL[0], "--mock-park-ms=35", *PARTIAL[1:], "--kept-copy", str(out), dbg=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (out / "kept.closed.1.bin").read_bytes() == kept_pages(7)
    lines = r.stdout.splitlines()
    tries = [ln for ln in lines if ln.startswith("tri: render_kept read ")]
    assert len(tries) == 1, r.stdout
    n = int(tries[0].split()[3])
    assert 2 <= n <= 10, tries[0]
    assert tries[0] == (f"tri: render_kept read {n} times after closing the first context, "
                        f"before the second context's render 1 (empty {n - 1}, 10 ms apart): "
                        "28672 bytes")
    copy = next(ln for ln in lines if ln.startswith(CLOSED_LINE))
    assert copy.endswith(f"{out}/kept.closed.1.bin (28672 bytes)"), copy


def test_kept_copy_after_the_close_still_empty_after_10_reads(tmp_path):
    """Still empty after the bound: a clear line, and an empty file as before (the run goes on)."""
    (tmp_path / "render_kept").write_bytes(kept_pages(7))
    out = tmp_path / "out"
    out.mkdir()
    r = run(PARTIAL[0], "--mock-park-ms=1500", *PARTIAL[1:], "--kept-copy", str(out),
            dbg=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (out / "kept.closed.1.bin").read_bytes() == b""
    lines = r.stdout.splitlines()
    assert ("tri: render_kept still empty after 10 reads after closing the first context, "
            "before the second context's render 1 (10 ms apart): the copy is empty") in lines, \
        r.stdout
    copy = next(ln for ln in lines if ln.startswith(CLOSED_LINE))
    assert copy.endswith(f"{out}/kept.closed.1.bin (0 bytes)"), copy


def test_kept_copy_read_at_once_says_no_tries(tmp_path):
    """A first read with bytes is said as before, with no read-again line."""
    (tmp_path / "render_kept").write_bytes(kept_pages(7))
    out = tmp_path / "out"
    out.mkdir()
    r = run(*PARTIAL, "--kept-copy", str(out), dbg=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert not [ln for ln in r.stdout.splitlines() if ln.startswith("tri: render_kept read ")]
    assert "still empty" not in r.stdout


def test_kept_copy_after_the_second_render_is_not_read_again(tmp_path):
    """Only the copy right after a close reads again: an empty render_kept after the second
    render (no context kept) is copied once, as before."""
    (tmp_path / "render_kept").write_bytes(b"")
    out = tmp_path / "out"
    out.mkdir()
    r = run("--mock", "tri", "--width", "64", "--height", "64", "--ctx2", "--kept-copy", str(out),
            dbg=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (out / "kept.1.bin").read_bytes() == b""
    assert "tri: render_kept read " not in r.stdout, r.stdout
    assert "still empty" not in r.stdout, r.stdout


@pytest.mark.parametrize("arg", ["--mock-park-ms=", "--mock-park-ms=x", "--mock-park-ms=-1",
                                 "--mock-park-ms=60001"])
def test_mock_park_ms_rejects_a_bad_value(arg):
    assert run("--mock", arg, "query").returncode != 0


def test_mock_park_ms_needs_the_mock():
    r = run("--mock-park-ms=10", "query")
    assert r.returncode != 0


def kpoke_run(tmp_path, *args):
    k = tmp_path / "kpoke"
    k.write_text("")
    env = {**os.environ, "SGXFIVE_KPOKE": str(k)}
    r = subprocess.run([TOOL, *args], capture_output=True, text=True, timeout=60, env=env)
    return r, k.read_text().splitlines()


def test_kpoke_render_reaches_the_render_details_zls_word(tmp_path):
    """Q088: the render details' ZLS control word is rd:11 (the kernel's SGX_RENDER_RD_ZLSCTL,
    byte 0x2c of hw_render_details; E057 poked it so). --kpoke-render N:rd:11=V arms it for
    render N's kick, after --depth's own rd:11 (its --depth-ctl), and the kernel applies a kick's
    armed pokes in order, so the row's value is the one the job carries; on an overflowing scene
    the partial renders run from that job's render details."""
    r, lines = kpoke_run(tmp_path, "--mock", "--mock-pb-pages=0x28", "tri", "--width", "1024",
                         "--height", "768", "-n", "1", "--keep-overflow", "--depth",
                         "--depth-ctl", "0x0017100c", "--kpoke-render", "1:rd:11=0x0011700a")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "tri: kpoke before render 1: rd:11=0x0011700a" in r.stdout
    zls = [ln for ln in lines if ln.startswith("rd:11=")]
    assert zls == ["rd:11=0x0017100c", "rd:11=0x0011700a"], lines


def test_kpoke_render_reaches_the_zls_word_of_the_final_render_after_a_geometry_kick(tmp_path):
    """The final render's own kick after an overflowing geometry kick: the rd:11 poke of render
    2 is written after render 1's job and before render 2's (the geometry kick takes none)."""
    r, lines = kpoke_run(tmp_path, "--mock", "--mock-pb-pages=0x28", "tri", "--width", "1024",
                         "--height", "768", "-n", "2", "--geometry", "1", "--keep-overflow",
                         "--kpoke-render", "2:rd:11=0x0011100a")
    assert lines == ["rd:11=0x0011100a"], (lines, r.stdout + r.stderr)
    out = r.stdout.splitlines()
    poke = out.index("tri: kpoke before render 2: rd:11=0x0011100a")
    geo = next(i for i, ln in enumerate(out) if ln.startswith("tri 1024x768 #1: geometry only"))
    assert geo < poke, r.stdout
