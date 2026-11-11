# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The kernel's verifier against the Python one (phase 11.29 review R9).

host/own_host.c is built with shim headers around the fork's real sgxfive_owntask.c and sgx_fw.c
(the fork is read at the pinned commit of forkpin.py, from RESGX545_LINUX or ../linux), and run over the same
blobs as fwtask.refusal(): the crafted ones, every blob of asm/fwtask, every single-bit change of
the words of some of them, and random words of the canonical forms. The two must agree on every
verdict and on the first reason. Without a C compiler or the checkout the tests skip and say so;
a skip is not a pass. None of this touches the closed firmware."""
import functools
import pathlib
import random
import shutil
import struct
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fwtask  # noqa: E402
import gen_verify  # noqa: E402

SGXFIVE = gen_verify.SGXFIVE
REGS = fwtask.load_regs()


@functools.cache
def host_build() -> pathlib.Path:
    cc = shutil.which("cc") or shutil.which("gcc")
    if cc is None or not (SGXFIVE / "sgxfive_owntask.c").is_file():
        pytest.skip(f"SKIPPED, NOT PASSED: no C compiler or no fork commit {gen_verify.forkpin.pin()} in {gen_verify.LINUX}")
    out = pathlib.Path(__import__("tempfile").mkdtemp(prefix="own_host_")) / "own_host"
    flags = [] if "sgx_own_apply" in (SGXFIVE / "sgxfive_owntask.h").read_text() else ["-DHOST_NO_APPLY"]
    r = subprocess.run([cc, "-std=gnu11", "-O1", "-Wall", "-Wextra", *flags, f"-I{HERE / 'host' / 'shim'}",
                        f"-I{SGXFIVE}", "-o", str(out), str(HERE / "host" / "own_host.c"),
                        str(SGXFIVE / "sgxfive_owntask.c"), str(SGXFIVE / "sgx_fw.c")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-2000:]
    return out


def c_verdicts(blobs, tmp_path) -> list[str | None]:
    f = tmp_path / "blobs.bin"
    f.write_bytes(b"".join(struct.pack("<I", len(b)) + b for b in blobs))
    r = subprocess.run([str(host_build()), "verify", str(f)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = []
    for line in r.stdout.splitlines():
        out.append(None if line == "OK" else "parse" if line == "EINVAL" else line.removeprefix("EPERM "))
    assert len(out) == len(blobs)
    return out


def agree(blobs, tmp_path, names=None):
    got = c_verdicts(blobs, tmp_path)
    bad = [(names[i] if names else i, got[i], fwtask.refusal(b, REGS)) for i, b in enumerate(blobs)
           if got[i] != fwtask.refusal(b, REGS)]
    assert not bad, f"{len(bad)} of {len(blobs)} differ, first: {bad[:3]}"
    return got


def test_c_verifier_gives_the_crafted_blobs_their_reason(tmp_path):
    cb = gen_verify.crafted_blobs()
    got = c_verdicts([d for _, d, _, _ in cb], tmp_path)
    for (name, _, err, why), g in zip(cb, got):
        assert g == (why or "parse"), name


def test_c_verifier_accepts_every_source(tmp_path):
    names = [p.stem for p in fwtask.sources()]
    got = c_verdicts([fwtask.blob_of(n) for n in names], tmp_path)
    assert got == [None] * len(names), dict(zip(names, got))


def flips(words):
    for i in range(len(words)):
        for b in range(64):
            yield i, b, words[:i] + [words[i] ^ 1 << b] + words[i + 1:]


@pytest.mark.parametrize("name", ["null", "mem", "x9b_r1", "state"])
def test_c_and_python_agree_on_every_bit_flip_of_every_word(name, tmp_path):
    p = fwtask.parse_blob(fwtask.blob_of(name))
    muts = [fwtask.pack_blob(w, p.patches, p.entries) for _, _, w in flips(p.words)]
    got = agree(muts, tmp_path)
    assert 0 < got.count(None) < len(got)       # a flip in a free field is accepted, the rest not


# the canonical words with their free fields randomised, the way a hostile blob would
def random_word(rng):
    row = rng.choice([r for r in fwtask.FORMS if r[1] != "DENY"])
    free = ~row[2] & fwtask.ALL
    return row[3] | rng.getrandbits(64) & free


def random_blob(rng):
    n = rng.randrange(1, 14)
    words = [random_word(rng) for _ in range(n)]
    pool = fwtask.assemble_text("mov r1, #0xdeadbeef\nstad [r1,+#0], r4\nldad.bypassl1 r2, [r1,+#1], drc0\n"
                                "mov pclink, r30\nlapc\nbr #1\np0 br -#0x1\nnop.end\nmov r30, #0xdeadbeef")
    words += [rng.choice(pool) for _ in range(rng.randrange(0, 8))]
    n = len(words)
    patches = [fwtask.Patch(rng.randrange(0, n + 1), rng.choice(["res", "cont0", "cont5", "kind9"]),
                            rng.choice([0, 0, 4, 0xfff, 0x1000]))
               for _ in range(rng.randrange(0, 4))]
    entries = [rng.randrange(0, n + 1) for _ in range(rng.randrange(0, 3))]
    return fwtask.pack_blob(words, patches, entries)


def test_c_and_python_agree_on_random_blobs_of_canonical_words(tmp_path):
    rng = random.Random(1129)
    blobs = [random_blob(rng) for _ in range(6000)]
    got = agree(blobs, tmp_path)
    assert len(set(got)) > 6, set(got)        # the random blobs reach many different reasons


def test_c_and_python_agree_on_random_bytes_in_the_blobs_of_the_sources(tmp_path):
    rng = random.Random(545)
    blobs = []
    for p in fwtask.sources():
        good = fwtask.blob_of(p.stem)
        for _ in range(300):
            b = bytearray(good)
            for _ in range(rng.randrange(1, 4)):
                b[rng.randrange(len(b))] ^= 1 << rng.randrange(8)
            blobs.append(bytes(b))
    agree(blobs, tmp_path)
