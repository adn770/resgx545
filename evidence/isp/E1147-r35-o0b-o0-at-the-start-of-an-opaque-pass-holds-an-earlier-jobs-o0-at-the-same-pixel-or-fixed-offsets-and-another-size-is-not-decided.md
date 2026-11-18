+++
id = "E1147"
claim = "r35-o0b stage o (32 t10 probe triangles, module 7CE8E38E), the corrected rerun of r35-o0 (E1143), every control passed: at the start of an opaque pass's pixel shader, on the pixels that keep a value, o0 holds the o0 an earlier job's shader wrote at the same pixel (130 to 287 pixels a row), 32 rows lower (36 or 85) or 32 columns right and 16 rows up (0 or 4), or a value of a job further back (36 in one row), the background elsewhere, 4 of 4 held-out rows at 64 x 64: 'Q073 RULE (a) same size: controls passed; h1 rows decided 4 of 4; H-OFFSETS 4 held, 0 FAILED ...: DECIDED, H-OFFSETS' (H-SAMEPIX 4 FAILED on h1, H-OTHER 4 FAILED); a debugfs reset between keeps it (2 of 2) and the t10 fill between replaces every kept pixel with its colour (2 of 2); after a job of another size it is not decided: a 64 x 64 pass-through after a 128 x 128 job kept 0 and 12 pixels (the 12 at 80 rows lower), a 128 x 128 one after a 64 x 64 job 0 and 6 (same pixel): 'Q073 RULE (b) other size: ... not decided'; 'Q073 RULE: NARROW: (a) decided; open: (b)'; the offsets were formed post hoc from E1143 and are held out here"
unit = "isp"
method = "r35-o0b (render/closing-r35-o0b), stage o of the question-closing pass (round 35: closing29/plan/rank-round35.md section 3.1, the corrected rerun of r35-o0 after E1143, safe class), dataset render-closing-r35-o0b; attempt out/20261118-091726 (scores score-o.txt); on the laptop at home (192.168.12.234, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06) for every row (`probe --temps 32 --pixels --tri pixel --width N --height N --max-width 128 --max-height 128 FILE`, N 64 or 128, E417's form; A' with --vtx-coords 2 and E081's pds_iter_xy and vtx_coords slots) and the kit's health pair, every job one process of the kit runner (kit/run_stage.sh at resgx545 204501a), a debugfs reset before every A' and K row and h4's P, `noreset` elsewhere, 2026-11-18 from 09:17:27; the rows are tables/o.txt, the frozen predictions predictions/o.tsv (gen/make.py), the rule score/score.py's q073 command (fold/q073-rule.out), the score reproduced byte for byte (fold/reproduce.out)); freezes: FROZEN.sha256 0cda3a3cb789fa164e2a13b8dda817772cfa4c90e1a580e2b122b76f1e31a6ad (62 files), PREDICTIONS.sha256 1f2837a1f8a3354429d5a9c71ae22a4a29f788f55fff8e020ba9ba64f5334102 (1 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 204501aa, resgx545:tools/closing/kit/lib_kit.sh at 204501aa, resgx545:tools/closing/kit/run_stage.sh at 204501aa, resgx545:tools/closing/kit/kitscore.py at 204501aa, resgx545:tools/closing/kit/fake/sudo at 204501aa, resgx545:tools/closing/kit/fake/timeout at 204501aa, resgx545:tools/closing/kit/fake/df at 204501aa, resgx545:tools/closing/kit/fake/modinfo at 204501aa, resgx545:tools/closing/kit/fake/sha256sum at 204501aa, resgx545:tools/closing/kit/fake/tool.sh at 204501aa, resgx545:tools/closing/kit/fake/tool.py at 204501aa, resgx545:tools/closing/kit/fake/ssh.py at 204501aa, resgx545:tools/closing/scorekit.py at 204501aa, resgx545:tools/closing/sessioncheck.py at 204501aa, data:isp/o0-start/isp-o0-start-64/raw.txt at 1e400772, data:isp/o0-start/isp-o0-start-128/raw.txt at 1e400772, data:isp/o0-start/isp-o0-start-64/bins/isp-o0-start-64__0.bin at 1e400772, data:isp/o0-start/isp-o0-start-64/bins/isp-o0-start-64__1.bin at 1e400772, data:usse/output-registers/usse-output-registers-oreg-x/raw.txt at 1e400772, data:usse/output-registers/usse-output-registers-oreg-y/raw.txt at 1e400772, data:usse/output-registers/usse-output-registers-oreg-x/bins/pds_iter_xy.bin at 1e400772, data:usse/output-registers/usse-output-registers-oreg-x/bins/vtx_coords.bin at 1e400772, data:usse/output-registers/usse-output-registers-oreg-x/bins/usse-output-registers-oreg-x__0.bin at 1e400772, data:render/closing-r34-q010/out/20261116-231015/c/begin.fill1.txt.gz at 1e400772, data:render/closing-r34-q010/out/20261116-231015/c/begin.health1.txt.gz at 1e400772, data:render/closing-r35-o0/fold/posthoc.out at 1e400772, data:render/closing-r35-o0/out/20261118-085126/score-o.txt at 1e400772, resgx545:probes/isp/o0-start.toml at 204501aa, resgx545:probes/usse/output-registers.toml at 204501aa, resgx545:probes/usse/templates/pix_op.s at 204501aa, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; pinned commits named by the session: resgx545 main 204501aac415; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-18"
data = ["render-closing-r35-o0b:out/20261118-091726/o/", "render-closing-r35-o0b:fold/"]
terms = ["ISP0.PASS_TYPE"]
+++
**What ran.** One stage o of 32 t10 probe triangles in a 128 x 128 render context, r35-o0's
programs and groups (E1143) with h1 four times and h5 twice, the second replicate in reverse
group order. A' stores (pa0 & 0xffff0000) | ((pa1 >> 16) & 0xffff), a value unique per pixel
(E081); K stores 0xff00ff00; P stores o0 unchanged (E417's kept bytes). Groups: c0 (A' 64, 128),
c1 (K then P, twice), h1 (A' 64 then P 64, four times), h2 (A' 128 then P 64), h3 (A' 64 then P
128), h4 (A' 64, a debugfs reset, P 64), h5 (A' 64, the t10 fill, P 64); every P `noreset` but
h4's. The fix after E1143, frozen before the run: an A' control gates only its own group and the
rows of its size, and the 128 x 128 A' control passes with 98 % of its pixels A'(x, y). The fit
is E1143's post hoc reading (offsets (0, 0), (0, 32), (32, -16), (0, -16) at 64 x 64; (0, 0),
(-64, -16) for a 128 x 128 pass-through after a 64 x 64 job); every P row is held out.

**Frozen verdict (as printed).**

```
SUMMARY: o: H-FILLREPLACE: the t10 fill between replaces it with the fill's colour (2 of 2 rows decided)
SUMMARY: o: H-OFFSETS: o0 at the start of the opaque pass holds an earlier job's o0 at the same pixel or at a fixed offset (E1143's set), or a value of a job further back (4 of 4 rows decided)
SUMMARY: o: H-OFFSETS128: a 128 x 128 pass-through after a 64 x 64 job reads it at E1143's offsets (1 of 2 rows decided)
SUMMARY: o: H-OTHER: o0 holds neither is not supported: 0 held, 4 FAILED, 0 cannot tell of 4
SUMMARY: o: H-RESETCLEAR: a debugfs reset between leaves none of the previous job's o0 is not supported: 0 held, 2 FAILED, 0 cannot tell of 2
SUMMARY: o: H-RESETKEEP: a debugfs reset between keeps the previous job's o0 (2 of 2 rows decided)
SUMMARY: o: H-SAMEPIX: o0 holds the previous job's o0 at the same pixel is not supported: 1 held, 4 FAILED, 1 cannot tell of 6
SUMMARY: o: H-SIZEKEEP: a 64 x 64 pass-through after a 128 x 128 job keeps some pixel is not supported: 1 held, 1 FAILED, 0 cannot tell of 2
SUMMARY: o: H-SIZENONE: a 64 x 64 pass-through after a 128 x 128 job keeps no pixel is not supported: 1 held, 1 FAILED, 0 cannot tell of 2
SUMMARY: o: H-TRIONLY: the previous triangle's o0 survives the t10 fill between is not supported: 0 held, 2 FAILED, 0 cannot tell of 2
Q073 RULE: NARROW: (a) decided; open: (b)
```

**Results [HW].**

- Controls: 18 of 18 passed. A' at 64 x 64: 1062 of 1062 pixels A'(x, y) (14 rows); at 128 x
  128: 4272, 4274 and 4275 of 4284 (the rest another pixel's value, as in E1143). P after K kept
  K on 426 and 304 of 1062 pixels.
- h1 (A' 64 then P 64), kept pixels by where they read A': h1a 206 (130 at (0, 0), 36 at (0,
  32), 4 at (32, -16), 36 a value of an earlier row), h1b 372 (287, 85), h1c 262 (173, 85, 4),
  h1d 188 (148, 36, 4). The offset (0, -16) of E1143's h1c did not recur.
- h4 (a reset between): 414 (378 at (0, 0), 36 at (0, 32)) and 323 (238, 85). h5 (the fill
  between): 651 and 651 pixels, all of the fill's colour 0xff336699.
- h2 (P 64 after A' 128): 0 and 12 kept pixels (the 12 read A' 80 rows lower). h3 (P 128 after
  A' 64): 0 and 6 (at (0, 0)).

**What it shows.** In the opaque pass, o0 at the start of a pixel's shader holds, on the pixels
that keep one, the o0 that the previous job's shader wrote at the same pixel or at the pixel 32
rows lower or 32 columns right and 16 rows up, else a value of a job further back, and the
background on the other pixels; a debugfs reset does not clear it and a fill between replaces it.
The offsets are the tile height's multiples [infer: the pixel's slot in an earlier tile's
output buffer]. The counts vary between runs (188 to 414 at 64 x 64, E417's 390 to 450).

**What it does not show.** After a previous job of another size: the 64 x 64 pass-through after
a 128 x 128 job kept 0 or 12 pixels, the 128 x 128 one after a 64 x 64 job 0 or 6, so neither
frozen rule held on both rows. Which pixels keep a value and why these offsets; the translucent
pass.
