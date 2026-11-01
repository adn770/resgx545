+++
id = "E591"
claim = "With the first context's mappings, slot and memory kept at its close (kernel debugfs render_keep), the second context's render after the close of a first context that kept the DPM owner (render flags 0xc) is exact in 13 of 13 jobs (7 of keep-closed, 6 of keep-pages) and leaves TA3DCtl dwords 20 and 25 cleared as with the first context open (13 of 13), where without keep it faults at 0x200030c1 (BIF status 0x90004) in 2 of 2; afterwards the kept first context's TA data holds words in its control page (page 1: 16 of the ramp's dwords replaced, word 0 0x00200047), OTPM page (page 2: 20 dwords replaced, word 0 0x04000417) and state page (page 3: 34 dwords replaced, words 0 and 1 0x00020001 and 2) in the 9 of 9 flags-0xc jobs that put a ramp 0xa5000000 + i in one of the pages, and in none of the 6 of 6 jobs with flag bit 2 alone or no flag, and the ramps do not change the render (exact in 9 of 9); a kept first context that rendered a 1024x768 scene in partial renders, with no second context rendered, holds 18 non-zero dwords in its state page (page 6), 4 of 4, as E464 found without keep"
unit = "dpm"
method = "scripts keep-closed (15 jobs), keep-pages (6), keep-partial (8 in two runs: 4 solo, 4 with the second context), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 34729EB82083B1D04B0643E (built from the linux fork's p1135 branch, base 3d9b8bdefe94, tip da1eaeaa1247: commits 46 to 48 as they were before the review's fixes, series check 6 of 6 PASS, KUnit 176/176 with the debug option; installed equal to loaded at the start of every script, loaded once at 04:59:38), stock firmware (own_arm off), tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e, unchanged), no reboot, no clock-gate register written (no kreg, no kregnow), reset only through debugfs (the kernel pokes of commits 46 to 48 and debugfs tadata_fill are the only writes besides reset): tri -n 1 --ctx2 --close-first-early --close-trace --words --dump-render with debugfs render_keep armed, render_kept read after the tool exits"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["dpm-kept-state-page", "dpm-kept-state-page-amended"]
terms = ["CR_DPM_TASK_STATE", "CR_DPM_STATE_BASE0", "CR_DPM_CONTROL_BASE", "ta3d_ctl"]
+++

**What ran.** Three scripts, 29 job runs (the four solo rows of the first keep-partial run exited 2
on a tool usage error, no hardware, and are not counted; they were rerun, below). Each is `tri -n 1
--ctx2 --close-first-early` unless said: the first context renders 64x64 with its render flags
flipped by the kernel poke ta:7^=V, is closed, the second context of the same VM renders; `--words`
snapshots the control block before the first render, after the first, after the close and after the
second, `--dump-render` the second context's TA data; each case reset the GPU first. debugfs
render_keep was armed before the tool (kernel commit 47: the next render context closed keeps its
mappings, its render slot and its memory after the firmware's CLEANUP; the kernel log names the kept
context: 0x32411000, slot 0, TA data 0x20000000, the first one in 13 of 13 keep jobs of keep-closed
and 6 of 6 of keep-pages) and the kept context's TA data was read through debugfs render_kept after
the tool exited (commit 48, the TA data of the newest kept context). keep-closed, 15 jobs: V = 0x0
(2 keep), 0x4 (2 keep, 2 keep with a ramp 0xa5000000 + i in page 3 of the first context's TA data,
put there by debugfs tadata_fill before its render: its state page for a 64x64 context, 0x20003000),
0xc (2 without keep, 4 with, 3 with the ramp). keep-pages (a follow-up declared after it), 6 jobs: V
= 0xc with the ramp in page 1 or in page 2 (3 each). keep-partial (a follow-up), 8 jobs: a first
context rendering 1024x768 on a 0x28-page parameter buffer (the scene overflows and is finished by
partial renders, E464), alone (4: V = 0x4, 0xc, two each) or with the second context (4). Pilots,
not data: two jobs on the old module (5AD04F33, no switch) at 04:34 to 04:43 to see the tool's
output, keep-0 (exact) and nokeep-c, which faulted at 0x200030c1 with BIF status 0x90004 as E458's
runs did.

**Results.** [HW] Without keep, V = 0xc: `job faulted, context lost` at the second context's render,
BIF fault status 0x90004 at 0x200030c1 (2 of 2, as E458's 6 of 6). With keep, population one, the 13
keep jobs with V = 0xc (7 of keep-closed, 6 of keep-pages): the second render is exact (diff 0 of
4096 and the second context's own check) in 13 of 13, and also in the 6 of 6 keep jobs with V = 0x0
or 0x4. TA3DCtl dwords 20 and 25 are the first context's RT data + 0x18 (0x32411318) after its
render and after the close, and 0 after the second context's render in 13 of 13 jobs with 0xc (dword
20 stays 0x32411318 and dword 25 is 0 in the 4 of 4 with 0x4, 0 and 0 in the 2 of 2 with no flag):
the outcome with the first context open (E458). The kept first context's TA data after the second's
render, flags 0xc, no ramp: page 1 holds one non-zero dword, word 0 of 0x00200047, page 2 word 0 of
0x04000417, page 3 words 0 and 1 of 0x00020001 and 0x00000002, the other 32 dwords 0; pages 1 to 3
are zero in every job with V = 0x0 or 0x4 (6 of 6; the ramp in page 3 stays whole, 2 of 2). With a
ramp (the 9 of 9 flags-0xc jobs that had one): in page 3 all 34 dwords written were ramp dwords
replaced and none of the other 990 (3 of 3), in page 1 16 dwords (3 of 3) and in page 2 20 dwords (3
of 3), word 0 as above, the others 0; the render is exact in these 9 of 9 jobs. The second context's
own TA data (dump) holds only the page 4 (71 non-zero dwords) that every job holds (19 of 19), so
the pages written are the first context's, not the second's. Solo partial renders (kept first
context, no second context rendered): the state page (page 6) holds 18 non-zero dwords and the pages
7 to 11 405, 571, 495, 370 and 170, the same in 4 of 4 (V = 0x4 and 0xc); this is E464's finding
again (18 non-zero dwords after a partial render, flags 0x4 and 0xc alike) read from the kept
context, not a result about the kept store or the partial-render comparison, which is not tested. In
the 4 jobs with the second context the tool did not render it (it closes the second context first
after an overflowed render, "0 of 1 renders ok"), the kernel kept the second context, never
rendered, its 17 pages all zero: not scored. Declared before the runs: H45-K (kept mappings: the
render is exact) right in 13 of 13 scored jobs (the 2 controls of keep-closed with E458's fault
right too); H45-S (a store writes the kept state page, ramp changed) right in 3 of 3, its null H45-N
right in 2 of 2 (V = 0x4: ramp whole); H45-W (follow-up: only written, the ramps of pages 1 and 2
are replaced and the render stays exact) right in 6 of 6.

**What the pages say about the store.** The pages were read after the tool exited, so the written
words may come from anything between the first render and then: the second context's TA kick, its
render, its close and its CLEANUP (the tool's trace prints "cleanup after closing the second
context" lines). The clearing of dwords 20 and 25 is seen after the second render (the fourth
snapshot), not located in time either. The two contexts share a VM, so "the second context's
directory" and "the kept owner's addresses" are the same directory.

**Module load.** The module-load KUnit output of this install (34729EB8, loaded at 04:59:38) was
kept (analysis/modload-kernel.txt, 329 lines): 14 suites ok, kpoke 32 of 32, no `not ok`, with
`sgx_render_test_pb` (ok 4) and `sgxfive_debug_test_pb_small` (ok 1) among them, one minute after
the on-laptop build (04:58); the laptop was then up about 29.5 hours (booted 2026-11-07 23:27, not
03:xx on the 8th as the sub-phase's plan.md says). The "SGX recovery failed: -19" and "job hung,
recovery held" lines of the journal since the install are this KUnit's (the NULL-device lines), not
a recovery of the hardware. Q167 asks about those two cases failing at the module load of 5AD04F33:
they did not fail here. The amended module (B21FDA82, below) was loaded at 06:03:06, right after a
78 second build and a 22 minute series check on the same laptop (up about 30.6 hours, 122 MB free,
1.6 GB of cache): 12 of 14 suites ok and 3 cases failed, `sgxfive_coredump_test_bounds`,
`sgxfive_debug_test_render_newest` and `sgxfive_debug_test_render_donor`, each "Expected ctx->mem.va
!= NULL", with a kernel "page allocation failure: order:5, mode GFP_KERNEL|__GFP_ZERO|__GFP_COMP"
warning from the KUnit thread in the journal at that second (dpm-kept-state-page-amended); the two
cases of Q167 passed, kpoke 32 of 32 (the new test among them). That is the allocation reading of
Q167 seen once, with its kernel line, in other cases of the same kind ([infer]: the cases allocate a
large contiguous block that a fragmented 2 GB machine cannot always give); the failing cases are not ones these commits touched. Q167 stays open: the laptop was not freshly booted either time.

**Reading.** [infer] What accesses 0x20003000 after a kept owner's context is closed is a store made
while or after the second context's TA kick takes the DPM slot (the owner words 20 and 25 are
cleared by then): it changes dwords of the kept owner's control, OTPM and state pages, at the
owner's addresses, through the VM's directory. The writer is not identified (a hardware task or the
firmware) and the pages are DPM pages by E310's naming and their registers only. The fault of E458
is then that store reaching pages that the close unmapped: with them mapped and the memory kept the
render is exact. The ramps in the three pages do not matter to the render (9 of 9 exact), so no read
of them was seen; a read before the store would not show in a render that is exact either way, the
ramp being gone once the store has run, and the rest of the ramps in pages 1 and 2, 1008 and 1004
dwords, were left whole, so a read of them would have been seen only if a task used them. The data
cannot tell a page that is mapped but freed from one that is unmapped (the switch keeps both).

**Not shown.** What the stored words are (0x00200047, 0x04000417, the list pairs), at which kick the
store is made, who makes it, whether the second context's own pages are written at its own render, a
load task reading a partial render's lists back (the second context did not render after a partial
render), what sets the fields of register 0x0740 (Q045's first part). The kernel fix of the review
(below) changes only the case of a timed-out CLEANUP at the keep: every armed close in these runs
printed its "closed and kept" line (13 + 6 + 4 + 4 contexts), so none was cancelled; the experiments
were not rerun on the amended commits.

**Kernel commits.** The module of the runs was built at tip da1eaeaa1247. Afterwards the review of
this sub-phase asked for the changes below; the three commits were rebuilt on the same base,
3d9b8bdefe94, as 7a114862ebe4 (46), 4a47b3953728 (47) and 1dd291a61499 (48), and the series check
passed again, 6 of 6 (KUnit 106/106 with the debug option off at each, 173, 175 and 176 with it on).
The module of the amended tip, srcversion B21FDA82BD5E5CB5A627E3B, was built on the laptop and
installed; its module-load KUnit is above, and one plain 64x64 triangle drew exactly after the load.
No experiment ran on it. What changed: in 47 the render_keep switch is taken when the close starts,
before the CLEANUP, because a CLEANUP the firmware does not answer runs a recovery reset that drops
a switch still set, which would have silently cancelled the keep; the kpoke header says that a bg
poke is lost on a replay after a recovery; one pointer read under READ_ONCE; two lines wrapped; one
KUnit test frees its pages on a failed assertion. Only the case of a timed-out CLEANUP changes
behaviour; the rest are comments, a test and a read. The checks of the diff are in the phases entry.
