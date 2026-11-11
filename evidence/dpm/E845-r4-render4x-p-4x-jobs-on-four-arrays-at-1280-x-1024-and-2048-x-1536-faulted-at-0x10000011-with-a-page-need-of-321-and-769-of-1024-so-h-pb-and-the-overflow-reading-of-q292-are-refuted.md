+++
id = "E845"
claim = "R4-render4x stages s0 and p: the three controls reproduced as frozen (1x 1024 x 768 hash 0xc9e301d225fe2325; 4x 288 x 144 hash 0x4a61860dcb4ab325, 12 parameter pages; 4x 1024 x 768 hash 0xde0b9233c9822325, 193 pages, all 0 wrong), then the 4x full triangle on a context made for 4x targets (four region-header arrays, CR_TE_AA 0xe0000000, parameter buffer 0x422 pages) faulted at 1280 x 1024 and at 2048 x 1536, whose frozen page need U4 = 1 + ceil(2 tiles16 / 32) is 321 and 769 of the 1024 usable pages, with E828 j4's word (BIF_INT_STAT 0x90100, BIF_FAULT 0x10000011: page 0x10000, SB 1, CID 1), no pixel right and health ok after each; the stage stopped at its second fault and its four other sizes did not run: H-PB not supported (0 held, 2 FAILED, 4 cannot tell), so a 4x render on four arrays faults where its scene fits the buffer, and E828's 4096 x 4096 fault is not a parameter-buffer overflow"
unit = "dpm"
method = "R4-render4x (R4-G) stages s0 (3 controls) and p (6 held-out sizes, fault limit 2) of the question-closing pass, round 4 (decisions R4-3 and the render plan's 3 a, 4 a, 5 a, 7 a), dataset render-closing-r4-render4x, first attempt out/20261111-211315 (s0 21:13:15, p 21:14:39 Mac time; driver log run.log), on the laptop (host cedar), 2026-11-11, kernel 7.3.0-resgx545, module srcversion 99CD90DA26E3AFF9C450517 (fork resgx545 a2788bd8; installed = loaded, debugfs defaults checked), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, from resgx545 r3-rgn4 4623753); the 4x rows `tri --tri-full --keep-going --keep-overflow --wait-ms 20000 --width W --height H --max-width W --max-height H --aa4` with E824's words (cmd:1=0xe0000000, cmd:10=0xeaa26e26, cmd:13=0x80000002, cmd:16=0xeaa26e26), --dump-render and --regs 0x0700-0x072c, the 1x control `tri --width 1024 --height 768 -n 1` (E827's ctl-u-1024-n1, the tool's default triangle), render_rgn_arrays 0 (automatic) and render_pb_pages 0x422 read back, a debugfs reset before each job, a fill and a health triangle after each fault; U4, the TA data size and the completion of every size frozen in predictions/p.tsv before the first job (the fit: E824's ten kept dumps, 10 of 10; FROZEN.sha256 80a16d2b..., PREDICTIONS.sha256 7ceff7ba...); p stopped by its frozen rule (rc 15) after p-2048x1536, the second fault-class event, so p-2048x1920, p-4096x960, p-960x4096 and p-3072x1280 did not run; the lead's decision after the stop was `run/k.sh --from o` with the budgets unchanged (a second attempt for stages o, t and h, E846 to E848), p not run again; s0 scored by the frozen score/score_r.py s0 in the run (out/20261111-211315/score-s0.txt), p scored by the same frozen scorer after the run (`score_r.py p` and `score_r.py verdict out/20261111-211649 out/20261111-211315`; the driver does not score a stopped stage), both re-run on the kept files on 2026-11-11 with byte-identical output for s0; the non-zero parameter pages of s0's dumps and the job texts were read after the run (post hoc)"
tiers = ["HW", "infer"]
date = "2026-11-11"
data = ["render-closing-r4-render4x:out/20261111-211315/s0/", "render-closing-r4-render4x:out/20261111-211315/p/", "render-closing-r4-render4x:postrun/"]
terms = ["CR_TE_AA", "Parameter Buffer (PB)", "CR_BIF_FAULT", "CR_BIF_INT_STAT", "region header"]
+++
**What ran.** E828's 4096 x 4096 4x job on four region-header arrays faulted at the parameter
buffer's base. An offline fit (round 4 planning, appended to E828) read the non-zero parameter
pages of E824's ten four-array dumps as U4 = 1 + ceil(2 (W / 16) (H / 16) / 32), 10 of 10, which
gives 4097 pages at 4096 x 4096 against the 1024 a buffer of 0x422 pages leaves (P - 0x22): an
overflow, so Q292 was narrowed to "why an overflowing scene faults at 4x". Stage p held that fit
out at six sizes whose need passes (321 to 961 pages, four of them five times past the largest
fitted) and predicted that every one completes with 0 wrong pixels; 4096 x 960 and 960 x 4096
were the cells a width or height limit would fail.

**Frozen verdict (as printed).** s0: `controls {'s0-1x-1024x768': 'PASS', 's0-4x-288x144':
'PASS', 's0-4x-1024x768': 'PASS'}; later stages open; reg 0x0724 as a reported check not
usable`. p (`score_r.py verdict`): `H-PB: a 4x full-triangle job uses 1 + ceil(2 tiles16 / 32)
parameter-buffer pages and the layout formula's TA data, completing with 0 wrong pixels, at 6
held-out sizes up to U4 961 (4096 x 960 and 960 x 4096 included: a width or height limit would
fail there) is not supported: 0 held, 2 FAILED, 4 cannot tell of 6`.

**Results [HW].**

| job | set | U4 frozen | outcome | right pixels |
|---|---|---|---|---|
| s0-1x-1024x768 | control | (1x) | complete, as frozen | 786432 of 786432 |
| s0-4x-288x144 | control | 12 | complete, 12 pages, as frozen | 41472 of 41472 |
| s0-4x-1024x768 | control | 193 | complete, 193 pages, as frozen | 786432 of 786432 |
| p-1280x1024 | held out | 321 | fault 0x90100 at 0x10000011 | 0 of 1310720 |
| p-2048x1536 | held out | 769 | fault 0x90100 at 0x10000011 | 0 of 3145728 |

Both faults: the kernel's `SGX BIF fault: stat 0x100 addr 0x10000011`, then `BIF fault 0x90100 at
0x10000011 ... recovering`, the tool's `job faulted, context lost`; no pixel of the target was right
(the first, (0, 0), read the 0xdeadbeef pre-fill) and no dump was written. The fill and the health
triangle after each fault passed, as after E828's j4 (3 of 3). The register 0x0724 read 0 after both
completed 4x controls; the frozen check reported it against K2's held c1 reading (0x000b000b) and
found it not usable.

**Read after the run [HW, post hoc].** The s0 dumps' non-zero parameter pages: 0 to 0x12
(19 scene pages) for the 1x default triangle, 0 to 0xb (12) at 288 x 144 and 0 to 0xc0 (193) at
1024 x 768 at 4x, each with the fixed pages 0x422, 0x423 and 0x463 of the dump; the 4x counts are
U4's.

**What it shows.** [HW] On four arrays a 4x render of the full triangle faults with E828 j4's
word at 1280 x 1024 and 2048 x 1536, where its scene needs 321 and 769 of the 1024 pages the
buffer has. The fault is therefore not the buffer running out (H-PB refuted held out, and with it
the overflow reading of Q292 and of E828's correction); E846 adds that a 4x scene that does
overflow ends in -ENOSPC, post hoc. Together with the records the onset of the fault is bounded:
every four-array 4x job that completed had W <= 1024 and H <= 768 (E824's eight sizes up to 1024
x 768, E828's and s0's 288 x 144, s0's and E846's o3 1024 x 768) and every one that faulted had W
>= 1280 and H >= 1024 (1280 x 1024 and 2048 x 1536 here, 4096 x 1152 in E846, 4096 x 4096 in
E828). So the first faulting size lies past 1024 x 768 and at or before 1280 x 1024: past 1024
pixels wide (2048 samples), past 768 high (1536 samples), or past both, between 786432 and 1310720
pixels, between 193 and 321 pages of need; the records do not separate these.

**What it does not show.** Whether the width, the height or the count decides: the two cells
that would separate them (4096 x 960, 960 x 4096) did not run, nor did the other two sizes. What
the 3D-side access at page 0x10000 is (requestor bit 8, `SB` 1) [infer, the planning's reading:
a reader following a zero pointer]; no image or dump of a faulting job was kept. One run each, one
boot.
