+++
id = "E1073"
claim = "Round 18 offline (O18-1, Q139; no run): on E509's 329 kept cases (ta/mtile-fields and ta/mtile-fields-risky), the first kernel fault line of each of the 162 that faulted gives two kinds, 155 at 0x90100 (FAULT_REQ bit 8, page 0x10000, SB 1) and 7 at 0x90004 (FAULT_REQ bit 2, TA data pages 0x20008, 0x2000a and 0x20010); the form H-KIND (0x90004 iff an axis's bounds are all 0, n = 2: B2, n = 4: B1, B2 and B3, or the stride puts the last macrotile at or past slot 3072; else 0x90100), fitted post hoc on those lines, gives 162 of 162, and its rival H-ONE-KIND (every faulting word 0x90100) 155 of 162 (95.7 %); the stride clause rests on one case; frozen by the sha256 of fit/o18_1.py before r18-flag ran, which held it out (E1074)"
unit = "ta"
method = "Offline, no run: O18-1 of closing18/plan/rank-round18.md (section 2, f3), round 18 (closing18/DECISIONS-R18.md, R18-3 (a): f3 is built only if a form fits at least 95 % of E509's faulting kinds). fit/o18_1.py of render/closing-r18-flag (sha256 b1829c2c958fa67b72c05e0d0cf36186f568660f79de9ca239d88082bd823cb1, standard library only) reads ta/mtile-fields{,-risky}/cases.tsv and kernel.log at resgx545-data 45423fbc3 (git show), takes each case's first 'sgxfive: BIF fault S at A' line after its 'resgx545 case NAME' marker (the later lines of a case are its health triangles), decodes each case's words with r10-geo's q139_fit reading (n = 4 iff CR_TE_MTILE1 bit 31; bounds B1 bits 29:22, B2 21:12, B3 11:0 per axis; the stride ta:146 or the rule's mx my) and prints each form's count (fit/o18_1.out, its last line the form file's sha256); the session's tests/test_gen.py checks the output current. Written and frozen before the session's freeze (FROZEN.sha256 of r18-flag names fit/o18_1.py and fit/o18_1.out)"
tiers = ["HW", "infer"]
date = "2026-11-14"
data = ["ta-mtile-fields", "ta-mtile-fields-risky", "render-closing-r18-flag:fit/"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE", "CR_BIF_INT_STAT"]
+++
**What ran.** No laptop run. E509's two datasets were read again for the one thing their records
never used: the fault line of each faulting case. A case's first fault line is its own job's; the
later lines of a case (three at 640 x 480 with an all-zero word or stride 256) are its health
triangles failing twice before the third drew. Two forms were written against those lines and the
rule of the plan applied: f3 is built only if a form reaches 95 %.

**Results [HW].** 329 cases, 162 faulting: 155 with 0x90100 at 0x10000011 to 0x10000018 (page
0x10000, `SB` 1, the list varying), 7 with 0x90004: the x-side all-zero words at 256 x 256
(m1-B2-0, part1-0_0_0: page 0x20008) and 640 x 480 (part1-0_0_0: 0x2000a), the y-side ones at both
sizes (m2-B2-0, part2-0_0_0: 0x20010) and stride 256 at 640 x 480 (0x2000a). H-KIND 162 of 162,
H-ONE-KIND 155 of 162; the rule held, so f3 was built.

**What it shows.** [infer, post hoc] Which kind a faulting word gives follows its bounds: an axis
whose bounds are all 0 (every tile in its last macrotile) faults the TA's region header write
(0x90004, hw_spec 5.5's TA write past the kernel's layout), and the other faulting words fault the
3D's read at the parameter heap's first page (0x90100: a header with a zero stream offset, E869
[infer]). E1074 held the kind out on two words at a new size.

**What it does not show.** The page of a 0x90004 fault: E509's module (14D09986) kept no layout,
and the page did not follow the end of the TA data on B60AB0B4 (E1074). Nor whether a word faults
at all; that is E1048's H-COVER, post hoc. The stride clause is one case.
