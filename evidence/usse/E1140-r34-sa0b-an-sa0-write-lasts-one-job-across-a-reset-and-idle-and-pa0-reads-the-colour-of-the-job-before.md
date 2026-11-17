+++
id = "E1140"
claim = "r34-sa0b stage s (54 jobs, t30 probe fills whose readers output the value read, module 7CE8E38E), the corrected rerun of r34-sa0 (E1139), every control passed (16 sa0 writers read their marker back in dword 0, K1 their most frequent colour; 6 colour fills K3): an sa0 value written by iaddu32 in a fill's pixel task is read by the next job in 2048 of 2048 pixels with no job between, across a debugfs reset and 10, 60 and 120 s idle (10 of 10 rows), and a job between (a colour fill, the t10 fill, the t10 triangle) replaces it with that job's colour (6 of 6): 'Q136 RULE (a): ... R rows decided 16 of 16; holding on every row: H-ONEJOB ... DECIDED, H-ONEJOB' (H-PERSIST 6 FAILED, H-COLOUR 10 FAILED, H-RESET 2 and H-IDLE 6 FAILED); pa0 reads the colour the job before output, after a colour fill and the t10 fill (4 of 4 held out, a reset between too, 2 of 2) and after the t10 triangle 0xff00ff00 in 1536 and 0xff203040 in 512 pixels (both fits, as the sa0 readers after the triangle), E496's first-job mixture: 'Q136 RULE (b): ... H-PREV 4 held ... H-FIXED 0 held, 4 FAILED ...: DECIDED, H-PREV'; 'Q136 RULE: RETIRE-CAPABLE (both clauses decided)'; H-ONEJOB and H-PREV were formed post hoc from E1139 and are held out here on new rows"
unit = "usse"
method = "r34-sa0b (render/closing-r34-sa0b), stage s of the question-closing pass (round 34: closing29/plan/rank-round34.md section 3.6, the corrected rerun of r34-sa0 after E1139, safe class), dataset render-closing-r34-sa0b; attempt out/20261117-005911 (scores score-s.txt); on the laptop over the travel cable (host cedar, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (installed and loaded alike), stock firmware, tools ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, built from resgx545 42c4de7) for every probe fill (`probe --temps 32 FILE`, 64 x 32, 2048 instances, our program as the pixel task) and ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06) for the fill and triangle rows and the kit's health pair, every job one process of the kit runner (kit/run_stage.sh at resgx545 914dd23), a debugfs reset before each group's first row and the rs and pk3r readers, `noreset` elsewhere, idle:10/60/120 on the idle readers, 2026-11-17 from 00:59:11; the rows are tables/s.txt, the frozen predictions predictions/s.tsv (gen/make.py), the rule score/score.py's q136 command (fold/q136-rule.out), the score reproduced byte for byte (fold/reproduce.out)); freezes: FROZEN.sha256 e59f56e7407e3829a96c8baa9fb094171b84781ee6a5d3b8097448f6012fdb64 (62 files), PREDICTIONS.sha256 f3e8e2359f33eaa21a0961faa7868f8a41ce8ea160d05eadb7194e711b77435e (1 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 914dd232, resgx545:tools/closing/kit/lib_kit.sh at 914dd232, resgx545:tools/closing/kit/run_stage.sh at 914dd232, resgx545:tools/closing/kit/kitscore.py at 914dd232, resgx545:tools/closing/kit/fake/sudo at 914dd232, resgx545:tools/closing/kit/fake/timeout at 914dd232, resgx545:tools/closing/kit/fake/df at 914dd232, resgx545:tools/closing/kit/fake/modinfo at 914dd232, resgx545:tools/closing/kit/fake/sha256sum at 914dd232, resgx545:tools/closing/kit/fake/tool.sh at 914dd232, resgx545:tools/closing/kit/fake/tool.py at 914dd232, resgx545:tools/closing/kit/fake/ssh.py at 914dd232, resgx545:tools/closing/scorekit.py at 914dd232, resgx545:tools/closing/sessioncheck.py at 914dd232, data:usse/pa-dest/usse-pa-dest-persist/raw.txt at a3287ec6, data:usse/pa-dest/env.toml at a3287ec6, data:render/closing-r34-q010/out/20261116-231015/c/begin.fill1.txt.gz at a3287ec6, data:render/closing-r34-q010/out/20261116-231015/c/begin.health1.txt.gz at a3287ec6, data:render/closing-r34-sa0/fold/posthoc.out at a3287ec6, 42c4de7855d6f310321cc03fa0780b698a735e4d at built, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 253fd15bcb6a0a6381d20aacbb635af1c99d764388f394f9a24dc61266b6418d 42c4de7855d6f310321cc03fa0780b698a735e4d:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; pinned commits named by the session: resgx545 main 914dd2323f79; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-17"
data = ["render-closing-r34-sa0b:out/20261117-005911/s/", "render-closing-r34-sa0b:fold/"]
terms = []
+++
**What ran.** One stage s of 54 jobs in 12 groups, the second replicate in reverse order. Each
probe is a plain t30 fill whose pixel task runs one body in every instance. A writer W runs
`iaddu32.testtaz.chan0 sa0, p0, r1, r2` (r1 = 1, r2 = M - 1, so M), `mov r3, sa0`, dword 0 = r3,
o0 = K1 0xc0de0a01; its marker M is 0x5a0c0a01-08 or 0x5a0c0b01-08, one per row. A reader R runs
`mov r10, sa0` and P runs `mov r10, pa0`, each storing r10 to dword 0 and outputting it as o0
(E496's form; E1139's keyed readers aliased their own outputs). A colour fill K writes no sa or
pa: o0 = K3 0xc0de0a03. The groups:

- W, R with no job between: nr (noreset), rs (a debugfs reset), and i10, i60, i120 (noreset with
  10, 60 or 120 s idle);
- W, X, R with one job between: k3 (X = K), fl (t10 `fill`), tr (t10 `tri`);
- X, P: ptr (t10 tri, fit), pk3 (K), pfl (t10 fill), pk3r (K, then a reset).

**Frozen verdict (as printed).** fold/q136-rule.out: "Q136 RULE (a): controls 18 of 18 passed; R
rows decided 16 of 16; holding on every row: H-ONEJOB; H-PERSIST 10 held, 6 FAILED, 0 cannot tell
of 16; H-ONEJOB 16 held, 0 FAILED, 0 cannot tell of 16; H-COLOUR 6 held, 10 FAILED, 0 cannot tell
of 16; H-RESET 0 held, 2 FAILED, 0 cannot tell of 2; H-IDLE 0 held, 6 FAILED, 0 cannot tell of 6:
DECIDED, H-ONEJOB". "Q136 RULE (b): controls 4 of 4 passed; ptr fits read TRI: yes; H-PREV 4
held, 0 FAILED, 0 cannot tell of 4, H-FIXED 0 held, 4 FAILED, 0 cannot tell of 4 on pk3, pfl;
pk3r: pk3ra-p PREV, pk3rb-p PREV: DECIDED, H-PREV". "Q136 RULE: RETIRE-CAPABLE (both clauses
decided)".

**Results [HW].** Every reader's pixels were one value, or the triangle's two:

- after its writer, with or without a reset or idle: the marker in 2048 of 2048 pixels (10 rows);
- after K: K3 x2048; after the t10 fill: 0xff336699 x2048;
- after the t10 triangle, sa0 and pa0 readers alike: 0xff00ff00 x1536 and 0xff203040 x512.

Each reader's dword 0 was one of its pixel values. The writers read M back in dword 0 and output
K1 in 2044 pixels and M in 4 (E484's odd pixels). No job failed or hung, and no BIF fault line
appeared.

**What it shows.** [HW] An sa0 value written in a fill's pixel task is read by the next job: it
survives a debugfs reset and 120 s idle with no job between. Any job between, a fill writing no
sa or the 3D health triangle, replaces it with that job's colour. So it lasts one job, as E484
had for sa1, sa5 and sa7, and E496's job 8 was the write persisting, not only the colour rule.
[HW] pa0 in a fill's pixel task reads the colour of the job before, across a reset too. After the
health triangle that colour is 0xff00ff00 in 1536 and 0xff203040 in 512 pixels, E496's first-job
mixture count for count. [infer] E496's table ran after a triangle (its `before` line), so its
first jobs' mixture was that triangle's colour. H-ONEJOB and H-PREV were formed post hoc from
E1139 and hold here on held-out rows of a new run.

**What it does not show.** An o destination; operands other than sa0 and pa0; the other
registers of the banks; which instance reads which slot, and why a triangle's 64 x 64 render
reads as 1536 and 512 of a 64 x 32 fill (Q129, Q193); idle beyond 120 s; a module reload or
power cycle; the kernel's own jobs other than a debugfs reset.
