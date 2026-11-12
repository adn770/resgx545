+++
id = "E906"
claim = "r7-rp stage q293 (Q293, 4 jobs, three renders of one scene with CR_TE_AA 0x40000000): the 3D reads render 2's own object as it reads render 1's: with the kernel's poke before render 3 putting render 2's object (dump dwords 27 to 53) in the bit-29-set layout (E829's twin words shifted by 27, 16 of 16 pokes applied and seen in the dump) render 3 drew 4096 triangle pixels of 4096, 0 wrong against render 3's colours, while render 1's and render 3's objects stayed displaced, and 0xffffffff poked at its dword 11 (dump dword 38) drew nothing (0 of 4096); the control of three renders left objects at dwords 0, 27 and 54, each with a zero at its dword 11 and the format word 0x00040101 at its dword 12, and drew nothing, and E888's t7 row repeated its kept dump head, image counts, diff count and target hash 0x8ea26cdfee74a325 on module 41E2F5C7; frozen verdict 'Q293: render 2's own object is read as render 1's: put in the bit-29-set layout by a poke before render 3 it draws (u3, 4096 triangle pixels) and 0xffffffff at its dword 11 draws nothing (u4); three renders leave objects at 0, 27, 54 in the displaced layout and draw nothing (u1) (2 of 2 rows decided)'"
unit = "ta"
method = "r7-rp stage q293 of the question-closing pass, round 7 (decisions R7-2 a; plan closing7/a/exp-pixel-r7.md section 3.5, user decision 5 a), dataset render-closing-r7-rp, on the laptop (host cedar), 2026-11-12, one attempt out/20261112-205431 (started 20:54:31 Mac time, run-r7r.log; 143 jobs in nine stages, s0 first, the session gate, which passed 4 of 4: the default 64 x 64 triangle exact with t4, t6 and t7 and E831's z-ctl-34x18-y storing 924 with t4), kernel 7.3.0-resgx545, module srcversion 41E2F5C756F96D20F7109A4 (fork 3f0b3e74, installed = loaded, knobs at their defaults at every stage start, read only), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a; tools ~/sgxfive-test-rgn4 (t4, sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a), round 6's t6 (built from resgx545 d9b2969, sha256 97df5c0ebf5bff2786a59b302e9a8a722bad36f0ef2f5dba11b6f2957f4ad98c) and t7, built by the lead on the build host from resgx545 1c64f3a, which allows odd widths (lead/build_tool7.sh, source pinned in TOOL7SRC.sha256, sha256 f2df4f99add18f011a3607dc3a73ac42cdfab3ec730d1e1f8cd7621761643375 in TOOL7.sha256, the slot run/freeze_r7.sh tool7 filled once, checked on the laptop before every stage); tables, predictions, models, scorers and runner frozen before the first job (FROZEN.sha256 33237f0d..., PREDICTIONS.sha256 c4be8ddd...; FROZEN.commits pins the resgx545 files read at 1c64f3a and data 830641e6); every stage ran to its end with health ok after it, no stop, no lead decision during the run and no reboot. Scored by the frozen score/score_r7.py in the run (out/ATT/score-STAGE.txt); at the fold (2026-11-12) the same scorer re-run on the kept files gave output byte-identical to the kept one for every stage (p7-rd's once its first line, the absolute path of the kept p7-rdc directory, names the run's tree), and the 944 kept files decompress to the raw sha256 the laptop logged (fold/reproduce.sh, fold/reproduce.out). Rows (t4): `tri --tri-full --keep-going --wait-ms 20000 --width 64 --height 64 --max-width 64 --max-height 64 -n 3 --geometry 1 --geometry 2 --poke cmd:1=0x40000000 --poke cmd:10=0xeaa26e26 --poke cmd:13=0x80000002 --poke cmd:16=0xeaa26e26 --dump-render`, renders 1 and 2 geometry only, render 3 drawing, the module's `render_rgn_arrays` set to 1 around each row and read back (restored after); u1 (control, no poke, first: a class other than ok would have ended the stage), u2 (control: E888's t7 again, `-n 2` with `2:par:11=1`, frozen against its kept dump head, dwords 0 to 63, image and hash from the 99CD90DA boot), u3 (held out: `3:par:38..53` = E829's p3 words, 16 kernel pokes, the tool's limit), u4 (held out: `3:par:38=0xffffffff`); u3 and u4 were cannot tell unless every poke is applied (the kernel's lines) and seen in the dump; rival for u3: 0 triangle pixels (render 2's object read differently or not at all). Scorer score_dump.py q293, replayed before the freeze on E888's t7 (holds), t8 (fails) and E897's 13 dumps. Every job class ok"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-rp:out/20261112-205431/q293/", "render-closing-r7-rp:out/20261112-205431/s0/", "render-closing-r7-rp:fold/"]
terms = ["CR_TE_AA", "Parameter Buffer (PB)", "PB_OBJ.FORMAT"]
+++
**What ran.** With `CR_TE_AA` bit 29 clear and bit 30 set the TA inserts a zero dword right before
an object's format word and the 3D, reading the bit-29-set layout, takes that zero as the format
word and draws nothing (E728, E829, E888). E829 showed this for render 1's object; E897 found render
2's own object in 13 kept dumps with the same insertion, never drawn, but every empty job had both
objects displaced, so whether the 3D skips render 2's object for its own zero or stops at render 1's
was not separated. Here a scene of three renders (two geometry-only, the third drawing) let a kernel
poke before render 3 rewrite render 2's object alone.

**Frozen verdict (as printed).** `q293: Q293: render 2's own object is read as render 1's: put in
the bit-29-set layout by a poke before render 3 it draws (u3, 4096 triangle pixels) and 0xffffffff
at its dword 11 draws nothing (u4); three renders leave objects at 0, 27, 54 in the displaced layout
and draw nothing (u1) (2 of 2 rows decided)`.

**Results [HW].** From `out/20261112-205431/score-q293.txt`:

| row | poke before render 3 | last render's image |
|---|---|---|
| u1 control | none | 0 triangle, 4096 background |
| u2 control | E888's t7 (`-n 2`, `2:par:11=1`) | 0 triangle, diff 3969, E888's hash |
| u3 held out | `3:par:38..53`, the twin's 16 words | 4096 triangle, diff 0 |
| u4 held out | `3:par:38=0xffffffff` | 0 triangle, 4096 background |

u1's dump holds objects at dwords 0, 27 and 54, each with 0 at +11 and 0x00040101 at +12; u2's dump
head (dwords 0 to 63) and its target hash 0x8ea26cdfee74a325 are E888's.

In u3 and u4 every poke was applied (the kernel's lines) and its value was in the dump.

**What it shows.** The 3D reads render 2's object in the bit-29-set layout too: put there, it
draws the triangle over the whole target with render 3's colours; with 0xffffffff where it takes
the format word, nothing. Render 1's object stayed displaced in u3 and render 2's still drew, so the
3D does not stop at a displaced object: it reads each object's format word where the bit-29-set
layout puts it and skips one it cannot draw [infer]. With E829 and E888 the inserted zero is the
whole reason the image is empty, for every object of the scene. u2 shows the 41E2F5C7 module
reproduces E888's row on the 99CD90DA module byte for byte where frozen.

**What it does not show.** What the inserted dword is for: no finite test, set aside in round 6.
One triangle a render, 64 x 64, `CR_TE_AA` 0x40000000 only; render 3's own object was not poked.
