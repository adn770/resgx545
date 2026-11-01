# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Round trips over every encoding the disassemblers decode.

For random words, whenever usse-dis (pds-dis) decodes a word to text, the
assembler must give back a word that decodes to the same text. Several
encodings print identically (bits the instruction ignores, operand fields an
operation does not read), so the words are compared through their decodes;
the share of words that come back bit-identical is reported.

USSE words are drawn per form of the decoder's table (its fixed bits, random
elsewhere, plus one- or two-bit flips of the fixed bits) and uniformly, for the
SGX545 and, fewer, for the SGX540 reading; PDS words uniformly per opcode.

The closed programs the user's own firmware file holds (the microkernel and the
five EDM PDS programs, in the private data repository: tools/records datasets.repos())
are read at run time and must reassemble bit for bit from their listings: the
encoder's choices for the bits an instruction ignores (the forms' dflt) agree
with the programs the firmware was built with. No word of them is stored here;
without the data those tests skip.
"""
import pathlib
import random
import subprocess
import sys

import pytest

from conftest import DIS_DIR, HERE, disasm, run_asm

sys.path[:0] = [str(HERE.parent / "fwcutter"), str(HERE.parent / "records")]
import datasets  # noqa: E402
import facts  # noqa: E402

SEED = 20261020
PER_FORM = 1500
UNIFORM = 50000
PDS_PER_OPCODE = 4000

PRIVATE = datasets.repos().get("data-private", pathlib.Path("/nonexistent"))
IMAGES = PRIVATE / "firmware" / "images" / "images"
needs_images = pytest.mark.skipif(
    not IMAGES.is_dir(), reason="SKIPPED, NOT PASSED: no firmware images in the private data "
    "repository; set RESGX545_DATA_PRIVATE")


def usse_corpus(rng, per_form=PER_FORM, uniform=UNIFORM):
    out = subprocess.run([str(DIS_DIR / "usse-dis"), "--forms"], capture_output=True,
                         text=True, check=True).stdout
    words = []
    for line in out.splitlines():
        _, mask, val, _, pat = line.split("\t")
        if pat == "(reject)":
            continue
        mask, val = int(mask, 16), int(val, 16)
        fixed = [b for b in range(64) if mask >> b & 1]
        for i in range(per_form):
            w = val | (rng.getrandbits(64) & ~mask & (2**64 - 1))
            if i % 3 == 2:
                for b in rng.sample(fixed, min(len(fixed), rng.choice((1, 2)))):
                    w ^= 1 << b
            words.append(w)
    return words + [rng.getrandbits(64) for _ in range(uniform)]


def decoded(text):
    return not (text.startswith((".long", ".word")) or "TODO" in text)


def pds_corpus(rng):
    return [(op << 27) | rng.getrandbits(27) for op in range(32) for _ in range(PDS_PER_OPCODE)]


def round_trip(tool, dis, words, tmp_path, *dis_args, opts=()):
    """Decode words, reassemble the decoded ones and decode them again: the texts must agree.
    Returns the decoded words and their reassembled words, in order."""
    texts = disasm(dis, words, tmp_path, *dis_args, opts=opts)
    keep = [(w, t) for w, t in zip(words, texts) if decoded(t)]
    again = run_asm(tool, "\n".join(t for _, t in keep) + "\n", tmp_path, *opts)
    assert len(again) == len(keep)
    texts2 = disasm(dis, again, tmp_path, *dis_args, opts=opts)
    bad = [(w, t, w2, t2) for (w, t), w2, t2 in zip(keep, again, texts2) if t != t2]
    same = sum(w == w2 for (w, _), w2 in zip(keep, again))
    print(f"\n{' '.join((tool, *opts))}: {len(words)} words, {len(keep)} decoded, {len(bad)} "
          f"failed, {same} bit-identical, {len(keep) - same} canonicalised "
          f"({100 * (len(keep) - same) / max(len(keep), 1):.1f}%)")
    assert not bad, bad[:5]
    return [w for w, _ in keep], again


def test_usse_round_trip(tmp_path):
    words = usse_corpus(random.Random(SEED))
    kept, _ = round_trip("usse-asm", DIS_DIR / "usse-dis", words, tmp_path)
    assert len(kept) > 50000


def test_usse_round_trip_sgx540(tmp_path):
    opts = ("--core", "540")
    words = usse_corpus(random.Random(SEED + 540), per_form=300, uniform=10000)
    kept, _ = round_trip("usse-asm", DIS_DIR / "usse-dis", words, tmp_path, opts=opts)
    assert len(kept) > 10000


def test_pds_round_trip(tmp_path):
    words = pds_corpus(random.Random(SEED))
    kept, _ = round_trip("pds-asm", DIS_DIR / "pds-dis", words, tmp_path, "0")
    assert len(kept) > 80000


def words_of(blob, width):
    data = blob.read_bytes()
    return [int.from_bytes(data[i:i + width], "little") for i in range(0, len(data), width)]


@needs_images
def test_the_microkernel_reassembles_bit_for_bit(tmp_path):
    kept, again = round_trip("usse-asm", DIS_DIR / "usse-dis",
                             words_of(IMAGES / "00_ukernel.bin", 8), tmp_path)
    assert len(kept) > 6000 and again == kept


@needs_images
def test_the_edm_pds_programs_reassemble_bit_for_bit(tmp_path):
    """Each EDM PDS program reassembles from its pds-dis listing, data segment included."""
    rows = {facts.BUFFER_NAMES[b.id]: b.pds_rows for b in facts.BUFFERS}
    progs = sorted(IMAGES.glob("0[1-5]_pds*.bin"))
    assert len(progs) == 5
    for blob in progs:
        data = rows[blob.stem.split("_", 1)[1]] * 4
        listing = subprocess.run([str(DIS_DIR / "pds-dis"), str(blob), str(data)],
                                 capture_output=True, text=True, check=True).stdout
        assert run_asm("pds-asm", listing, tmp_path) == words_of(blob, 4), blob.name
