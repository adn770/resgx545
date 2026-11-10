+++
id = "E756"
claim = "With the index list of E414's five-triangle job (15 vertices) written as 32-bit words (the tool's --index-width 32, which sets bit 25 of VDM word 2 itself), the job faulted at BIF fault 0xd0008 at 0x1 with 0 events seen (1 run), as it did with bit 24 set as well (1 run) and as the control with the 16-bit list and bit 25 does (ix-25, 1 run, the fault of S1's g-e4 in 2 of 2): bit 25 does not select a 32-bit index width (the frozen HW32, predicted to draw E414's object, refuted in these 2 of 4 told rows; the frozen HX, bit 25 is something else, consistent in 4 of 4); with bit 25 cleared by a flip over the 32-bit list (ix32-n, 2 of 2) the job completed with an object of 5 vertices (30 object dwords, against 15 vertices and 67 dwords of the 16-bit control ix-c) and an image of background only (4096 of 4096 pixels), which both frozen models predicted (not the control's object) and which is what a 32-bit list read as 16-bit indices gives (0, 0, 1, 0, 2, 0, ... name vertices 0 to 4); the two faulting conditions each ran once, because the stage's hypothesis limit skipped their replicates"
unit = "vdm"
method = "S1b stage g-e4w of the question-closing pass (8 jobs; probe --tri pixel --vertices 15 --copy-depth --dump-render --pixels with the green pixel program: ix-c the control with the 16-bit list (E414's five triangles, 15 vertices); ix32-n twice, --index-width 32 (the 32-bit list 0..14 written as 32-bit words, VDM word 2 bit 25 set by the option) and --vdm 2^=0x02000000 (bit 25 cleared again); ix32-25 and ix32-2425, --index-width 32 alone and with --vdm 2^=0x01000000 (bits 25 and 24 set), each with a replicate row that the runner skipped (cases.tsv: rc -, class skipped) after the group's one hypothesis event; ix-25 last, the 16-bit list with --vdm 2^=0x02000000, the control that faults); the knob proof is the probe's '32-bit indices' echo of the 32-bit jobs (the scorer voids a job without it) and the echoed VDM words; on the laptop (direct cable), 2026-11-10, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71, built from main with the --index-width option, whose words were checked against the tool's mock before the run); a debugfs reset before each job; tables, predictions, scorer and runner frozen before the session (FROZEN.sha256, PREDICTIONS.sha256); scored by the frozen score/score_s1.py g-e4w (out/score-g-e4w.txt, re-run from the dataset with the same output); the faults are read from the kernel log slice of each job"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-s1b:out/g-e4w/"]
terms = ["VDM_INDEX0.PRIMITIVE_TOPOLOGY", "VDM_INDEX0.WORDS_PRESENT", "CR_BIF_FAULT"]
+++
**What ran.** E737 (S1) found that bit 25 of the index list header faults the job at BIF fault
0xd0008 (2 of 2 alone, 2 of 2 with bit 24), and that bit 24 alone hangs it, over the 16-bit index
list. A fault does not show that the bit selects the index width, so S1b ran the positive test S1
named: the list written as 32-bit words, with the bit set. HW32 (bit 25 selects 32-bit indices)
predicted E414's object word for word with the bit set (ix32-25) and a different object with it
cleared (ix32-n), and "same or hang" with bit 24 as well; HX (bit 25 is something else) predicted
the fault of the 16-bit job whatever the list width. ix32-n does not separate the two (both
predict a changed object); ix32-25 does. The tool change (`--index-width 32`) sets bit 25 itself,
so the hypothesis under test is built into the option; the xor in ix32-n takes it away.

**Frozen verdict.** `controls ok; ix32-n: ['changed', 'changed']; ix32-25: ['fault 0xd0008',
'void: skipped (hypothesis limit of its group or stage)']; ix32-2425: ['fault 0xd0008', 'void:
skipped (hypothesis limit of its group or stage)']; held out: consistent ['HX (4)'], refuted
['HW32 (2 of 4)']; repeat only: consistent none, refuted none` (out/score-g-e4w.txt). The control
ix-c gave E414's object (15 vertices, o0 x2998 and green x1098 pixels) and ix-25 faulted 0xd0008,
S1's word, as frozen. The "(4)" and "2 of 4" count the told rows: ix32-n twice (both models hit)
and the two single faulting runs (HW32 misses, HX hits).

**Results [HW].** ix32-25-r1, ix32-2425-r1 and ix-25 each: `BIF fault 0xd0008 at 0x1 ... stalls
job N, recovering`, `SGX stopped, 0 events seen`, then a reset to EVENT_STATUS 0x20000000/0x480;
the tool reported `job faulted, context lost`. The replicates of the two 32-bit faulting
conditions were skipped by the per-group limit of one event ("group ix32-25 reached its 1
events"), so each stands on one run. ix32-n-r1 and -r2: rc 0, an object of 5 vertices and 30
dwords (ix-c: 15 and 67) whose first dwords equal the control's header words, and every pixel of
the 64 x 64 image the background. Health after the stage fine; no other kernel-log error.

**Post hoc (read after the run; [infer], not held out).** The fault is the same with a 16-bit and
with a 32-bit list, so its cause does not depend on the list width; bit 25 is not the width select
in the sense HW32 states it, and the fault is at address 0x1 with zero events seen. The 5-vertex
object of ix32-n is the one a list read at 16-bit width gives (indices 0, 0, 1, 0, 2, 0, ... hold
the vertices 0 to 4): with bit 25 clear the TA reads this list as 16-bit, which also shows the
tool's 32-bit list was written as intended. 0xd0008 is not new to this stage: it is in the
published kernel log of usse/output-room-vdm (16 lines, jobs 9671 and 9731 among them, at
addresses 0xc100002 and 0xb000001), which Q112's "in no other record" and E737 did not know; there
it comes from a different table, so the word names a requestor and a type, not this header bit.

**Not shown.** Whether any header bit, or any other field, makes the TA read 32-bit indices (the
test ran one candidate, bit 25, with the list at 32-bit width; bit 24's hang was not tried over a
32-bit list), what bit 24 waits on, whether the 0xd0008 of this stage and of output-room-vdm name
the same requestor (the fault address 0x1 against 0xc100002 differs), anything about two faulting
runs per condition (each ran once), and indices above 16 bits in any form.