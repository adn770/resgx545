+++
id = "E946"
claim = "R8-k2 stage xf (Q108; a fill's destination and a copy's read-only source with one PTE flag, 9 jobs): every frozen verdict 'cannot tell: controls: xf-c-end: cannot tell', since the stage's fourth fault (the isolation control's, then WRITEONLY's fill, EDMPROTECT's fill and RO|WO's copy) reached its #limit 4 with the end control left, so it never ran; read after the run, every other control passed and the rows read as E945's: WRITEONLY's fill wrote its whole image then faulted at the image's last page (0x80020, SB 31), RO|WO's copy faulted its texture read at the source's first page (0x80002, nothing written), CACHECONSISTENT on the copy's source changed nothing (exact), EDMPROTECT's fill faulted at the first page (0xa0020, nothing written); the tool's isolation redid E021's read-only write fault (0x80020 at page 0x3e200000) [HW, post hoc]"
unit = "bif"
method = "R8-k2 stage xf of the question-closing pass, round 8 (decisions R8-5 a and R8-6 a; plan closing8/rank/rank-round8.md section 3, K2), on the laptop (host cedar), 2026-11-13 03:24 to 03:28, one attempt out/20261113-032428 (dataset render-closing-r8-k2), kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 from the linux fork's branch r8-kernel at 2a650d74 (debugfs vm_pte_flags and vm_pte_addr, commit 8cbd644f; checked and delivered, delivery manifest: gma500_gfx.ko sha256 b97e2f0b..., built on cachix 2026-11-12T23:56Z, not landed in resgx545 yet; the lead's one-shot boot at 03:11, installed = loaded, both knobs 0 at each stage start), tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., source sgxfive-test.c 703cbcea... at resgx545 4dd6251, whose libsgxfive and uapi trees are 4623753's, the build's commit), the session kit of resgx545 68b3136 (kit/run_stage.sh with run/hooks.sh: a debugfs reset before each job, the row's knobs written and read back before it and restored to 0 after it, the kernel's recovery then the kit's reset and strict health fill and triangle after every fault, both drawing exactly after every row); frozen before the first job: FROZEN.sha256 56b2626d..., PREDICTIONS.sha256 06b12e5a..., FROZEN.commits (kit at 68b3136, the control outputs at data 1e83dc86); scored by the frozen score/score.py (out/ATT/score-STAGE.txt), re-run at the fold on the kept files with byte-identical output, every kept file decompressing to the raw sha256 the laptop logged (out/fold/reproduce.sh, reproduce.out); no lead decision during the run. Each knob row set vm_pte_addr to the first page of one mapping the tool makes (its own allocation order: 0x3e001000 a fill's 64 x 32 destination, a copy's read-only source or the 64 x 64 colour target; 0x3e000000 the render's GENERAL page with its VDM stream, indices and vertices) and vm_pte_flags to one flag; its premise, the kernel's `vm_map A +S: PTE flags F` line with the frozen flags, was read in every knob row. Outcomes as frozen: exact (job ok, diff 0, the knob-free control's hash), diff, fault (a kernel `BIF fault S at A` line with A's page in the mapping). Decoded after the run (post hoc, out/fold/post_read.py): BIF_INT_STAT and BIF_FAULT with hw_spec.md section 5.5's fields and the faulting page's place in the mapping. Jobs: `fill` (64 x 32, stride 256), `copy --print-addrs` (64 x 32, the source mapped read-only by the tool), `isolation` (the tool's VM checks, whose read-only check aims a fill at a read-only mapping), rows xf-c-fill, xf-c-copy, xf-c-addr (the address with flags 0), xf-c-ro (isolation), xf-wo-fill, xf-cc-copy, xf-edm-fill, xf-wo-copy, xf-c-end. The stage stopped by its rule (rc 24) after xf-wo-copy, its fourth fault event of #limit 4 with xf-c-end left (the builder's budget counted the isolation control's fault and allowed for 3 of the rows, not for H-WO-ALL's fill fault as well); the driver went on to stage tri (E945)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r8-k2:out/20261113-032428/xf/", "render-closing-r8-k2:out/fold/"]
terms = ["CR_BIF_FAULT", "CR_BIF_INT_STAT"]
+++
**What ran.** The transfer's side of Q108 (E945 has the render's): knob-free controls for a
fill and a copy (r7-rp's fill hash 0xb60c6095080bd325; copy-addresses' copy hash
0x9b1c0be484ac0d25 and source 0x3e001000), the address knob alone (flags 0), the tool's
`isolation` as the read-only control, then WRITEONLY on a fill's destination, CACHECONSISTENT
on a copy's source, EDMPROTECT on a fill's destination, WRITEONLY on a copy's source (with the
tool's own READONLY, RO|WO, decision R8-6), and the fill again as the end control.

**Frozen verdict (as printed).** Every SUMMARY of the stage, for the seven hypotheses: `cannot
tell: controls: xf-c-end: cannot tell`. The runner: `## STOP (stage xf): 4 faults or hangs (the
limit is 4) with rows left, after xf-wo-copy`. Controls xf-c-fill, xf-c-copy, xf-c-addr and
xf-c-ro passed; xf-c-end did not run.

**Results [HW], read after the run (post hoc).**

| row | flag (PTE) | job | image | BIF_INT_STAT | BIF_FAULT (page, SB, CID) |
|---|---|---|---|---|---|
| xf-c-addr | none (address only) | ok | exact, no PTE line | - | - |
| xf-wo-fill | WO (0x2) | faulted | exact (0 of 2048 wrong) | 0x80020 | 0x3e0021f1 (0x3e002000, the image's last page; 31; 1) |
| xf-cc-copy | CACHED (0xc with RO) | ok | exact | - | - |
| xf-edm-fill | EDMPROT (0x10) | faulted | nothing written (2048 of 2048) | 0xa0020 | 0x3e001001 (0x3e001000, first; 0; 1) |
| xf-wo-copy | RO + WO (0x6) | faulted | nothing written (2048 of 2048) | 0x80002 | 0x3e001001 (0x3e001000, first; 0; 1) |

The isolation control printed PASS for all nine of its checks; the kernel's three faults were
0x90020 at 0x3e100001 and at 0x3e001002 (its unmapped-address checks, FAULT_TYPE 1) and 0x80020
at 0x3e200002 (the read-only write, page 0x3e200000, as render/client-jobs). The health fill and
triangle drew exactly after every row, the stop's included, and stage tri then passed both of
its knob-free controls (E945).

**What it shows.** [HW, post hoc: no frozen verdict decided] The transfer reads as the render:
WRITEONLY lets a fill's writes land and then faults at the image's last page with SB 31, as the
3D's colour write in E945; a copy's texture read of a READONLY + WRITEONLY page faults with
FAULT_REQ bit 1 (the bit of E765's texture fetch, here FAULT_TYPE 0) before writing anything;
EDMPROTECT faults a fill's writes with FAULT_TYPE 2 as the 3D's; CACHECONSISTENT on a copy's
source changes nothing seen. [infer] The end control would have passed: the health fill, the
same job, drew exactly after the stop.

**What it does not show.** A held verdict for any transfer row (the gate was shut); WRITEONLY
alone on a texture read (the tool maps a copy's source read-only); EDMPROTECT on a texture read.
