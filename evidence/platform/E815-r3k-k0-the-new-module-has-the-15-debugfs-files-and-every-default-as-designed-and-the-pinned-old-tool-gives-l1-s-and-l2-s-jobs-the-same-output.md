+++
id = "E815"
claim = "R3k stages k0f and k0t (K0, the regression gate of the new module, stock firmware, no task of ours): F0 found all 15 debugfs files the kernel batch added or relies on and every default as designed (hold_recovery N, kick_no_bump N, render_pb_pages 0x00000422, render_rgn_arrays 0x00000001, the kicker file 'kicker 2 ccbctl 2 2 kicks 2', six kregnow rows 0x4, 0x110, 0x130, 0x740, 0xc00, 0xc04 and neither clear register), 12 of 12 rows held; the pinned old tool ~/sgxfive-test-r1 gave L1's geometry job dd-p1 (o0 mixed 0xff203040 x3622 and 0xff00ff00 x474, the line, parameter-buffer and TA-data hashes equal to the landed ones) and L2's pixel job t-ctl-green-16x16 (o0 0xff00ff00 in 256 of 256, CR_EVENT_STATUS2 0x400 before and after) exactly as they were kept, 11 of 11 rows held; two attempts of k0f before these stopped before any GPU job (the firmware was not loaded after the boot; the landed log filter read a new reset log line as a fault)"
unit = "platform"
method = "R3k session K0 (stages k0f, k0t; decisions R3-K1 to R3-K11), dataset edm-closing-r3k-events, 2026-11-10, kernel 7.3.0-resgx545, the new module of round 3 (fork resgx545 8fc748b0, srcversion 230E0EF50FFFD606C53AE3C, installed = loaded, checked at each preflight; gma500_gfx.ko sha256 06bf58db6e1c78f2bd9858bcc7b9e63d752786e098e50b5c67345ce69f2ceb78 as recorded in env.json), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, the laptop (host cedar) on the home LAN, not the direct cable, rebooted into the new module at 18:48 (boot-test-kernel.sh then test-session.sh, health ok); the final run in one driver call from 19:12:08 Mac time (out/r3-k0.log: k0f 19:12:08, k0t 19:12:15), each stage gated on the previous stage's kept stage.json, k0f with no GPU job (reset once, 15 files, 4 defaults, kicker and kregnow read, srcversion), k0t two jobs of the pinned tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053; health tool ~/sgxfive-test-s1b sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71) with the arguments L1 and L2 used; scored by the frozen score/score_r3.py k0f and k0t (out/score-k0f.txt, out/score-k0t.txt), health ok after each stage. Failed attempts before any GPU job, kept in the dataset: K0 attempt 1 (18:53, out/attempt1-nofw): the firmware was not loaded after the fresh boot, F0 got ENODEV (errno 19) from kicker, kregnow and miscinfo and the debugfs reset returned -19, stop 5; the health tool's fill and triangle loaded it. K0 attempt 2 (18:54, out/attempt2-logfilter): F0 read every file and default as predicted but the landed fwtask_run.BAD_LOG (word fault) matched the new reset line 'SGX reset: after the fault clear BIF_FAULT 0x0 BIF_INT_STAT 0x80000' of fork 36f3d278 and classed the job unhealthy, stop 4 (reset, gate and health ok); the session's r3_run.py now excludes that one exact line (mock test first), refrozen to 463c251b. K1 attempt 1 (19:13, out/kev-attempt1-armlog): stage f stopped (4) after the arm and before any row because the landed cmd_arm sliced dmesg by line count, which is constant when the ring buffer is full (1880 lines), and returned an empty log although the kernel had printed 'own task armed ... exit 0x1974'; r3_run.py arm() now reads its own kmsg marker slice (mock test first), refrozen to 1d6a3ad2. The landed tools/fwtask/fwtask_run.py itself was not changed (the session pins its hash). Freeze history of the session (FROZEN.sha256 over every generator, scorer, runner, table, blob and prediction; PREDICTIONS.sha256 1f32e767... throughout): 1527b62e... (FROZEN.pre-logfix.sha256) until K0's second attempt, 463c251b... (FROZEN.pre-armlog.sha256; K0's four stages and K1's first attempt ran under it) until K1's first attempt, 1d6a3ad2... (FROZEN.sha256; K1 ran under it); each refreeze was made after a failed attempt and before the next one, with the mock test first, and changed no prediction file. The README.md and PREFLIGHT.md of the dataset are the pre-run documents (README.md says prepared, not run; sections 1 and 7 of PREFLIGHT.md carry hashes older than the final freeze)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r3k-events:out/k0f/", "edm-closing-r3k-events:out/k0t/", "edm-closing-r3k-events:out/attempt1-nofw/", "edm-closing-r3k-events:out/attempt2-logfilter/"]
terms = ["CR_EVENT_KICK", "CR_EVENT_STATUS2", "CR_BIF_INT_STAT"]
+++
**What ran.** The kernel batch changed the module (fork 8fc748b0: the `kicker`, `kick_no_bump` and
`render_rgn_arrays` files, `kregnow` rows for the BIF and clear registers, a parameter-buffer poke
space, two reset log lines). K0 is the gate before any of it is used: every new file exists and
reads its default (k0f, no job), and the tools of L1 and L2, pinned and not rebuilt, still give
the outputs those sessions kept (k0t).

**Frozen verdicts (as printed).** `SUMMARY: k0f: defaults as designed; K0 rows: held out: 1 held,
0 FAILED, 0 cannot tell/void; control: 11 held, 0 FAILED, 0 cannot tell/void` and `SUMMARY: k0t:
both jobs as L1 and L2 kept them; K0 rows: held out: 2 held, 0 FAILED, 0 cannot tell/void;
control: 9 held, 0 FAILED, 0 cannot tell/void`.

**Results [HW].**

| stage | what | read |
|---|---|---|
| k0f | files | boot, hold_recovery, kick_no_bump, kicker, kregnow, load, miscinfo, own_arm, own_code, own_res, regs, render_pb_pages, render_rgn_arrays, reset, status: all 15 present |
| k0f | defaults | hold_recovery N, kick_no_bump N, render_pb_pages 0x00000422, render_rgn_arrays 0x00000001 |
| k0f | kicker | `kicker 2 ccbctl 2 2 kicks 2` (the held-out row: the per-load kick count equals the command count) |
| k0f | kregnow | rows 0x4, 0x110, 0x130, 0x740, 0xc00, 0xc04 |
| k0t | gd (dd-p1) | tool rc 0; `o0 mixed 0xff203040 x3622 0xff00ff00 x474`; line, parameter and TA-data hashes as the landed output |
| k0t | px (t-ctl-green-16x16) | tool rc 0; `o0 0xff00ff00 (256 of 256)`; STATUS2 0x400 before and after |

**What failed before it.** Attempt 1 of k0f stopped at exit 5 with ENODEV on the first file
touched because the firmware was not loaded after the boot; nothing had touched the GPU. Attempt 2
read every file and default as predicted and was classed unhealthy only because the landed log
filter (the word fault) matched the reset line the new module prints after the clear; the runner
fix and the refreeze are in the method. Both attempts are kept (`out/attempt1-nofw/`,
`out/attempt2-logfilter/`).

**What it shows and does not.** The new module carries the debugfs surface the kernel batch needs
with its defaults and does not change what the pinned tool does on a geometry job and a pixel job
(2 jobs, one each). It is not a regression test of the module's other paths; the later stages of
the session are.
