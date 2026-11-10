+++
id = "E737"
claim = "Flipping bits of the index list header (VDM word 2) of E414's five-copy job (15 vertices, 16-bit indices) breaks the job, 2 of 2 runs each: bit 24 alone hangs it (job hung, recovering; 1 event seen), bit 25 alone and bits 24 and 25 together fault it (BIF fault 0xd0008 at 0x1, 0 events seen, the same word in 4 of 4), while the unflipped control reproduced E414's object (15 vertices, 67 dwords); the frozen verdict is HH for bit 24 and HW's signature (a fault) for bit 25 and for both, which by the proposal earns the positive test of a 32-bit index buffer"
unit = "vdm"
method = "S1 stage g-e4 (7 jobs, 4 conditions; paths relative to render/closing-s1/ of the dataset: probe --tri pixel --vertices 15 --copy-depth --dump-render --pixels with --vdm 2^=0x01000000, 0x02000000 or 0x03000000, two runs each, the control unflipped), hangs and faults declared as hypotheses and measured (runner knob hypo:GROUP:2), a debugfs reset before each job and a recovery after each failed one, on the laptop (direct cable), 2026-11-09, kernel 7.3.0-resgx545, module B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1 (sha256 d776afbc...); the flipped word checked offline against the tool's mock (tests/emit_checks.py); frozen before the stage; scored by the frozen score/score_s1.py g-e4 (out/score-g-e4.txt); the kernel lines read from the kept per-job dmesg slices"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["render-closing-s1:out/g-e4/"]
terms = ["VDM_INDEX0.PRIMITIVE_TOPOLOGY", "VDM_INDEX0.WORDS_PRESENT", "CR_BIF_FAULT"]
+++
**What ran.** Q112 asks what bits 25:24 of the index list header do (clear in every captured list)
and whether the TA takes indices wider than 16 bits. The control is E414's five-copy job, unflipped;
each flip ran twice. Frozen hypotheses: HW (the bits select wider indices: the 16-bit buffer read as
32-bit indices fetches far vertices, a changed object or a fault), HN (no effect), HH (a hang).

**Frozen verdict.** control ok; ix-24: HH (hang in 2 of 2); ix-25: HW signature (fault in 2 of 2);
ix-2425: HW signature (fault in 2 of 2) (out/score-g-e4.txt).

**Results [HW].** Control: object present, 15 vertices, 67 object dwords, rc 0. Bit 24: rc 3, `job
hung, context lost`, the kernel's `job N hung, recovering` with "SGX stopped, 1 events seen", 2 of
2. Bit 25 and bits 24+25: rc 3, `job faulted, context lost`, `BIF fault 0xd0008 at 0x1 (PD ...)
stalls job N, recovering` with "0 events seen", 4 of 4. Every recovery returned (EDM up after 132 to
231 us in five of them and 1779 us in one) and the health triangle after the stage was exact.

**Reading [infer].** The two bits do different things, so they are not read as one field whose
two non-zero values both mean "wider": a hang for 24, a fault for 25 whatever 24 holds. The fault
is what HW predicted for a 16-bit list read as 32-bit indices (index pairs such as 0x00010000 read
as one index point far past the vertex buffer); the address 0x1 and the word 0xd0008 are not decoded
here (no landed record shows 0xd0008; 0xd0400 at 0x1 appears in E707). A fault does not
show that the bit selects the width: that is the positive test (a 32-bit index buffer with the bit
set must give the five-copy object back, and the unflipped header over it must break).

**Not shown.** Which bit, if either, is the width select; what bit 24's hang waits on; whether the
wider read is what faults.

**Correction 2026-11-10:** The reading above that the fault is the signature the width hypothesis
predicted for bit 25 is refuted by S1b's g-e4w (E756): with the index list written as 32-bit words
and bit 25 set the job faulted at BIF fault 0xd0008 at 0x1 exactly as over the 16-bit list (1 run
each; the frozen HW32 predicted E414's object and was refuted, HX consistent), and with bit 25
cleared the 32-bit list was read as 16-bit. Bit 25 is not a 32-bit index select. Also, 0xd0008 is
not in no other record: the published kernel log of usse/output-room-vdm holds 16 lines of BIF fault
0xd0008 (at 0xc100002, 0xb000001 and others), from jobs of another table; that it is the same
requestor is not shown.
