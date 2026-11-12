+++
id = "E828"
claim = "R3-rgn4 (the laptop check of the linux fork's 4x render contexts, fork resgx545 a2788bd8, module srcversion 99CD90DA): at render_rgn_arrays 0 (automatic) a 288 x 144 job at CR_TE_AA 0xe0000000, mode 2, on a context made with DRM_SGXFIVE_CTX_RENDER_AA_4X completed with 0 of 41472 pixels wrong, hash 0x4a61860dcb4ab325, TA data 0x8000 bytes, its target and both dumps equal to E824's h1; the same job on a context made without the flag was refused with EINVAL at submission; at render_rgn_arrays 1 the job faulted as in E729 (BIF_INT_STAT 0x90004, BIF_FAULT 0x20006061, recovery held; then one health triangle failed before one passed), and E827's row ctl-a1-256x160-tee0 reproduced byte for byte (hash 0x845a011c4fbf2325, 0 of 40960 wrong, TA data 0x6000 bytes, sha256 eaa6c96c...4372992); the 1x control reproduced E827's ctl-u-1024-n1; a 4096 x 4096 context with the flag was created and its 4x job faulted (BIF_INT_STAT 0x90100, BIF_FAULT 0x10000011) with 1048576 of 16777216 pixels right, the first wrong at (1024, 0), no dump written, health ok 3 of 3 after"
unit = "ta"
method = "R3-rgn4, the lead's laptop check of decision D3 (dataset render-closing-r3-rgn4), 2026-11-11, laptop host cedar booted 07:16 into kernel 7.3.0-resgx545 with the module of the linux fork's branch resgx545 at a2788bd86537fe8de22a37c2b61b9f48408b71a5 (commits 11, the 4 MiB TA-data slot, and 12, DRM_SGXFIVE_CTX_RENDER_AA_4X and the debugfs render_rgn_arrays: 0 automatic, 1, 2 or 4 forced), debug option on, built on the build host, srcversion 99CD90DA26E3AFF9C450517 loaded = installed, gma500_gfx.ko sha256 68ca2d56f83b8f3702d890ccf3b91208823528d0b2bf13009528229e8486797a; KUnit 14 suites with no 'not ok' and health ok before the first job; stock firmware; tool ~/sgxfive-test-rgn4 from resgx545 r3-rgn4 at 4623753 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a); the runner run/rgn4-check.sh by hand: a debugfs reset before each job, render_rgn_arrays and hold_recovery written per job, the kernel log marked around it; each job `tri --tri-full --keep-going --wait-ms 20000 --width W --height H --max-width W --max-height H` with E824's words (--poke cmd:1=0xe0000000 --poke cmd:10=0xeaa26e26 --poke cmd:13=0x80000002 --poke cmd:16=0xeaa26e26), --aa4 where the flag is named, --dump-render on j1r and j6r, the 4096 x 4096 job without --max-width/--max-height and with --keep-overflow; the 1x control `tri --width 1024 --height 768 -n 1 --keep-going --keep-overflow --wait-ms 20000`; order j5, j1, j3, j6, j1r, j6r, j2 (hold_recovery Y), j4. Not a frozen session: the predictions are the section 'Laptop check proposal' of the series report (rgn4-REPORT.md in the dataset, file time 05:09:42, before the boot), read by hand against the outputs after the run; no freeze, no scorer. The comparisons with E824's h1 and E827's rows were made after the run against their kept files in resgx545-data. Disclosures: the first runs of j1 and j6 rendered as j1r and j6r did and then failed at --dump-render (Permission denied) and were rerun with the same commands; case 1r ran twice and the kept outputs are the second run's; the health checks after j2 and j4 come from the operator's notes, no output kept"
tiers = ["HW", "infer"]
date = "2026-11-11"
data = ["render-closing-r3-rgn4:out/rgn4/", "render-closing-r3-rgn4:rgn4-REPORT.md"]
terms = ["CR_TE_AA", "region header", "Tile Accelerator (TA)", "CR_BIF_INT_STAT", "CR_BIF_FAULT", "Parameter Buffer (PB)"]
+++
**What ran.** E824 ran the sizes that fault at one array of region headers (E507, E729) with the
debug knob `render_rgn_arrays` at 4 and found four arrays complete them. The fork's commits 11 and
12 make that the kernel's rule: a render context created with the new flag
`DRM_SGXFIVE_CTX_RENDER_AA_4X` gets four arrays at the knob's new default 0 (automatic); a job whose
`CR_TE_AA` sets bit 31 or 30 on a context created without the flag is refused with `-EINVAL`, unless
the knob forced a count when the context was made; the TA-data slot doubles to 4 MiB, so the
four-array layout of 4096 x 4096 (0x223000 bytes) fits. This check runs the flag, the refusal, the
forced old layout and the largest size once each, with E824's words.

**Results [HW].**

| job | knob | size, flag | outcome | wrong | hash, TA data |
|---|---|---|---|---|---|
| j5 | 0 | 1024 x 768, 1x | complete | 0 of 786432 | 0xc9e301d225fe2325 |
| j1r | 0 | 288 x 144, flag | complete | 0 of 41472 | 0x4a61860dcb4ab325, 0x8000 bytes |
| j3 | 0 | 288 x 144, none | refused at submission, EINVAL | - | - |
| j6r | 1 | 256 x 160, none | complete | 0 of 40960 | 0x845a011c4fbf2325, 0x6000 bytes |
| j2 | 1, held | 288 x 144, none | BIF 0x90004 at 0x20006061, held | all | - |
| j4 | 0 | 4096 x 4096, flag | BIF 0x90100 at 0x10000011 | 15728640 of 16777216 | no dump |

The BIF pair is the kernel's log line: BIF_INT_STAT, then BIF_FAULT. j5's triangle counts are
207456 triangle, 578976 background, E827's `ctl-u-1024-n1` values; j3's kernel-log slice holds no
fault; j2's tool output reads Timer expired, j4's `job faulted, context lost`, its first wrong
pixel at (1024, 0). The TA data sha256s: j1r d3741578..., j6r eaa6c96c...4372992.

j1r's target hash, diff, triangle counts and both dumps (parameter pages and TA data) are byte for
byte those of E824's h1 (288 x 144 at knob 4): the automatic four arrays of a flagged context give
the layout the knob gave. j6r's are those of E827's `ctl-a1-256x160-tee0`, run there on the round 3
module at its default of one array. After j2 (the fault read, the knobs back, a debugfs `reset`)
one health triangle failed and the next passed; after j4 the health check passed 3 of 3 (both from
the operator's notes; no output was kept).

**Where j4 faulted [infer].** BIF_FAULT 0x10000011 lies in page 0x10000, the first page of the
PARAMETERS heap (base 0x10000000, `sgxfive_drv.c`). In the fork's layout a render context's
`param_base` is that heap's base plus its slot times 8 MiB (`sgxfive_cmd.c`, `sgxfive_ctx.h`), so
0x10000000 is the `param_base` of the context in slot 0, the first free slot of a VM
(`sgxfive_vm.c`); the kernel writes `param_base` as the TA's and the 3D's request base
(`sgx_render.c`) and maps the slot's pages from `param_base` + 0x1000 (`SGX_RENDER_PARAM_PB`,
`sgx_render.h`; `sgxfive_render.c`). That the job's context held slot 0 is read from the code, not
measured. Why the job reached that address, and what the 1048576 right pixels (the first wrong at
x 1024 of row 0) say about it, are not settled here (Q292).

**What it shows.** On the new module the flag gives a 4x context the layout E824 measured at knob
4, and the 4x render at 288 x 144 completes with it; without the flag the kernel refuses the job
before it runs, so the fault of E507 and E729 can no longer be reached by accident; a forced count
of 1 restores the old layout byte for byte (j6r) and the old fault (j2). E827's 4x row
`ctl-a1-256x160-tee0` now needs `render_rgn_arrays` 1 to reproduce: at the default it is refused,
by design, and with the flag it gets four arrays and other dumps. That is a behaviour of the new
kernel, not a correction of E827.

**What it does not show.** One run of each job, one boot. At 4096 x 4096 the context is created but
the 4x render does not complete: the four-array TA data size there (0x223000 bytes, the proposal's
prediction) was not measured, because no dump was written. Between 1024 x 768 (E824's h8, the
largest 4x render that completed) and 4096 x 4096 no size was run. The ZLS buffer, which keeps one
array's size, was not examined. The health triangles after a failed 4x job: one failed after j2
(two after each of E824's c1 and E826's f2), none after j4; the cause stays open (Q140).

**Correction 2026-11-11:** This adds readings made offline in round 4's render planning
(`closing4/render4x/pb_pages.out`, `u4_layout.out`) and leaves the claim as is; all are post hoc
and [infer]. The non-zero pages among the 0x422 PB pages of E824's ten kept four-array dumps
(`--tri-full`, `CR_TE_AA` 0xe0000000) equal U4 = 1 + ceil(2 (W / 16) (H / 16) / 32) in 10 of 10
(page 0 the object, every later page 32 full 128-byte slots), a fit read from those same dumps.
At 4096 x 4096 it gives 4097 pages for this record's 4x job, against 1024 usable (P - 0x22 at the
maximum P 0x422; the knob only shrinks the buffer, E704, E734), so the job would be the first 4x
partial render on record, and the full triangle would overflow from about 2048 x 2032 up. The
fault word, BIF_INT_STAT 0x90100 with BIF_FAULT 0x1000001x (requestor bit 8, page 0x10000, `SB`
1), was seen before only in E511's three HS faults (0x10000016, 0x10000012, 0x10000013); page 0
of a parameter slot is never mapped, so the access is at the request base plus zero. The fork
has no partial renders (an overflow returns -ENOSPC), and at 1x an overflow has never faulted
(E311, E412, E438). 1048576 right pixels with the first wrong at (1024, 0) are one 1024 x 1024
block, a macrotile of a 4 x 4 split; no image was kept. Q292 holds the test (a 4x size whose page
need is below 1024 faulting, or a small 4x overflow ending in -ENOSPC, would refute it).

**Correction 2026-11-11:** (the second, after R4-render4x) The overflow reading of the correction
above is refuted and the claim stands as it is. The 4x full triangle on four arrays faulted with
this record's word (0x90100 at 0x10000011) at 1280 x 1024 and 2048 x 1536, whose scenes need 321
and 769 of the 1024 usable pages (E845, held out: H-PB not supported, 2 FAILED), and at 4096 x
1152 (E846); a 4x scene that does overflow ended in -ENOSPC without a fault at 1024 x 768 and 288
x 144 (E846, read after the run, its frozen verdict gated). So j4 is not a 4x partial render: the
fault is about the size, and its onset lies past 1024 x 768 and at or before 1280 x 1024 (Q292).
The page fit U4 itself held again where a dump was kept (193 pages at 1024 x 768, 12 at 288 x
144; E845, E846).

**Correction 2026-11-12:** (the third, after R6-render4x) The claim stands; the cause of j4's
fault is now held out. A four-array 4x job faults with this word where its target's Z-ordered
tail-pointer entries pass the region headers of its context (E887, 11 of 11 held-out rows, two
held faults losing exactly the predicted stream offsets); at 4096 x 4096 they end at 0x80000
against `td.rgn` 0x43000. On a module that gives a 4x context four times the tail room, 4096 x 960
completes with 0 wrong pixels and 4096 x 1152, which also overflows, ends in -ENOSPC without a
fault (E889), so j4's fault is the layout's tail room, not the overflow; its right 1024 x 1024
block is a property of the faulting job that was not pursued.
