+++
id = "E933"
claim = "R8-geo stage vdm (Q271; 8 renders of E703's capacity form, probe --tri pixpds:12 with 126 vertices, VDM word 7 SET by --vdm 7=V rather than xored, no fault or hang): word 7 set to its natural value (rows 3 at N = 8 V = 4, 0x03c00082; rows 2 at N = 2 V = 2, 0x02c00082) leaves the image of the natural job (the controls, 2 of 2 PASS); rows set to 3 at N = 2 V = 2 (natural + 1, R V = 6) change the image, the same way in both replicates (H-LAYOUT held 2 of 2, H-COUNT refuted 2 of 2); rows set to 2 at N = 8 V = 8 (natural - 1, a reading) change it too; frozen verdicts 'H-COUNT (rows a count) is not supported: 0 held, 2 FAILED, 0 cannot tell of 2' and 'H-LAYOUT (rows a stride) (2 of 2 rows decided)'"
unit = "vdm"
method = "R8-geo stage vdm of the question-closing pass, round 8 (decision R8-2 a; plan closing8/rank/rank-round8.md R8-4), on the laptop (host cedar), 2026-11-13, attempt out/20261113-015842 (dataset render-closing-r8-geo; the first attempt, out/20261113-015816, ran nothing: the lead passed SGX_TARGET_SSH_OPTS where the kit reads SGX_TARGET_HOST_KEY_ALIAS, so staging failed, and the lead's run log inside the session directory was a new file the freeze refused), kernel 7.3.0-resgx545, module srcversion 37EC97AB0CB37213C42FCCC (fork 664fd0d0, installed = loaded, knobs at their defaults at the stage start), tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., resgx545 4623753), the session kit of resgx545 d97c4739 (kit/run_stage.sh with run/hooks.sh, a debugfs reset before each job, every job class ok, no stop, no lead decision); frozen before the first job: FROZEN.sha256 2687abf3..., PREDICTIONS.sha256, FROZEN.commits; scored by the frozen score/score.py (out/ATT/score-STAGE.txt), re-run at the fold on the kept files with byte-identical output, every kept file decompressing to the raw sha256 the laptop logged (out/fold/reproduce.sh, reproduce.out). Jobs (risky as E703's, last, the health fill and triangle after each): `probe --tri pixpds:12 --temps 32 --width 64 --height 64 --vertices 126 --vtx-coords N --vdm 6^=X [--vdm 7=V] --pixels --dump-render $W` with render/closing-s1's pix_pa0.bin, vtx_cN.bin and p1131-fmt-N__0.bin (pinned, byte copies), V (vertices a task) set by flipping word 6's MAX_VERTICES as E703 did; N = 8 and 2 instead of the plan's 11 (only those programs are published). The natural word 7 was read before the freeze from a Mac build of the tool's own source (resgx545 4623753, hash checked) against the library's mock with --emit-scene (lead/dryrun_vdm.sh): 1 << 24 | 3 << 22 | 1 << 7 | 2 with the rows in 31:24. Frozen (predictions/vdm.tsv): each set row's image equal to or different from its natural twin's, run just before it (the image the sha256 of the 4096 --pixels values); the render memory kept for a decoder, not read here"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r8-geo:out/20261113-015842/vdm/", "render-closing-r8-geo:out/fold/"]
terms = ["VDM_TASK1.OUTPUT_SIZE", "VDM_TASK0.MAX_VERTICES"]
+++
**What ran.** E703 forced the rows of VDM_TASK1 (bits 31:24) with a xor and found every forced job's
render changed, even at products that natural jobs keep intact; with a xor the natural value cannot
be written, so 'the forcing breaks a job' and 'wrong rows break a job' were not told apart. The tool
also sets a word (`--vdm 7=V`, the same path). Stage vdm ran three natural jobs, the natural word
written through the set at two of them (the controls), rows one above the natural at N = 2 twice,
and rows one below at N = 8.

**Frozen verdict (as printed).** Controls `vdm-set-n8-v4: image same as vdm-nat-n8-v4 ... PASS`
and `vdm-set-n2-v2 ... PASS`; `H-COUNT (rows a count) is not supported: 0 held, 2 FAILED, 0
cannot tell of 2` (`the two replicates refuted under H-COUNT`); `H-LAYOUT (rows a stride) (2 of
2 rows decided)`.

**Results [HW].** The image (the o0 histogram the tool prints):

| job | rows (natural) | image |
|---|---|---|
| natural N = 8 V = 4, N = 2 V = 2, N = 8 V = 8 | 3, 2, 3 | c7868c7b...: 2821 background, the rest positions |
| set to natural, N = 8 V = 4 and N = 2 V = 2 | 3 (3), 2 (2) | c7868c7b..., as the natural |
| set to 3, N = 2 V = 2, twice | 3 (2) | b0ad2325... both: 2485 background, 1608 other |
| set to 2, N = 8 V = 8 | 2 (3) | 8dc72367...: 1692 background, 2396 other |

**What it shows.** [HW] Writing word 7 by itself does not break a job: the natural value set
through the same path leaves the render as it was. A rows value other than the natural one breaks
the render even where the task's output holds every vertex with room to spare (R V = 6 at N = 2,
two identical replicates): the rows are not a count of room. [infer] They are the vertex's output
stride (H-LAYOUT), as E703's broken jobs at products 30 and 32 suggested; below the natural value
the render breaks too.

**What it does not show.** How the broken image follows from the stride (the kept render memory
is not decoded here), rows at other N, and anything of the capacity limit (Q094's, decided).
