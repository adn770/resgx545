+++
id = "E1139"
claim = "r34-sa0 stage s (60 jobs, t30 probe fills, module 7CE8E38E): every control passed (18 sa0 writers read their marker M back in dword 0 with K1 their most frequent colour, 6 colour fills K3), but the frozen reader decode (each pixel = the value read xor a key) did not hold: every reader's pixels came in pairs {x, x ^ key}, about 1904 and 144 of 2048, so 18 of 20 sa0 readers and every pa0 row read cannot tell and the frozen rule printed 'Q136 RULE: NARROW: neither clause decided' (a builder error: the reader form had no control on a known value; the 'held' H-RESET 2 of 2, H-IDLE 6 of 6 and the two rr-r2 rows are artefacts of that decode); post hoc [infer], taking the more frequent member of each pair as the value read before the job's own o0 writes (a reader's read aliases what earlier instances of the job wrote to o0): sa0 read its marker after the writer with no job between, across a debugfs reset and 10, 60 and 120 s idle (14 of 14 rows), and the output of a job between (a colour fill, the t10 fill, the t10 triangle, a reader; 8 of 8), H-ONEJOB's pattern on 20 of 20; pa0 read the colour of the job before on 8 of 8 rows, a reset between included, and after the t10 triangle 0xff00ff00 in 1536 and 0xff203040 in 512 pixels in both replicates, E496's first-job mixture count for count; nothing post hoc decides: the corrected rerun r34-sa0b freezes it"
unit = "usse"
method = "r34-sa0 (render/closing-r34-sa0), stage s of the question-closing pass (round 34: closing29/plan/rank-round34.md section 3.6 with the lead's sketch, safe class), dataset render-closing-r34-sa0; attempt out/20261117-001613 (scores score-s.txt); on the laptop over the travel cable (host cedar, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (installed and loaded alike), stock firmware, tools ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, built from resgx545 42c4de7) for every probe fill (`probe --temps 32 FILE`, 64 x 32, 2048 instances, our program as the pixel task) and ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06) for the fill and triangle rows and the kit's health pair, every job one process of the kit runner (kit/run_stage.sh at resgx545 fd916fe), a debugfs reset before each group's first row and the rs readers, `noreset` elsewhere, idle:10/60/120 on the idle readers, 2026-11-17 00:16:14 to 00:25:55; the rows are tables/s.txt, the frozen predictions predictions/s.tsv (gen/make.py), the rule score/score.py's q136 command (fold/q136-rule.out), the score reproduced byte for byte (fold/reproduce.out), the post hoc reading fold/posthoc.py (fold/posthoc.out)); freezes: FROZEN.sha256 dd0e281425bfeb36c814afe2841dc684835ac107b0c8d62c7a05b540399d6bc4 (63 files), PREDICTIONS.sha256 2d17def4b149e33b7f9aa2e197d6ba6b0b0adfe008ce4c468c1420066e12ed77 (1 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at fd916fed, resgx545:tools/closing/kit/lib_kit.sh at fd916fed, resgx545:tools/closing/kit/run_stage.sh at fd916fed, resgx545:tools/closing/kit/kitscore.py at fd916fed, resgx545:tools/closing/kit/fake/sudo at fd916fed, resgx545:tools/closing/kit/fake/timeout at fd916fed, resgx545:tools/closing/kit/fake/df at fd916fed, resgx545:tools/closing/kit/fake/modinfo at fd916fed, resgx545:tools/closing/kit/fake/sha256sum at fd916fed, resgx545:tools/closing/kit/fake/tool.sh at fd916fed, resgx545:tools/closing/kit/fake/tool.py at fd916fed, resgx545:tools/closing/kit/fake/ssh.py at fd916fed, resgx545:tools/closing/scorekit.py at fd916fed, resgx545:tools/closing/sessioncheck.py at fd916fed, data:usse/pa-dest/usse-pa-dest-persist/raw.txt at 9a809796, data:usse/pa-dest/env.toml at 9a809796, data:render/closing-r34-q010/out/20261116-231015/c/begin.fill1.txt.gz at 9a809796, data:render/closing-r34-q010/out/20261116-231015/c/begin.health1.txt.gz at 9a809796, 42c4de7855d6f310321cc03fa0780b698a735e4d at built, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 253fd15bcb6a0a6381d20aacbb635af1c99d764388f394f9a24dc61266b6418d 42c4de7855d6f310321cc03fa0780b698a735e4d:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; pinned commits named by the session: resgx545 main fd916fedc118; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-17"
data = ["render-closing-r34-sa0:out/20261117-001613/s/", "render-closing-r34-sa0:fold/"]
terms = []
+++
**What ran.** One stage s of 60 jobs in 13 groups, the second replicate in reverse order. Each
probe is a plain t30 fill whose pixel task runs one body in every instance. A writer W runs
`iaddu32.testtaz.chan0 sa0, p0, r1, r2` (r1 = 1, r2 = M - 1, so M), `mov r3, sa0`, dword 0 = r3,
o0 = K1 0xc0de0a01; its marker M is 0x5a0c0a01-09 or 0x5a0c0b01-09, one per row. An sa0 reader R
runs `mov r3, sa0`, dword 0 = r3, o0 = r3 ^ 0x33330000. A pa0 reader P does the same with pa0 and
0x00550000. A colour fill K writes no sa or pa: dword 0 = o0 = K3 0xc0de0a03. The groups:

- W, R with no job between: nr (noreset), rs (a debugfs reset), and i10, i60, i120 (noreset with
  10, 60 or 120 s idle);
- W, X, R with one job between: k3 (X = K), fl (t10 `fill`, 0xff336699), tr (t10 `tri`, colours
  0xff00ff00 and 0xff203040);
- rr: W, R, R;
- X, P: ptr (t10 tri, fit), pk3 (K), pfl (t10 fill), pk3r (K, then a reset).

**Frozen verdict (as printed).** fold/q136-rule.out: "Q136 RULE (a): controls 20 of 20 passed; R
rows decided 2 of 20; holding on every row: none; H-PERSIST 0 held, 2 FAILED, 18 cannot tell of
20; H-ONEJOB 2 held, 0 FAILED, 18 cannot tell of 20; H-COLOUR 2 held, 0 FAILED, 18 cannot tell of
20; H-RESET 2 held, 0 FAILED, 0 cannot tell of 2; H-IDLE 6 held, 0 FAILED, 0 cannot tell of 6: not
decided (a held-out R row is not decided)". "Q136 RULE (b): controls 4 of 4 passed; ptr fits read
TRI: no; H-PREV 0 held, 0 FAILED, 4 cannot tell of 4, H-FIXED 0 held, 0 FAILED, 4 cannot tell of
4 on pk3, pfl; pk3r: pk3ra-p cannot tell, pk3rb-p cannot tell: not decided". "Q136 RULE: NARROW:
neither clause decided".

**Results [HW].** Every control passed: 18 writers (dword 0 = M; o0 K1 x2044 and M x4, E484's odd
pixels) and 6 K rows (K3 x2048). Every reader's pixels came in pairs {x, x ^ key}. For example:

- nra-r: 0x5a0c0a01 x1904 and 0x693f0a01 x144, dword 0 0x693f0a01;
- k3a-r: 0xc0de0a03 x1904 and 0xf3ed0a03 x144;
- fla-r: 0xff336699 x1812 and 0xcc006699 x236;
- tra-r: 0xff00ff00 x1432, 0xff203040 x472, 0xcc33ff00 x104 and 0xcc133040 x40;
- rra-r2: 0x693f0a09 x1904 and 0x5a0c0a09 x144;
- pk3a-p: 0xc0de0a03 x1904 and 0xc08b0a03 x144;
- ptra-p: 0xff00ff00 x1416, 0xff203040 x472, 0xff55ff00 x120 and 0xff753040 x40.

The other rows read the same forms (fold/posthoc.out). No job failed or hung, and no BIF fault
line appeared.

**What it shows.** The frozen decode assumed each pixel was its own instance's read xored with the
key. That assumption fails on 28 of 28 readers: a builder error, with no control for the reader
form. The scorer's 'held' lines for H-RESET, H-IDLE and the rr-r2 rows come from that decode, not
from the hardware.

Post hoc [infer] (fold/posthoc.py): what a reader reads aliases what earlier instances of the same
job already wrote to o0. Instances that read first output v ^ key; later ones read that back and
output v. This matches the larger member of each pair and dword 0 (the last store) being mostly
v ^ key. With v the larger member:

- sa0 reads the writer's M with no job between, across a debugfs reset and 120 s idle (14 rows),
  and the output of a job between (8 rows: K3, 0xff336699, the triangle's two colours, rr's
  first reader's keyed colour). That is H-ONEJOB's pattern on 20 of 20 rows, and it separates
  E496's job 8 from the colour rule.
- pa0 reads the colour the job before output on 8 of 8 rows, across a reset (pk3r). After the t10
  triangle it reads 0xff00ff00 in 1536 and 0xff203040 in 512 pixels in both replicates
  (1416 + 120, 472 + 40). These are E496's first-job counts, and E496's table ran after a
  triangle (`before` in env.toml).

None of this was frozen, so none of it decides.

**What it does not show.** A decided answer to either clause of Q136; the aliasing itself (which
instance reads which slot, and why the counts are about 1904 and 144: Q129, Q193); readers whose
own output does not feed back. The corrected rerun r34-sa0b freezes these post hoc readings as
its fit, with readers that output the value read (E496's form).
