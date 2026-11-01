# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The decoders over the user's own closed programs, read at run time.

The private data repository (tools/records datasets.repos(): $RESGX545_DATA_PRIVATE or a
sibling resgx545-data-private) holds the firmware images the cutter reproduces
(firmware/images: the microkernel and the five EDM PDS programs) and the transfer captures
(firmware/transfer, read with tools/fwcutter/tqcapture.py). Every instruction of those
programs must decode, and every form they use must be among the made-up words pinned by
test_forms.py and test_pds.py. No word or text of a closed program is stored here: the
tests check counts and form indices only, and skip without the data.
"""
import pathlib
import struct
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "fwcutter"), str(HERE.parent / "records")]
import datasets  # noqa: E402
import facts  # noqa: E402

import test_forms  # noqa: E402
import test_pds  # noqa: E402

PRIVATE = datasets.repos().get("data-private", pathlib.Path("/nonexistent"))
IMAGES = PRIVATE / "firmware" / "images" / "images"
TRANSFER = PRIVATE / "firmware" / "transfer"
SKIP = "SKIPPED, NOT PASSED: no {} in the private data repository; set RESGX545_DATA_PRIVATE"

needs_images = pytest.mark.skipif(not IMAGES.is_dir(), reason=SKIP.format("firmware images"))
needs_transfer = pytest.mark.skipif(not TRANSFER.is_dir(),
                                    reason=SKIP.format("transfer captures"))


@pytest.fixture(scope="module", autouse=True)
def build():
    subprocess.run(["make", "-s", "-C", str(HERE), "usse-dis", "pds-dis"], check=True)


def _which(tool: str, path: pathlib.Path, *extra: str) -> list[tuple[str, int]]:
    """(text, form index) of each instruction: -1 for an undecoded word; data dwords left out."""
    out = subprocess.run([str(HERE / tool), "--which", str(path), *extra], capture_output=True,
                         text=True, check=True).stdout
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) == 3:
            rows.append((parts[1], int(parts[2].lstrip("#"))))
    return rows


def _pinned_forms(tool: str, words: list[int], fmt: str, tmp_path: pathlib.Path,
                  *extra: str) -> set[int]:
    blob = tmp_path / "pinned.bin"
    blob.write_bytes(struct.pack(f"<{len(words)}{fmt}", *words))
    return {i for _, i in _which(tool, blob, *extra)}


def _edm_programs() -> list[tuple[pathlib.Path, int]]:
    """(image, data dwords) of the five EDM PDS programs: rows of four dwords (facts.py)."""
    rows = {facts.BUFFER_NAMES[b.id]: b.pds_rows for b in facts.BUFFERS}
    return [(p, rows[p.stem.split("_", 1)[1]] * 4) for p in sorted(IMAGES.glob("0[1-5]_pds*.bin"))]


@needs_images
def test_every_microkernel_word_decodes():
    uk = IMAGES / "00_ukernel.bin"
    rows = _which("usse-dis", uk)
    assert len(rows) == uk.stat().st_size // 8 > 6000
    assert sum(i < 0 for _, i in rows) == 0


@needs_images
def test_every_edm_pds_instruction_decodes_with_pinned_forms(tmp_path):
    progs = _edm_programs()
    assert len(progs) == 5
    used = set()
    for path, data in progs:
        rows = _which("pds-dis", path, str(data))
        assert rows and sum(i < 0 for _, i in rows) == 0, path.name
        used |= {i for _, i in rows}
    assert used <= _pinned_forms("pds-dis", list(test_pds.EDM_FORMS), "I", tmp_path, "0")


@needs_transfer
def test_every_transfer_use_instruction_decodes_with_pinned_forms(tmp_path):
    import tqcapture
    progs = {n: ps for n, ps in tqcapture.programs(tqcapture.load_capture(TRANSFER)).items()
             if n.startswith("USE")}
    assert progs
    used, n = set(), 0
    for name, copies in progs.items():
        for k, p in enumerate(copies):
            blob = tmp_path / f"{name}_{k}.bin"
            blob.write_bytes(p)
            rows = _which("usse-dis", blob)
            assert rows and sum(i < 0 for _, i in rows) == 0, name
            used |= {i for _, i in rows}
            n += len(rows)
    assert n > 0
    assert used <= _pinned_forms("usse-dis", list(test_forms.FORMS), "Q", tmp_path)
