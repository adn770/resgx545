+++
id = "E1103"
claim = "r25-csc stage csc (16 jobs): a fill's transfer command loads colour-space set 0 when its load flag is set (xfer:17 bit 0, the set's words xfer:18 to 22), and a fill without the flag keeps the set the last load left: per format 28 and 29, after E037's UYVY copy loaded set 0 with zeros (hash 0xd3522437a14b6325, black) the unpoked fill read opaque black, the fill poked with the BT.601 words read E037's conversion of its texel and the next unpoked fill the conversion again (H-FILLLOAD fit 4 of 4); after the copy loaded BT.601 (0xb6067a95fa98de2d) the unpoked fill read the conversion, the fill poked with zeros read opaque black and the next unpoked fill black again (H-FILLLOAD held out 4 of 4); H-FILLIGNORE (the fills read the copy's set) 0 of 4 and 0 of 4; every control passed and every poke was echoed as sent"
unit = "texture"
method = "r25-csc (render/closing-r25-csc), stage csc of the question-closing pass (round 25: closing24/DECISIONS-R24.md, session r25-csc of the round 24 plan (closing24/plan/rank-round24.md), sections 2.2 and 5, R24-1 to R24-6 (a), safe class), dataset render-closing-r25-csc; attempt out/20261115-213805 (scores score-csc.txt); on the laptop over the travel cable (host cedar, kernel 7.3.0-resgx545, module srcversion E0CC40275493F8AEAD8180B (linux fork 456404fcffe5; installed and loaded alike), stock firmware, tool ~/sgxfive-test-t22 (t22, sha256 9b62d31539564b0ca9e949aa1b44e325455b485a985fdfa65976684888d219ee, built on the laptop from resgx545 3c68e8d by lead/build_tool22_laptop.sh: probe --poke keeps its poke set alive through the job and echoes `probe NAME: poked SPACE:N 0xOLD -> 0xNEW`), every job one process of the kit runner (kit/run_stage.sh) in table order, a debugfs reset between jobs and the health fill and triangle (t10) only at the stage's ends, every output kept gzipped; the rows are tables/csc.txt, the programs bins/ (E568's fy-28-p0 and fy-29-p0 as r23-pk ran them) and the frozen predictions predictions/csc.tsv (gen/make.py)); freezes: FROZEN.sha256 b27f072b6916129e0fe05bc471ca43a36537d053266a7c62b9e3cb6b797c9e08 (56 files), PREDICTIONS.sha256 2602aac18f3ff675314b8084ab526195a0361e961175b666bcc725f6e7cb978d (1 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 7f214e51, resgx545:tools/closing/kit/lib_kit.sh at 7f214e51, resgx545:tools/closing/kit/run_stage.sh at 7f214e51, resgx545:tools/closing/kit/kitscore.py at 7f214e51, resgx545:tools/closing/kit/fake/sudo at 7f214e51, resgx545:tools/closing/kit/fake/timeout at 7f214e51, resgx545:tools/closing/kit/fake/df at 7f214e51, resgx545:tools/closing/kit/fake/modinfo at 7f214e51, resgx545:tools/closing/kit/fake/sha256sum at 7f214e51, resgx545:tools/closing/kit/fake/tool.sh at 7f214e51, resgx545:tools/closing/kit/fake/tool.py at 7f214e51, resgx545:tools/closing/kit/fake/ssh.py at 7f214e51, resgx545:tools/closing/scorekit.py at 7f214e51, resgx545:tools/closing/sessioncheck.py at 7f214e51, data:render/closing-r23-pk/bins/fy-28-p0-csc.bin at 40050d0a, data:render/closing-r23-pk/bins/fy-29-p0-csc.bin at 40050d0a, data:render/closing-r23-pk/out/20261115-202948/q181/fy-28-p0-csc.txt.gz at 40050d0a, data:render/closing-r23-pk/out/20261115-202948/q181/fy-29-p0-csc.txt.gz at 40050d0a, data:render/closing-r23-pk/out/20261115-202948/q181/c-copy-csc.txt.gz at 40050d0a, data:render/closing-r23-pk/out/20261115-202948/q181/c-copy-none.txt.gz at 40050d0a, data:render/closing-r23-pk/tables/q181.txt at 40050d0a, data:render/closing-r23-pk/lead/build_tool22_laptop.sh at 40050d0a, data:render/closing-r10-st1/lead/build_tool10.sh at 40050d0a, 3c68e8de6bdfeecd37b97e2d6095fef932e0e6d9 at built, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 396252bdb513282a17ed9c17446754c6478984fc423fba55236b6865bfb023c0 3c68e8de6bdfeecd37b97e2d6095fef932e0e6d9:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=E0CC40275493F8AEAD8180B; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-15"
data = ["render-closing-r25-csc:out/20261115-213805/csc/", "render-closing-r25-csc:fold/"]
terms = ["transfer_cmd.load_yuv_csc", "TEXFORMAT"]
+++
**What ran.** Per format F of 28 and 29, in this order: yF-zc, E037's `copy --every-value
--pixels` with the UYVY texture words (tex:1=0x7d03f01f, tex:0^=0x90), xfer:17^=0x1 and xfer:18 to
22 all zero (control, frozen E037's black hash); yF-a, E568's fy-F-p0 fill `probe --temps 32
--coords --pixels` unpoked (control, frozen black); yF-b, the fill with xfer:17^=0x1 and the
BT.601 words 0x00950095, 0x00000095, 0x010203ce, 0x039800cc, 0 (fit); yF-c, the fill unpoked
(fit); yF-bc, the copy loading the BT.601 words (control, frozen E037's 0xb6067a95fa98de2d);
yF-d, the fill unpoked (control, frozen E1097's conversion); yF-e, the fill with xfer:17^=0x1 and
xfer:18 to 22 zero (held out); yF-f, the fill unpoked (held out). Frozen per fill H-FILLLOAD (a
poked fill loads its words, an unpoked one keeps the set) against H-FILLIGNORE (the fills read
the set the copy loaded); conversion is E1097's measured pixel sha256 (r23-pk's kept fy-F-p0-csc),
black 0xff000000 at 2048 pixels. A fill is decided only when the controls of its half before it
passed.

**Frozen verdict (as printed).** attempt 20261115-213805, stage csc (score-csc.txt): `SUMMARY:
csc: controls all passed`; `SUMMARY: csc: H-FILLLOAD (fit) (4 of 4 rows decided)`; `SUMMARY:
csc: H-FILLLOAD (heldout) (4 of 4 rows decided)`; `SUMMARY: csc: H-FILLIGNORE (fit) is not
supported: 0 held, 4 FAILED, 0 cannot tell of 4`; `SUMMARY: csc: H-FILLIGNORE (heldout) is not
supported: 0 held, 4 FAILED, 0 cannot tell of 4`. The score reproduces byte for byte
(fold/reproduce.out).

**Results [HW].** Copies: y28-zc and y29-zc 0xd3522437a14b6325, y28-bc and y29-bc
0xb6067a95fa98de2d (E037's both). Fills, pixel sha256: y28-a, y28-e, y28-f, y29-a, y29-e, y29-f
e3a911a4... (black at 2048 of 2048); y28-b, y28-c, y28-d 575a006f... and y29-b, y29-c, y29-d
e3e7e916... (E1097's conversion of fy-28-p0 and fy-29-p0). Every poked fill echoed its six pokes
as sent (xfer:17 0x00000000 -> 0x00000001; xfer:18 to 22 the BT.601 words in b, zero in e); no
unpoked fill echoed any. No fault, hang or stop.

**What it shows.** The fill's transfer command loads colour-space set 0 when its load flag is set,
with the words it carries: BT.601 turns a black set into the conversion, zeros turn a converting
set into black, in both formats, on held-out rows. A fill without the flag does not load and reads
whatever set the last load left, across the runner's debugfs reset (E1097, again here in c, d and
f). Q181's question, whether the fill's transfer command loads the set at all, is answered: it
does, as the copy's does (E037). [infer] E568's eight black jobs and E037's no-load black read an
unloaded set or a set of zeros after boot, consistent with this.

**What it does not show.** What the set holds after boot before any load (zeros fits E037 and
E568, not measured here), whether set 1 or the other set fields (E040) load the same way in a
fill, and other YUV formats or texture sizes.
