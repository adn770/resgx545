+++
id = "E665"
claim = "The fields of CR_ISP_ZLSCTL that the records read (the pitch G in bits 11:3, bit 1 the load with bit 14 loading the depth and bit 13 the stencil, bit 2 with bit 18 the depth store and with bit 17 the stencil store, bit 19 the negation, bits 26:24 the depth format, bit 0 the colour image off) decode, in 47 vectors of the kind zls-ctl, as the records state them, with 0 differences: 15 matched (bit readings that use no address, pitch or format and no inferred load: bit 2 cleared, the five values the closed driver writes, nine of E467's ten controls), 23 fitted and 9 refused; the 32 single-bit flips of E411's 0x0017100c (bits 1, 12 to 16, 20 to 23 and 27 to 31 change no field, bit 2 clears both stores, bits 3 and 4 change G, 17 and 18 clear the stencil's and the depth's store, 19 negates, 24 selects the format 1) compare the pages of the 16-page scratch buffer that each flip stored in both runs of E411 (page 4 and 5 for the stencil, 12 to 15 for the depth) with the dwords the model's store writes (sums of 640 to 5120 dwords a flip, 0 pages different), so every flip that stores anything is fitted through E465's address rule, and a flip's pitch, a format or a load by bit 1 alone ([infer]: E411 part B saw no effect of bit 1 alone) makes a vector fitted as well; bit 0 stores what the control stores (the same pages in both runs: page 4 and pages 12 to 15, 5120 dwords, the same first values) and writes no colour pixel (4096 of 4096 pixels keep the sentinel), modelled for that one control, 0x0017100d, and refused (Q244) for any other control with bit 0 set, which nothing ran; the refused nine are the seven flips of bits 5 to 11, whose jobs faulted (the pitch running out of the scratch buffer, [infer]: Q242, refused in that arrangement and nowhere else), bit 25 (the 16-bit format at G = 1: its layout was derived at G = 33, Q242) and bit 26 (format 4, Q120); the bits set in no value and flipped in no run (bits 15 and 21 to 23 set together with others, any combination of the ignored bits) are not claimed, only the single flips"
unit = "zls"
method = "offline, no new run: sgx-pipe zls.rs Ctl, dword_sets and check_scratch_pitch and the unit kind zls-ctl of unitvec.rs against vectors that tools/usse-asm/zls_vectors.py makes from the bit tables of E411, E337 and E467 and from the per-page lines of control-bits/output.txt (the two runs of each flip must agree, the script asserts it): the fields of a flipped control are the bit arithmetic of the records' reading, the same arithmetic as the Rust decoder (flip_fields in the script, checked against itself by test_zls_vectors.py), so they are readings, not independent measurements; the pages are the run's own lines; a vector whose field, page count or key is changed fails, and a misspelled expectation key is a mismatch (tests/zls_vectors.rs); the tests of this fold were written first and shown failing, and the mutation list was rerun"
tiers = ["CAP", "HW", "infer"]
date = "2026-11-09"
data = ["zls-control-bits", "unit-vectors-12-4"]
terms = ["CR_ISP_ZLSCTL"]
+++

**What ran.** `zls::Ctl::decode` returns the fields (and refuses bit 0 with any control but
0x0017100d). The vectors compare each field the record states and leave the others out. A flip
vector also carries the pages E411 read back in its scratch arrangement (`arrangement =
"e411-scratch"`, a 64 x 64 target, a stencil buffer): the model's `dword_sets` gives the dwords
the store writes and the kind counts them per 1024-dword page, the stencil buffer from page 4 and
the depth buffer from page 12, of the 16 pages; a dword the model puts past page 15 was not seen
(bit 4's pitch of 4 tiles puts slots 8 to 13 there: the run shows pages 12 and 14 only).

**Results.** 15 matched, 23 fitted, 9 refused, 0 mismatches. Flip 3 (G = 0, tiles overlapping)
stores 640 + 1024 + 1024 + 512 = 3200 dwords in the run and 5 slots of 640 in the model; flip 4
stores 512 + 512 + 1024 + 1024 = 3072; flips 17 and 18 drop the stencil's 1024 or the depth's 4096;
24 stores 5120; the other flips store 5120 as the control. The 12.0 rule that a result on a fitted
rule is not matched is not bent: the vectors that compare a pitch, a format, a stored page or
a load by bit 1 alone are reported fitted, because E465, E466 and an [infer] reading stand under
them.

**Bit 0.** An earlier draft refused bit 0 saying it "wrote no pixel and what it stores was not
seen", and Q244 called that a contradiction with E411's table. It was not: the raw output of
control-bits (bit0-r1 and bit0-r2) shows bit 0 set stores exactly the control's pages in both runs
and leaves only the colour image unwritten. The refusal that remains is for what was not run: bit
0 together with any other control.

**Not what an earlier draft said.** The expectations were not "written by hand": the script makes
them from the bit arithmetic and the run's lines, and "no vector here uses E465's address rule" was
wrong for the vectors that compare pages, pitches or formats.

**An observation on E467 (corrected in the record by a dated paragraph, drafted apart).** E467 and
its script name 0x0011d10a "load only, bits 1, 13, 14 (0x11710a + 0x6000)". The sum carries:
0x11710a already has bits 12, 13 and 14 set, and adding 0x6000 gives 0x11d10a, with bits 12, 14 and
15 and bit 13 clear. The record's statement that a load-only control stores nothing holds for both;
the vector states only what the store enables say (bit 2 clear: nothing stored).

**What it does not show.** The effect of the ignored bits together; why the closed driver sets bits
12, 16 and 20 in every value; the stencil load (E467 saw it through the copy only); the faulted
jobs' cause; what reads the unpatched word between frames (Q088).
