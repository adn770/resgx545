+++
id = "E965"
claim = "R9-faults stage tri2 (Q108; the 64 x 64 triangle with PTE flags on its colour target or the ZLS buffers of tri --depth --depth-store, 7 renders, the three knob-free controls passed): WRITEONLY and EDMPROTECT together (0x12) on the colour target faulted as EDMPROTECT alone (0xa0020 at the target's first page, nothing written; E945's WRITEONLY fault came after the image, at its last page); EDMPROTECT on the depth store's buffer faulted the ZLS store at its first page (0xa0200, FAULT_REQ bit 9, nothing stored, no pixel written); WRITEONLY there let the whole store land (4096 dwords) and faulted at the store window's last page (0x80200 at 0x3e018001, SB 0); EDMPROTECT on the depth buffer, which the clearing control does not load, changed nothing (exact); frozen verdicts 'H-OR ... (1 of 1 rows decided)' (H-CANCEL '0 held, 1 FAILED'), 'H-EDM-FIRST ... (1 of 1 rows decided)' (H-WO-FIRST '0 held, 1 FAILED'), 'H-EDM-WRITE ... (1 of 1 rows decided)' (H-EDM-3D '0 held, 1 FAILED'), 'H-WO-ALL (1 of 1 rows decided)'"
unit = "bif"
method = "R9-faults stage tri2 of the question-closing pass, round 9 (decision S-6 (a) of closing9/DECISIONS-R9.md; plan closing9/seeds/exp-seeds-r9.md section 2, session S9-k2), on the laptop (host cedar), 2026-11-13, one attempt out/20261113-084720 (dataset render-closing-r9-faults; lead log out/run-r9f.log; no stop, no lead decision; xf2 from 08:47, tri2 from 08:50, bif from 08:51 Mac time), kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (the linux fork r8-kernel at 2a650d74: debugfs vm_pte_flags, vm_pte_addr, alias_skip (commit 42) and render_pb_pages; the round 9 test boot, installed = loaded, every knob at its default at each stage start), stock firmware, tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., resgx545 4623753 bound by source, TOOLSRC.sha256, recipe userspace/libsgxfive/Makefile; every row replayed on the library mock before the run, none refused), built on the session kit of resgx545 f32dfac (kit/run_stage.sh with run/hooks.sh: a debugfs reset before each job, the row's knobs written and read back before it and restored after it, the kernel's recovery then the kit's reset and strict health fill and triangle after every fault and every knob row, all drawing at the first try; no SGX recovery failed line); frozen before the first job: FROZEN.sha256 675739af..., PREDICTIONS.sha256 ae76ed3f..., FROZEN.commits (kit and replay inputs at resgx545 f32dfac, control outputs at data 2d666bfa); scored by the frozen score/score.py (out/ATT/score-STAGE.txt), re-run at the fold on the kept files with byte-identical output, every kept file decompressing to the raw sha256 the laptop logged (fold/reproduce.sh, reproduce.out). Each knob row set vm_pte_addr to the first page of one mapping the tool makes (0x3e001000: the 64 x 64 colour target of tri, 5 pages, or the depth buffer of tri --depth --depth-store, 20 pages; 0x3e015000: the depth store's buffer, 20 pages; the colour target of the depth jobs at 0x3e029000, read from the tool's source on the library mock) and vm_pte_flags (0x12, 0x10 or 0x2); the kernel's PTE line with the frozen flags was read in every knob row. The depth jobs' ZLS pokes: control 0x0017100c (bit 1, the load, clear: doc/specs/3d.md section 11.5), load base the depth buffer, store base the store's buffer. Outcomes as frozen: exact (job ok, diff 0, the knob-free control's hash, tri-c-depth's as read for the depth rows), fault and fault@PAGE (the first BIF fault line whose page lies in the mapping). Rows tri-c, tri-c-depth (job ok, fb 0x3e029000, 4096 stored dwords changed, E465's window of 8 tiles of 512), tri-woedm-fb, tri-edm-dst, tri-edm-dld (a reading row), tri-wo-dst, tri-c-end; 3 faults against the stage's #limit 5, no stop"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r9-faults:out/20261113-084720/tri2/", "render-closing-r9-faults:fold/", "vectors-closing-r9-faults-pte"]
terms = ["CR_BIF_FAULT", "CR_BIF_INT_STAT"]
+++
**What ran.** E945 put one flag at a time on a 64 x 64 render's colour target or GENERAL page.
Stage tri2 held out the open cases: WRITEONLY and EDMPROTECT together on the colour target, and
EDMPROTECT and WRITEONLY on the buffers of the ZLS (tri --depth --depth-store: the depth buffer,
the load base, and a separate store buffer). Frozen rivals: H-OR (together they fault, as each
does alone) against H-CANCEL, with H-EDM-FIRST (the fault is EDMPROTECT's, at the first page,
nothing written) against H-WO-FIRST (WRITEONLY's, at the last page after the image), neither
favoured; H-EDM-WRITE (every client write faults: the ZLS store too) against H-EDM-3D (only the
pixel back end's colour write); and E945's WRITEONLY groups on the store. The depth buffer's row
was frozen as a reading: the clearing control loads nothing, so both EDMPROTECT rivals predict
it exact.

**Frozen verdict (as printed).**

- `Q108 WO+EDM, H-OR: WRITEONLY and EDMPROTECT together fault the colour write, as each does alone
  (E945) (S9-k2, frozen) (1 of 1 rows decided)`; H-CANCEL `0 held, 1 FAILED`.
- `Q108 WO+EDM-PAGE, H-EDM-FIRST: together, the fault is EDMPROTECT's: at the target's first
  page, before the image is written (E945 tri-edm-fb at 0x3e001001) (rival, not favoured) (1 of 1
  rows decided)`; H-WO-FIRST `0 held, 1 FAILED`.
- `Q108 EDM-3D, H-EDM-WRITE: EDMPROTECT faults every client write and no client read (E945: the
  colour write faulted, the VDM's reads did not) (S9-k2, frozen) (1 of 1 rows decided)`;
  H-EDM-3D `0 held, 1 FAILED`.
- `Q108 WRITEONLY, H-WO-ALL: WRITEONLY faults every access (rival) (1 of 1 rows decided)`; H-WO
  and H-WO-NONE `0 held, 1 FAILED`.

All three controls passed (tri-c and tri-c-end r7-rp's health triangle; tri-c-depth job ok, fb
0x3e029000, 4096 store dwords changed, image hash 0x99385a04ee01c585 as the plain triangle's).

**Results [HW].**

| row | flags on | job | image | ZLS store | BIF_INT_STAT | BIF_FAULT (page, SB, CID) |
|---|---|---|---|---|---|---|
| tri-woedm-fb | colour target (0x12) | faulted | nothing written | - | 0xa0020 | 0x3e001001 (first; 0; 1) |
| tri-edm-dst | store buffer (0x10) | faulted | nothing written | nothing stored | 0xa0200 | 0x3e015001 (first; 0; 1) |
| tri-edm-dld | depth buffer (0x10) | ok | exact | 4096 stored | - | - |
| tri-wo-dst | store buffer (0x2) | faulted | 512 of 4096 right | 4096 stored | 0x80200 | 0x3e018001 (0x3e018000, the window's last; 0; 1) |

The kit's health drew exactly at the first try after every row.

**Read after the run (post hoc).** tri-wo-dst's image is right in 512 pixels, the first wrong
one at (32, 0): the first 32 x 16 tile [infer]. Its store holds every dword of the 64 x 64
window (16 KiB from 0x3e015000), and the page named is that window's last, so WRITEONLY on the
store behaves as on a colour target: the writes land, then the fault names the last page
written; here SB is 0, not 31. FAULT_REQ bit 9 (0x200) is the ZLS store's [infer: from the
access set up, as hw_spec.md section 5.5 reads every bit].

**What it shows.** [HW] With both flags on the colour target the job faults as with EDMPROTECT
alone, at the first page before any pixel is written (H-EDM-FIRST). EDMPROTECT faults the ZLS
store's write at its first page (FAULT_TYPE 2, requestor bit 9), so it stops client writes
beyond the pixel back end's colour write (H-EDM-WRITE over H-EDM-3D). WRITEONLY on the store
faults after the store landed, at the store window's last page.

**What it does not show.** EDMPROTECT or WRITEONLY on a depth load (the control here loads
nothing, and EDMPROTECT stops writes only, so tri-edm-dld says only that no client wrote the depth
buffer [infer]); the TA's own writes (parameter buffer, region headers); the EDM's buffers; why the
colour image stops after one tile under WRITEONLY on the store.
