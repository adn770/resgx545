# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""usse-asm: assemble USSE text as usse-dis prints it.

Every form of the decoder's table is checked through the made-up word that
tools/usse-dis/pinned.tsv pins for it: its text assembles to the pinned word
itself, unless that word sets bits its form ignores; then to the canonical word,
which the decoder prints as the same text. The other tests use texts of our own
choosing; the expected words are either encodings the instruction set fixes
completely (nop.end) or the assembler's own output for the canonical spelling.
"""
import subprocess

from conftest import DIS_DIR, HERE

PINNED = DIS_DIR / "pinned.tsv"

# Forms whose pinned word carries bits the form ignores (pingen keeps the best-spread
# word); their texts assemble to the canonical word instead, which decodes the same.
CANONICALISED = {128, 145, 146, 147, 148, 159, 160, 173, 199, 208}


def pinned(isa):
    """(form index, word, text) of the pinned words of one instruction set."""
    rows = []
    for line in PINNED.read_text().splitlines():
        if line and not line.startswith("#"):
            which, form, word, text = line.split("\t")
            if which == isa:
                rows.append((int(form), int(word, 16), text))
    return rows


def test_every_pinned_form_assembles(usse_asm, usse_dis):
    rows = pinned("usse")
    assert len(rows) > 200
    words = usse_asm("\n".join(t for _, _, t in rows))
    assert usse_dis(words) == [t for _, _, t in rows]
    assert {f for (f, w, _), got in zip(rows, words) if got != w} == CANONICALISED


def test_canonical_words_are_a_fixed_point(usse_asm, usse_dis):
    """Assembling the decode of an assembled word gives the word back."""
    words = usse_asm("\n".join(t for _, _, t in pinned("usse")))
    assert usse_asm("\n".join(usse_dis(words))) == words


def test_more_forms_round_trip(usse_asm, usse_dis):
    texts = ["phas #16, #4, pixel, end, perinstance", "phas r1, r1",
             "p3 mov.end o0, #0x00000000", "mov.skipinv.end i.lh, #0x00000000",
             "mov.skipinv.end o[il + #0], #0x00000000", "mov.end.repeat2 r0, r0",
             "mov.skipinv.end o0.xy, pa0", "nop.syncs.nosched.end.tog.trigger",
             "!p0 and r2, r2, ~#0x00040000", "ldad.bpcache.fetch4 r3, [r2,+#1], drc0",
             "stad.bpcache.fetch2 [r1,#82++], r5", "br -#0x00000010", "ba.savelink #0x00000123",
             "ldr r9, #372, drc0", "str #372, i2", "ima32.u r0, r0, r0, r0",
             "idiv.repeat9 r18, r1, r2, drc0", "idiv.skipinv.repeat16 r18, r1, r2, drc1"]
    assert usse_dis(usse_asm("\n".join(texts))) == texts


def test_lenient_spelling(usse_asm):
    src = """
        ; a comment line
        mov.skipinv.end   o0 ,#0x1234abcd     ; lower-case hex, odd blanks
        mov.skipinv r3, #0                    ; decimal for a hex field
        emitpix1.freep #0, r0, r1             /* the incp comment may go */
    """
    assert usse_asm(src) == usse_asm("mov.skipinv.end o0, #0x1234ABCD\n"
                                     "mov.skipinv r3, #0x00000000\n"
                                     "emitpix1.freep #0 /* incp */, r0, r1\n")


def test_listing_input(usse_asm):
    """usse-dis output assembles back: the index and hex columns are ignored."""
    src = "     0: 0x0123456789ABCDEF\tphas #0, #0, pixel, end, parallel\n" \
          "     1: 0x0000000000000000\tnop.end\n"
    assert usse_asm(src) == usse_asm("phas #0, #0, pixel, end, parallel\nnop.end\n")


def test_raw_words(usse_asm):
    assert usse_asm(".long 0x0123456789ABCDEF") == [0x0123456789ABCDEF]


def test_listing_output(usse_asm, tmp_path):
    (tmp_path / "l.s").write_text("nop.end\n")
    r = subprocess.run([str(HERE / "usse-asm"), "-l", "-o", str(tmp_path / "l.bin"),
                        str(tmp_path / "l.s")], capture_output=True, text=True, check=True)
    assert r.stdout == "     0: 0xF804014000000000\tnop.end\n"


def test_errors_name_the_line(usse_asm):
    r = usse_asm("nop.end\nfrobnicate r0\n", check=False)
    assert r.returncode == 1
    assert ":2: cannot assemble 'frobnicate r0'" in r.stderr


def test_out_of_range_is_refused(usse_asm):
    assert usse_asm("mov r128, #0", check=False).returncode == 1
    assert usse_asm("phas #262144, #0, pixel, end, parallel", check=False).returncode == 1


def test_canonical_choice_is_stable(usse_asm, usse_dis):
    """mov r0, r0 has a write-mask and a repeat encoding; the first form wins."""
    (w,) = usse_asm("mov r0, r0")
    assert usse_dis([w]) == ["mov r0, r0"]
    assert not w >> 53 & 1 and w >> 44 & 0xF == 1      # mask form, x only
    assert usse_asm("mov r0, r0") == [w]


def test_labels(usse_asm):
    """ba takes a label as an absolute instruction index; br only a number."""
    src = "start:\n nop\n ba #start\n ba.savelink #end\nend:\n nop.end\n"
    assert usse_asm(src)[1:3] == [0xF800000000000000, 0xF800020000000003]
    assert usse_asm("x:\n br #x\n", check=False).returncode == 1


def test_upper_case_hex_prefix(usse_asm):
    assert usse_asm(".long 0X0123456789ABCDEF") == [0x0123456789ABCDEF]
    assert usse_asm("     0: 0X0000000000000000\tnop.end\n") == usse_asm("nop.end")


def test_a_label_defined_twice_is_refused(usse_asm):
    r = usse_asm("x: nop\nx: nop\n", check=False)
    assert r.returncode == 1 and ":2: label 'x' defined twice" in r.stderr
