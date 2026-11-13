+++
id = "E964"
claim = "R9-faults stage xf2 (Q108; a fill's destination and a copy's read-only source with one PTE flag, 12 jobs, every control passed, E946's nine rows rerun token for token): WRITEONLY on a fill's destination let every pixel land and faulted the job at the page of the last pixel written, BIF_INT_STAT 0x80020 with SB 31, at 64 x 32 (page 0x3e002000), at 64 x 16 from row 16 (0x3e002000, the mapping's first page never written) and at 64 x 64 (0x3e004000), never at the mapping's first or last page; EDMPROTECT let a copy's texture read of its READONLY source through (PTE 0x14, exact) and faulted a fill's write at its first page (0xa0020, nothing written); E946's other rows read as post hoc (CACHECONSISTENT on the copy's source exact, READONLY with WRITEONLY on it 0x80002); frozen verdicts 'H-LASTROW (2 of 2 rows decided)' with H-MAPEND and H-FIRST '0 held, 2 FAILED', 'H-EDM-WRITE ... (1 of 1 rows decided)' with H-EDM-REQ '0 held, 1 FAILED', 'H-WO-ALL (4 of 4 rows decided)', 'H-CC-NEW (1 of 1 rows decided)', 'H-EDM-CLIENT (1 of 1 rows decided)'"
unit = "bif"
method = "R9-faults stage xf2 of the question-closing pass, round 9 (decision S-6 (a) of closing9/DECISIONS-R9.md; plan closing9/seeds/exp-seeds-r9.md section 2, session S9-k2), on the laptop (host cedar), 2026-11-13, one attempt out/20261113-084720 (dataset render-closing-r9-faults; lead log out/run-r9f.log; no stop, no lead decision; xf2 from 08:47, tri2 from 08:50, bif from 08:51 Mac time), kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (the linux fork r8-kernel at 2a650d74: debugfs vm_pte_flags, vm_pte_addr, alias_skip (commit 42) and render_pb_pages; the round 9 test boot, installed = loaded, every knob at its default at each stage start), stock firmware, tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., resgx545 4623753 bound by source, TOOLSRC.sha256, recipe userspace/libsgxfive/Makefile; every row replayed on the library mock before the run, none refused), built on the session kit of resgx545 f32dfac (kit/run_stage.sh with run/hooks.sh: a debugfs reset before each job, the row's knobs written and read back before it and restored after it, the kernel's recovery then the kit's reset and strict health fill and triangle after every fault and every knob row, all drawing at the first try; no SGX recovery failed line); frozen before the first job: FROZEN.sha256 675739af..., PREDICTIONS.sha256 ae76ed3f..., FROZEN.commits (kit and replay inputs at resgx545 f32dfac, control outputs at data 2d666bfa); scored by the frozen score/score.py (out/ATT/score-STAGE.txt), re-run at the fold on the kept files with byte-identical output, every kept file decompressing to the raw sha256 the laptop logged (fold/reproduce.sh, reproduce.out). Each knob row set vm_pte_addr to the first page of one mapping the tool makes (0x3e001000: a fill's destination, 3 pages for 64 x 32 and for 64 x 16 at y 16 (y + h rows and a guard), 5 for 64 x 64; a copy's read-only source, 3 pages) and vm_pte_flags to one flag; its premise, the kernel's vm_map A +S: PTE flags F line with the frozen flags, was read in every knob row. Outcomes as frozen (gen/make.py, score/score.py): exact (job ok, diff 0, the row's reference hash: the knob-free control's, or the library mock's fill hash for the two new sizes), diff, fault and fault@PAGE (the first BIF fault line whose page lies in the mapping). Rows xf-c-fill, xf-c-copy, xf-c-addr, xf-c-ro (the tool's isolation, a control whose own faults #limit does not count), xf-wo-fill, xf-cc-copy, xf-edm-fill, xf-wo-copy, xf-c-end (E946's, token for token), xf-wo-fill-low (fill --width 64 --height 16 --y 16), xf-wo-fill-64 (fill --width 64 --height 64), xf-edm-copy (copy --print-addrs); 5 faults of the rows and the isolation control's 3 against the stage's #limit 8, no stop"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r9-faults:out/20261113-084720/xf2/", "render-closing-r9-faults:fold/", "vectors-closing-r9-faults-pte"]
terms = ["CR_BIF_FAULT", "CR_BIF_INT_STAT"]
+++
**What ran.** E946's transfer rows were gated cannot tell: the stage's fourth fault, counting the
isolation control's own, stopped it before its end control (the kit now leaves a control's
expected fault out of #limit). Stage xf2 reran those nine rows token for token, so their frozen
predictions are E946's and their readings are not blind (E946 had read them post hoc), then
three held-out rows: WRITEONLY on a fill that writes only the second page of its mapping (64 x
16 from row 16), WRITEONLY on a 64 x 64 fill (four pages of image), and EDMPROTECT on a copy's
source, which the copy maps READONLY (PTE 0x14). The frozen rivals for WRITEONLY's fault page:
H-LASTROW (the page of the last pixel written; E945 and E946 post hoc), H-MAPEND (the mapping's
last page, the guard) and H-FIRST (its first page). For EDMPROTECT on a read: H-EDM-WRITE (client
writes fault, reads pass) against H-EDM-REQ (every access of the transfer faults).

**Frozen verdict (as printed).**

- `Q108 WO-PAGE, H-LASTROW: a WRITEONLY write faults at the page of the last pixel written (E946
  post hoc: xf-wo-fill at 0x3e002000; E945 tri-wo-fb at 0x3e004000) (S9-k2, frozen) (2 of 2 rows
  decided)`; H-MAPEND and H-FIRST `is not supported: 0 held, 2 FAILED, 0 cannot tell of 2`.
- `Q108 EDM-XF, H-EDM-WRITE: EDMPROTECT faults every client write and no client read (E945: the
  colour write faulted, the VDM's reads did not) (S9-k2, frozen) (1 of 1 rows decided)`; H-EDM-REQ
  `0 held, 1 FAILED`.
- E946's groups over every row: `H-WO-ALL: WRITEONLY faults every access (rival) (4 of 4 rows
  decided)` (H-WO `1 held, 3 FAILED`, H-WO-NONE `0 held, 4 FAILED`); `H-CC-NEW (1 of 1 rows
  decided)`; `H-EDM-CLIENT (1 of 1 rows decided)` (H-EDM-NONE `0 held, 1 FAILED`).

Every control passed, xf-c-end included.

**Results [HW].**

| row | flag (PTE) on | job | image | BIF_INT_STAT | BIF_FAULT (page, SB, CID) |
|---|---|---|---|---|---|
| xf-wo-fill | fill 64 x 32 (0x2) | faulted | exact | 0x80020 | 0x3e0021f1 (0x3e002000, last pixel's; 31; 1) |
| xf-cc-copy | copy source (0xc) | ok | exact | - | - |
| xf-edm-fill | fill 64 x 32 (0x10) | faulted | nothing written | 0xa0020 | 0x3e001001 (first; 0; 1) |
| xf-wo-copy | copy source (0x6) | faulted | nothing written | 0x80002 | 0x3e001001 (first; 0; 1) |
| xf-wo-fill-low | fill 64 x 16 at y 16 (0x2) | faulted | exact | 0x80020 | 0x3e0021f1 (0x3e002000, last pixel's; 31; 1) |
| xf-wo-fill-64 | fill 64 x 64 (0x2) | faulted | exact | 0x80020 | 0x3e0041f1 (0x3e004000, last pixel's; 31; 1) |
| xf-edm-copy | copy source (0x14) | ok | exact | - | - |

The isolation control read its nine checks PASS and its three faults (the last 0x80020 at
0x3e200002), and the kernel banned its file after the third, as before (render/client-jobs).
Each fault was the kernel's `BIF fault ... stalls job N, recovering`; the kit's health drew
exactly at the first try after every row. The 64 x 16 and 64 x 64 fills' images hash as the
library mock's (0x1b53c7736b16fb25, 0xc3ac149063f58325).

**What it shows.** [HW] WRITEONLY on a fill's destination faults the job at the page of the last
pixel written, after the writes land, with SB 31: held out at two sizes, and at 64 x 16 from row
16 the mapping's first page, never written, is not the one named (H-FIRST refuted), nor is the
guard page at the mapping's end (H-MAPEND refuted). EDMPROTECT does not stop a transfer's texture
read of its source (the copy exact with PTE 0x14) and stops its pixel write at the first page.
[infer] As E945 read it: something of the pixel side reads the last page it wrote, and that
read faults; the access stays the write's requestor bit 5.

**What it does not show.** WRITEONLY alone on a texture read (the copy maps its source READONLY);
EDMPROTECT on a texture read without READONLY; which unit makes the last-page access;
CACHECONSISTENT on data cached before the host's write.
