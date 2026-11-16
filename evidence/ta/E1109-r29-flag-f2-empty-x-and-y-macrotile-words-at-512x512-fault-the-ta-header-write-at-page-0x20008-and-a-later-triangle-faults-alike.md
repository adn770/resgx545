+++
id = "E1109"
claim = "r29-flag stage f2 (2 jobs, t10, E1074's form at 512 x 512 (n = 2, TA data 32768 bytes by the kernel's layout, c-512's reading), the size's own CR_TE_MTILE1 and CR_TE_MTILE2 with B2 cleared, words never run; 2 planned faults): both faulted with 0x90004, the TA's region header write, at TA data page 0x20008 (0x20008021 for the empty x axis, 0x20008061 for the empty y axis), so E1073's kind held 2 of 2 and the y page is not E509's 0x20010; frozen 'H-KIND ... (2 of 2 rows decided)', 'H-AXIS ... 1 held, 1 FAILED', 'H-SIZE ... 0 held, 2 FAILED'; after the y row the kit's strict health failed: the fill drew and the 64 x 64 health triangle faulted 0x90004 at 0x20008062 twice, no recovery failed, so the session stopped (rc 5) before its hang stages"
unit = "ta"
method = "r29-flag (render/closing-r29-flag), stage f2 of the question-closing pass (round 29, the flagged session with the user present: closing29/DECISIONS-R29.md (R29-1 to R29-6 (a): planned faults and recovered hangs only, the #limits counting planned rows and capped at 14; no kernel change, no boot, no clock-gate write, no held reset), plan closing29/plan/rank-round29.md sections 1 and 3), dataset render-closing-r29-flag; attempt out/20261116-055520; on the laptop over the travel cable (host cedar, kernel 7.3.0-resgx545, module srcversion E0CC40275493F8AEAD8180B (linux fork 456404fcffe5, installed and loaded alike), stock firmware, tools ~/sgxfive-test-t14 (t14, sha256 aa550b94585aaf6eb5d9b7927d320ad31ea8d1e206b8c5e99e4435c7f0a83859, built from resgx545 c58f9f9) and ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06) for the rows as named and t10 for the health pair, every job one process of the kit runner (kit/run_stage.sh at resgx545 c057181), a debugfs reset before every row, a reset and the strict health fill and triangle after every fault, every output and kernel slice kept gzipped; the stage gated on its s0 references (score-s0.txt: 8 of 8 passed, no SGX recovery failed line); the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/make.py)); freezes: FROZEN.sha256 705ffd3dc64e46ece569ec7539571e4dd0223dff840a69d4d9f0cd65634e3ce4 (85 files), PREDICTIONS.sha256 13684bc6bee5108879ecb0ef7d51086909aeb1357f950788113b29eecf4f5a1f (5 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at c0571816, resgx545:tools/closing/kit/lib_kit.sh at c0571816, resgx545:tools/closing/kit/run_stage.sh at c0571816, resgx545:tools/closing/kit/kitscore.py at c0571816, resgx545:tools/closing/kit/fake/sudo at c0571816, resgx545:tools/closing/kit/fake/timeout at c0571816, resgx545:tools/closing/kit/fake/df at c0571816, resgx545:tools/closing/kit/fake/modinfo at c0571816, resgx545:tools/closing/kit/fake/sha256sum at c0571816, resgx545:tools/closing/kit/fake/tool.sh at c0571816, resgx545:tools/closing/kit/fake/tool.py at c0571816, resgx545:tools/closing/kit/fake/ssh.py at c0571816, resgx545:tools/closing/scorekit.py at c0571816, resgx545:tools/closing/sessioncheck.py at c0571816, data:render/closing-r14-bif/out/20261114-055414/refill/rf-c-depth.depth-store.1.bin.gz at 73e058d5, data:render/closing-r14-bif/out/20261114-055414/refill/rf-c-depth.txt.gz at 73e058d5, data:render/closing-r14-flag/out/20261114-060824/f1/f1-ref-a.txt.gz at 73e058d5, data:render/closing-r14-flag/out/20261114-060824/f2/f2-ctl-256.txt.gz at 73e058d5, data:render/closing-r25-csc/out/20261115-213805/csc/y28-zc.txt.gz at 73e058d5, data:render/closing-r25-csc/out/20261115-213805/csc/y28-bc.txt.gz at 73e058d5, data:render/closing-r23-pk/out/20261115-202948/q181/c-copy-csc.txt.gz at 73e058d5, data:render/closing-r23-pk/out/20261115-202948/q181/c-copy-none.txt.gz at 73e058d5, data:render/closing-r14-flag/bins/f1-ref-a.bin at 73e058d5, data:render/closing-s1b/bins/p1139-green.bin at 73e058d5, data:render/closing-r13-flag/bins/p1131-green__0.bin at 73e058d5, data:render/closing-r13-flag/bins/p1131-blue__0.bin at 73e058d5, data:render/closing-r18-flag/out/20261114-133536/f4/b18-lib.txt.gz at 73e058d5, data:render/closing-r18-flag/out/20261114-133536/f4/b18-ramp.txt.gz at 73e058d5, data:render/closing-r18-flag/out/20261114-133536/f4/b18-lib.dmesg.gz at 73e058d5, data:render/closing-r18-flag/out/20261114-133536/f4/b18-ramp.dmesg.gz at 73e058d5, data:render/closing-r18-flag/out/20261114-133536/f2/q108-wo-load.dmesg.gz at 73e058d5, data:render/closing-r18-flag/out/20261114-133536/f2/q108-wo-tex.dmesg.gz at 73e058d5, data:render/closing-r18-flag/out/20261114-133536/f3/f3-k4.dmesg.gz at 73e058d5, data:vdm/state-units/cases.tsv at 73e058d5, data:vdm/state-units/output.txt at 73e058d5, data:vdm/state-units/kernel.log at 73e058d5, data:vdm/verification-1141ta/out-hw/p1141ta-dumps/vdm-series-b-all/cases.tsv at 73e058d5, data:vdm/verification-1141ta/out-hw/p1141ta-dumps/vdm-series-b-all/kernel.log at 73e058d5, data:render/closing-r13-flag/tables/f3.txt at 73e058d5, data:render/closing-r13-flag/out/20261113-220930/f3/cases.tsv at 73e058d5, resgx545:userspace/libsgxfive/src/render.c at c0571816, resgx545:userspace/libsgxfive/tools/sgxfive-test.c at c0571816, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, c58f9f9c87aa3f8370d2b66917898550d86f6879 at built, 3c68e8de6bdfeecd37b97e2d6095fef932e0e6d9 at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 9cef7a202fc8267fa04ab6986145b69fd4ab18beafbe6fdb5e65dd009a00b612 c58f9f9c87aa3f8370d2b66917898550d86f6879:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 396252bdb513282a17ed9c17446754c6478984fc423fba55236b6865bfb023c0 3c68e8de6bdfeecd37b97e2d6095fef932e0e6d9:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=E0CC40275493F8AEAD8180B; stops in the logs: f2 '## STOP: the health fill or triangle failed after f2-y512 (strict): recovery, then stop', '## abort: no recovery', the driver's 'STOP: stage f2 exited 5'; the frozen scorer run on the kept files at the fold (fold/score-f2.txt), the stage having kept no score file; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r29-flag:out/20261116-055520/f2/", "render-closing-r29-flag:fold/"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_BIF_FAULT"]
+++
**What ran.** Stage f2: `f2-x512` and `f2-y512`, t10 `tri --tri-full --pixels --width 512 --height
512 --max-width 512 --max-height 512 --kpoke-render 1:ta:N=V --wait-ms 20000 --keep-going
--dump-render "$W"` with `ta:143=0x02000008` (x: the size's word 0x02008008 with B2 cleared) and
`ta:144=0x04000010` (y: 0x04010010 with B2 cleared), both `expectfault expectdiff`, `#limit 2`.
The s0 references f2-ctl-256 (E1048's hash, 24576 bytes of TA data) and c-512 (the unpoked 512 x
512 job, job ok, 32768 bytes) passed. Frozen: the kind H-KIND (0x90004 on both, E1073); the page
H-AXIS (fixed by the axis at n = 2: x 0x20008, y 0x20010; E509, E1074) against H-SIZE (the TA data's
end + 2 pages for x, 0x2000a, + 10 for y, 0x20012) [infer, weak].

**Frozen verdict (as printed).** The stage kept no score file (it aborted, rc 5); the frozen
scorer run on the kept files at the fold (fold/score-f2.txt): `SUMMARY: f2: H-AXIS: the TA's
empty-axis write faults at a page fixed by the axis (x 0x20008, y 0x20010) is not supported: 1
held, 1 FAILED, 0 cannot tell of 2`; `SUMMARY: f2: H-KIND: E1073's kind: an empty-axis macrotile
word faults 0x90004 (the TA's header write) (2 of 2 rows decided)`; `SUMMARY: f2: H-SIZE: the TA's
empty-axis write moves with the TA data's end (x end + 2 pages, y end + 10) is not supported: 0
held, 2 FAILED, 0 cannot tell of 2`.

**Results [HW].** `f2-x512`: `BIF fault 0x90004 at 0x20008021`, `SGX stopped, 0 events seen`, the
reset clean, the strict health fill and triangle drew. `f2-y512`: `BIF fault 0x90004 at
0x20008061`, `SGX stopped, 0 events seen`, the reset clean; then the strict health: the fill drew
(`diff: 0`, f2-y512.fill3 and fill4) and the 64 x 64 triangle faulted twice (f2-y512.health3 and
health4: `job: failed: job faulted`, all 4096 pixels unwritten, 0xdeadbeef; kernel `BIF fault
0x90004 at
0x20008062`, jobs 714 and 716, `SGX stopped, 1 events seen`, each reset clean), so the runner
stopped (`## STOP: the health fill or triangle failed after f2-y512 (strict)`, `## abort: no
recovery`, rc 5). No `SGX recovery failed` line in the attempt; the lead reports a t10 triangle
drawing afterwards (outside the kept files). The x row's health had drawn at the first try.

**What it shows.** [HW] E1073's kind holds a third and fourth time: an axis whose bounds are all 0
faults the TA's header write, on either axis, at 512 x 512. Both writes fault at TA data page
0x20008, which at this size is the first page past the kernel's TA data (0x8000 bytes), where at
384 x 256 (E1074, 0x6000 bytes) the x write faulted at 0x20008 as well, two pages past it: the
page follows neither the axis (E509's y page 0x20010 is not seen here) nor the end by a fixed step
[post hoc]. [HW] After the y-side word a plain 64 x 64 triangle in a new context, after the kit's
debugfs reset and a fill, faulted the same TA write at the same page, twice; after the x-side word
it drew. Unlike E901's and E919's boots after a 0x90004 fault, which timed out (`SGX recovery
failed: -110`), every boot here came up and the next triangle's TA faulted instead. [infer] The
empty y word leaves TA state that the reset and a fill do not clear and that a later job's TA
follows; what cleared it before the lead's triangle is not kept.

**What it does not show.** What places the write at page 0x20008 (no TA data is dumped after a
failed render), the stride's relation to the RT data, what state the y word leaves and what
clears it, and the kind at four macrotiles a side.
