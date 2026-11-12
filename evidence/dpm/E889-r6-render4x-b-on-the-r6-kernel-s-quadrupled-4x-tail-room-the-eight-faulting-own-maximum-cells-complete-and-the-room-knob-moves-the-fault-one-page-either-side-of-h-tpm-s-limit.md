+++
id = "E889"
claim = "R6-render4x set B on the r6-kernel module (fork r6-kernel 3f0b3e74, srcversion 41E2F5C756F96D20F7109A4; 21 jobs, one attempt, 3 faults, all predicted): with four times the 4 side^2 tail room for a context made for 4x targets the eight own-maximum cells that faulted on the rgn4 module (1280 x 1024, 1184 x 768, 1024 x 800, 2048 x 240, 768 x 2048, 2048 x 1536, 1280 x 768, 1024 x 1024) completed with 0 wrong pixels and no region header off the rule (H-ROOM, 8 of 8 held out); with the room set by the debugfs render_tail_room, 1280 x 1024 completed at 0xb000 (td.rgn 0xe000, its entries end 0xd800) and faulted one page lower with E845's word, losing exactly the frozen 171 stream offsets 0xd000 to 0xd7f8, and 1024 x 768 faulted at 0x3000 (H-TPM's limit, 3 of 3 held out; the controls 1280 x 1024 at 0x4000 faulted and 1024 x 768 at 0x4000 completed); 2048 x 2032 (1017 pages) and 4096 x 960 completed with 0 wrong and 4096 x 1152 (1153 pages needed) ended in -ENOSPC without a fault [explore]; s0b's four controls passed"
unit = "dpm"
method = "R6-render4x set B, stages s0b (4 controls, fault limit 1), b (9 rows, limit 2), k (5 rows, limit 4) and r (3 rows, limit 1) of the question-closing pass, round 6 (decisions R6-3 a, R6-4 a; plan closing6/render4x/exp-render4x-r6.md section 4), dataset render-closing-r6-render4x, attempt out/20261112-153845 (s0b 15:38:46, b 15:39:59, k 15:41:35, r 15:42:55 Mac time; driver log run-r6x-B.log), on the laptop (host cedar), 2026-11-12, after the one-shot boot at 15:37 into kernel 7.3.0-resgx545 with the module of the linux fork's branch r6-kernel at 3f0b3e74 (56f8b932 gives a 4x context four times the tail room and adds the debugfs render_tail_room; srcversion 41E2F5C756F96D20F7109A4 installed = loaded, checked by the runner before the first job), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), the tool of E887 (sha256 e6951558..., no uAPI change); each b, k and r row `tri --tri-full --keep-going --keep-overflow --wait-ms 20000 --width W --height H --max-width W --max-height H --aa4` with E824's words, --dump-render (r1 and r3 without dumps) and the register snapshots; s0b r5's three controls with the r6-kernel's TA-data sizes and the 1x full triangle at 1024 x 768; a debugfs reset before each job, then render_tail_room written (0 or the row's room), read back and put back to 0 after the job (the kernel log's knobs-read and room-back lines), render_rgn_arrays 0 and render_pb_pages 0x422 read back, k3 with hold_recovery Y and its held dumps kept, the fill and the strict health triangle after each of the 3 fault-class events (k1, k4, k3, each BIF_INT_STAT bits 15:0 0x0100 and BIF_FAULT 0x10000011), no 'recovery failed' line, health ok and every knob at its default at each stage's end; the layout of the r6-kernel module transcribed from the fork (gen/layout_b.py) and H-TPM as stage A left it frozen in predictions/{s0b,b,k,kh,r}.tsv before the first job of set B (FROZEN-B.sha256 05fe1b89..., 356 files; PREDICTIONS-B.sha256 ebd564f3...; FREEZE-B.txt), a second freeze beside set A's, made after set A ran and its verdicts were read (disclosed in README-B.md; nothing was fitted on set A's files), set A's FROZEN.sha256 unchanged and both freezes verified at the fold; scored by the frozen score/score_b.py in the run (score-s0b.txt, score-b.txt, score-k.txt, score-r.txt) and re-run on the kept files on 2026-11-12 with byte-identical output; postrun/verdict-B.txt is the verdict the driver names"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r6-render4x:out/20261112-153845/", "render-closing-r6-render4x:postrun/"]
terms = ["CR_TE_AA", "CR_TE_TPC_ADDR", "Parameter Buffer (PB)", "CR_BIF_FAULT", "CR_BIF_INT_STAT", "region header"]
+++
**What ran.** Q292's planned kernel item (decision R5-8 a, R6-3 a): the fork's tail room for a
context made for 4x targets grows from 4 side^2 to 16 side^2 bytes, the region headers moving up
with it, and a debugfs knob sets the room by hand. Set B tested the change (H-ROOM: the eight
own-maximum cells that faulted on the rgn4 module complete), H-TPM's limit through the knob (one
page above and below the end of 1280 x 1024's entries, and 1024 x 768 one page under its own end),
and the largest targets.

**Frozen verdict (as printed).** s0b: `controls {'s0b-1x-1024x768': 'PASS', 's0b-1xf-1024x768':
'PASS', 's0b-4x-288x144': 'PASS', 's0b-4x-1024x768': 'PASS'}; later stages open`. b: `H-ROOM: with
the r6-kernel's automatic 4x room the eight own-maximum cells that faulted on the rgn4 kernel
complete with 0 wrong (b1-b8) (8 of 8 rows decided)`. k: `H-TPM's exact limit through the knob:
1280 x 1024 completes with the room at 0xb000 (td.rgn 0xe000, entries end 0xd800) and faults one
page lower losing exactly the frozen 171 offsets; 1024 x 768 faults with the room at 0x3000 (3 of 3
rows decided)`. r: `the largest targets: 2048 x 2032 and 4096 x 960 complete with 0 wrong; 4096 x
1152 ends in -ENOSPC without a fault [explore] (3 of 3 rows decided)`.

**Results [HW].**

| job | target | room, `td.rgn` | entries end | outcome | scene pages, TA data |
|---|---|---|---|---|---|
| b9 (control) | 1024 x 768 | 0x10000, 0x13000 | 0x7000 | complete, 0 wrong | 193, 172032 |
| b1 | 1280 x 1024 | 0x10000, 0x13000 | 0xd800 | complete, 0 wrong | 321, 262144 |
| b2 | 1184 x 768 | 0x10000, 0x13000 | 0xc760 | complete, 0 wrong | 225, 217088 |
| b3 | 1024 x 800 | 0x10000, 0x13000 | 0x7ac0 | complete, 0 wrong | 201, 200704 |
| b4 | 2048 x 240 | 0x10000, 0x13000 | 0xaff0 | complete, 0 wrong | 121, 139264 |
| b5 | 768 x 2048 | 0x40000, 0x43000 | 0x17800 | complete, 0 wrong | 385, 520192 |
| b6 | 2048 x 1536 | 0x40000, 0x43000 | 0x1c000 | complete, 0 wrong | 769, 643072 |
| b7 | 1280 x 768 | 0x10000, 0x13000 | 0xc800 | complete, 0 wrong | 241, 217088 |
| b8 | 1024 x 1024 | 0x10000, 0x13000 | 0x8000 | complete, 0 wrong | 257, 200704 |
| k1 (control) | 1280 x 1024 | 0x4000, 0x7000 | 0xd800 | fault 0x0100 at 0x10000011 | - |
| k5 (control) | 1024 x 768 | 0x4000, 0x7000 | 0x7000 | complete, 0 wrong | 193, 122880 |
| k2 | 1280 x 1024 | 0xb000, 0xe000 | 0xd800 | complete, 0 wrong | 321, 241664 |
| k4 | 1024 x 768 | 0x3000, 0x6000 | 0x7000 | fault, same word | - |
| k3 (held) | 1280 x 1024 | 0xa000, 0xd000 | 0xd800 | fault; lost set equal (171) | 321 written |
| r2 | 2048 x 2032 | 0x40000, 0x43000 | 0x1fff0 | complete, 0 wrong | 1017, 765952 |
| r1 | 4096 x 960 | 0x40000, 0x43000 | 0x2ff00 | complete, 0 wrong | no dump |
| r3 | 4096 x 1152 | 0x40000, 0x43000 | 0x3ac00 | -ENOSPC, no fault | no dump |

The completed rows with a dump have 0 region headers off the rule from the new `td.rgn` and
nothing non-zero below it. k3 lost the offsets from 0xd000 to 0xd7f8, header 0 among them (frozen:
yes). r3's tool line: 0 of 1 renders ok, 1 overflowed, no BIF line in its kernel slice. The s0b
controls reproduced the kept hashes with 0 wrong pixels, the 4x 1024 x 768 one on the new TA-data
size 0x2a000. Reported, not scored: b2's scene used 225 pages where U4 gave 223 (`DIFFERS`); every
other completed row matched U4. Read after the run from the tables (post hoc): b2 (1184 x 768) and
E887's a12 (992 x 1280), the two rows two pages over U4, are the only completed rows with an odd
count of 32-pixel tile columns on four macrotiles a side.

**What it shows.** [HW] The room the kernel gives a 4x context is what decides the fault: with four
times the room every size that faulted on its own maximum completes, up to 2048 x 2032 and 4096 x
960, and with the room set by hand the fault comes and goes one page either side of H-TPM's limit,
at one target and another, a held fault losing exactly the offsets the rule names. A 4x scene too
large for the buffer ends in -ENOSPC without a fault once its entries stay below the headers, at
4096 x 1152 as at the small overflows of E866. [infer] So the 4096-wide faults of E828 and E846
were the tail entries passing the headers (H-TPM gives both), not the overflow, and the room a 4x
context needs is 4 x (Z(2tx - 1, 2ty - 1) + 1) bytes, which the quadrupled room covers at every size
up to its maximum.

**What it does not show.** 4096 x 4096 and any size whose scene needs more than the 1024 usable
pages with a completing layout other than 4096 x 1152; why b2 and a12 took two pages over U4 (two
rows, read from the scorer's report; no rule is fitted); the residue E870 left (the 189 word-0
losses, bit 27, the right blocks of E828 and E846), which belongs to the old layout's faults and
is not pursued; one run each, one boot of the new module.
