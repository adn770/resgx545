+++
id = "E945"
claim = "R8-k2 stage tri (Q108; the 64 x 64 triangle with one PTE flag on its colour target or its GENERAL page, 7 renders, both knob-free controls exact): WRITEONLY faulted both rows, the colour target after the whole image was written (exact pixels, BIF_INT_STAT 0x80020 at the target's last page, SB 31) and the GENERAL page's read before anything was drawn (0x80008 at that page); CACHECONSISTENT on the GENERAL page changed nothing (exact); EDMPROTECT faulted the colour write at the target's first page (0xa0020, FAULT_TYPE 2, nothing written) and let the GENERAL page's read through (exact); frozen verdicts 'H-WO-ALL (WRITEONLY faults every access) (2 of 2 rows decided)', H-WO 'not supported: 1 held, 1 FAILED', H-WO-NONE 0 of 2, 'H-CC-NEW (1 of 1 rows decided)', H-CC-STALE refuted, H-EDM-NONE and H-EDM-CLIENT each '1 held, 1 FAILED' (EDMPROTECT stops the 3D's write, not the stream's read)"
unit = "bif"
method = "R8-k2 stage tri of the question-closing pass, round 8 (decisions R8-5 a and R8-6 a; plan closing8/rank/rank-round8.md section 3, K2), on the laptop (host cedar), 2026-11-13 03:24 to 03:28, one attempt out/20261113-032428 (dataset render-closing-r8-k2), kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 from the linux fork's branch r8-kernel at 2a650d74 (debugfs vm_pte_flags and vm_pte_addr, commit 8cbd644f; checked and delivered, delivery manifest: gma500_gfx.ko sha256 b97e2f0b..., built on cachix 2026-11-12T23:56Z, not landed in resgx545 yet; the lead's one-shot boot at 03:11, installed = loaded, both knobs 0 at each stage start), tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., source sgxfive-test.c 703cbcea... at resgx545 4dd6251, whose libsgxfive and uapi trees are 4623753's, the build's commit), the session kit of resgx545 68b3136 (kit/run_stage.sh with run/hooks.sh: a debugfs reset before each job, the row's knobs written and read back before it and restored to 0 after it, the kernel's recovery then the kit's reset and strict health fill and triangle after every fault, both drawing exactly after every row); frozen before the first job: FROZEN.sha256 56b2626d..., PREDICTIONS.sha256 06b12e5a..., FROZEN.commits (kit at 68b3136, the control outputs at data 1e83dc86); scored by the frozen score/score.py (out/ATT/score-STAGE.txt), re-run at the fold on the kept files with byte-identical output, every kept file decompressing to the raw sha256 the laptop logged (out/fold/reproduce.sh, reproduce.out); no lead decision during the run. Each knob row set vm_pte_addr to the first page of one mapping the tool makes (its own allocation order: 0x3e001000 a fill's 64 x 32 destination, a copy's read-only source or the 64 x 64 colour target; 0x3e000000 the render's GENERAL page with its VDM stream, indices and vertices) and vm_pte_flags to one flag; its premise, the kernel's `vm_map A +S: PTE flags F` line with the frozen flags, was read in every knob row. Outcomes as frozen: exact (job ok, diff 0, the knob-free control's hash), diff, fault (a kernel `BIF fault S at A` line with A's page in the mapping). Decoded after the run (post hoc, out/fold/post_read.py): BIF_INT_STAT and BIF_FAULT with hw_spec.md section 5.5's fields and the faulting page's place in the mapping. Jobs: `tri` (one 64 x 64 triangle on a render context, the tool's default), rows tri-c, tri-wo-fb, tri-cc-gen, tri-edm-fb, tri-edm-gen, tri-wo-gen, tri-c-end; 3 faults against the stage's #limit 4, no stop"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r8-k2:out/20261113-032428/tri/", "render-closing-r8-k2:out/fold/"]
terms = ["CR_BIF_FAULT", "CR_BIF_INT_STAT"]
+++
**What ran.** Q108 asked what the PTE flags other than READONLY do to a client's accesses
and what the fault reports; no record had set one. The round 8 kernel ORs a debugfs flag into
the PTEs of the one mapping that starts at a debugfs address. Stage tri ran the tool's plain
64 x 64 triangle seven times: knob-free first and last (the hash of r7-rp's health triangle,
0x99385a04ee01c585, and fb 0x3e001000 frozen), and between them WRITEONLY, CACHECONSISTENT and
EDMPROTECT on the colour target (0x3e001000, 5 pages: 4 of image and a guard) or on the render's
GENERAL page (0x3e000000, 1 page: the VDM control stream, the indices and the vertices, all
written by the host after the map). E946 has the transfer's rows.

**Frozen verdict (as printed).**

- `Q108 WRITEONLY, H-WO-ALL: WRITEONLY faults every access (rival) (2 of 2 rows decided)`; H-WO
  (a read faults, a write passes; frozen as the plan's) `is not supported: 1 held, 1 FAILED, 0
  cannot tell of 2`; H-WO-NONE `0 held, 2 FAILED`.
- `Q108 CACHECONSISTENT, H-CC-NEW: a unit reads the host's writes made after the map (plan K2,
  frozen) (1 of 1 rows decided)`; H-CC-STALE `0 held, 1 FAILED`.
- H-EDM-NONE and H-EDM-CLIENT: each `is not supported: 1 held, 1 FAILED, 0 cannot tell of 2`.

Both controls passed.

**Results [HW].**

| row | flag on | job | image | BIF_INT_STAT | BIF_FAULT (page, SB, CID) |
|---|---|---|---|---|---|
| tri-wo-fb | colour target | faulted | exact (0 of 4096 wrong) | 0x80020 | 0x3e0041f1 (0x3e004000, the image's last page; 31; 1) |
| tri-cc-gen | GENERAL page | ok | exact | - | - |
| tri-edm-fb | colour target | faulted | nothing written (4096 of 4096 sentinel) | 0xa0020 | 0x3e001001 (0x3e001000, first; 0; 1) |
| tri-edm-gen | GENERAL page | ok | exact | - | - |
| tri-wo-gen | GENERAL page | faulted | nothing drawn (4096 of 4096) | 0x80008 | 0x3e000001 (0x3e000000; 0; 1) |

Each fault was the kernel's `BIF fault ... stalls job N, recovering`, about 110 ms after the
map; its reset read BIF_FAULT 0 and BIF_INT_STAT 0x80000, and the kit's health fill and
triangle drew exactly at the first try after every row. The PTE line read the frozen flags in
every row (0x2, 0x8, 0x10 at the row's address).

**Read after the run (post hoc).** The WRITEONLY fault of the colour target is not a refused
write: every pixel is the CPU reference's, and the page named is the image's last, with SB 31
where every other fault of the session reads SB 0. [infer] Something of the 3D's pixel side
reads the target after its writes (the requestor bit is the write's, bit 5), and that read
faults. The GENERAL page's fault sets FAULT_REQ bit 3, the bit hw_spec.md gives the TA's read
of an unmapped stream page (E764), here FAULT_TYPE 0 as a READONLY write's (E766), not the
unmapped type 1. EDMPROTECT's fault is FAULT_TYPE 2, a type no record had seen.

**What it shows.** [HW] On this module, with the flag on one mapping of a 64 x 64 render:
WRITEONLY lets the colour writes land but faults the job at the target's last page, and faults
the read of a stream page before drawing; CACHECONSISTENT changes nothing seen of the host's
writes to the stream page; EDMPROTECT faults the 3D's colour write (FAULT_TYPE 2) and not the
stream page's read.

**What it does not show.** Which unit makes the last-page access under WRITEONLY; WRITEONLY or
EDMPROTECT on the parameter buffer, the TA's own writes or the EDM's buffers; flags together;
CACHECONSISTENT's effect on anything cached before the host's write (both maps were fresh);
whether the GENERAL page's reader is the VDM or the PDS (bit 3 is read from the access set up,
not from a source).
