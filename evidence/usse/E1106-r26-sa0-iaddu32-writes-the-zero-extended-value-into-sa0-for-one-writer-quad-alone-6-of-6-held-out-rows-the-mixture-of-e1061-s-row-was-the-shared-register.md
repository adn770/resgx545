+++
id = "E1106"
claim = "r26-sa0 stages uc and us (8 jobs, t24 `probe --coords`) on module E0CC4027: a single writer alone writes iaddu32's value into sa0 and it is the zero-extended one: eight (r1, source 2) pairs a program, `iaddu32.testtaz.chan0 sa0, p0, r1, r2`, `mov r3, sa0` and a store of r3 to the pair's own dword, run by one 2x2 quad selected as E513 selects it (`xor.testtaz` of pa0 and `!p0 br` over the body), read (r1 & 0xffff) + source 2 on 8 of 8 dwords in all six held-out rows (E1061's pairs at quad (0, 0) twice and at quad (62, 30), eight new pairs of seed 26126 at both quads and once more at (0, 0): 'H-ZX (heldout) (6 of 6 rows decided)'; H-SX, the sign extension, 1 of 8 dwords on E1061's pairs (the 0x7fff pair, where both agree) and 0 of 8 on the new ones, 'not supported: 0 held, 6 FAILED'; H-MIX, E1061's mixture, 0 of 6, 'not supported: 0 held, 6 FAILED'); both gate controls passed (c-e521, E1061's u-ctl-e521 program byte for byte, H-E521 8 of 8; c-one-r10, the branch form into r10, H-ZX 8 of 8 with `o0 mixed 0xc0de0001 x2044 0x0001ffff x4`: exactly the four lanes of one quad wrote r10) [HW]; so the mixture of E1061's sa0 row was other instances writing the shared sa0 (post hoc [infer] confirmed by its absence with one writer quad); E1061's frozen verdict stays as printed"
unit = "usse"
method = "r26-sa0 (render/closing-r26-sa0), stages uc, us of the question-closing pass (round 26: its decisions, session r26-sa0 of round 26's plan, section 2.2, with R26-1 to R26-7 (a), safe class), dataset render-closing-r26-sa0; attempt out/20261115-224747 (scores score-uc.txt, score-us.txt); on the laptop over the travel cable (host cedar, kernel 7.3.0-resgx545, module srcversion E0CC40275493F8AEAD8180B (linux fork 456404fcffe5; installed and loaded alike), stock firmware, tool ~/sgxfive-test-t24 (t24, sha256 fd15fce4ca75b3868fd42b7e5d639ae8a3096fc895543e25a707bac9fb5db040, built on the laptop from resgx545 1341034, recipe data render/closing-r25-sa64/lead/build_tool24_laptop.sh) and ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06, the health fill and triangle only), client pixel tasks: `probe --coords --temps 32 FILE`, one 64 x 32 copy of 2048 instances a job (pa0 = (y << 16) | x), each program storing eight values to scratch dwords 0-7 which the tool prints, a debugfs reset and the kit's health check around each job, no knob written; every row replayed on the library mock built from t24's source before the freeze (program not simulated), 8 jobs, one attempt (out/20261115-224747), 2026-11-15 from 22:47:47, rc 0, no stop, fault or lead decision; the freeze FROZEN.sha256 written before the first job; scored by the frozen score/score.py, reproduced byte for byte at the fold (fold/reproduce.out); fold/lead-run.log and fold/lead-stage.log the lead's driver logs; debug/ and the bytecode caches are not in the copy; freezes: FROZEN.sha256 64b14fd7c622e95484873e66dfdcf8a6d56514a05851b2fdf99687187b7dd1c9 (50 files), PREDICTIONS.sha256 9d57f25e65c0eeb232c02ff7ce176abf52d1d3f296685847aeb4ce161135d3a5 (2 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 95445c7d, resgx545:tools/closing/kit/lib_kit.sh at 95445c7d, resgx545:tools/closing/kit/run_stage.sh at 95445c7d, resgx545:tools/closing/kit/kitscore.py at 95445c7d, resgx545:tools/closing/kit/fake/sudo at 95445c7d, resgx545:tools/closing/kit/fake/timeout at 95445c7d, resgx545:tools/closing/kit/fake/df at 95445c7d, resgx545:tools/closing/kit/fake/modinfo at 95445c7d, resgx545:tools/closing/kit/fake/sha256sum at 95445c7d, resgx545:tools/closing/kit/fake/tool.sh at 95445c7d, resgx545:tools/closing/kit/fake/tool.py at 95445c7d, resgx545:tools/closing/kit/fake/ssh.py at 95445c7d, resgx545:tools/closing/scorekit.py at 95445c7d, resgx545:tools/closing/sessioncheck.py at 95445c7d, data:vectors/usse/decoder-vectors/usse-decoder-vectors-iaddu32-taz.vec.json at e639458f, data:vectors/usse/integer/usse-integer-iaddu32-value.vec.json at e639458f, data:usse/closing-r16-usse/out/20261114-092913/uadd/u-ctl-e521.txt.gz at e639458f, data:usse/closing-r16-usse/out/20261114-092913/uadd/u-i0.txt.gz at e639458f, data:usse/closing-r16-usse/out/20261114-092913/uadd/u-sa0.txt.gz at e639458f, data:render/closing-r10-st1/lead/build_tool10.sh at e639458f, 134103452432f328eac27ec148499cc3149cf83b at built, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: df2e8b82d089fe6d91e4a72f46ccfb22127a167a4008a529b398c4dfba14b13b 134103452432f328eac27ec148499cc3149cf83b:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=E0CC40275493F8AEAD8180B; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-15"
data = ["render-closing-r26-sa0:out/20261115-224747/uc/", "render-closing-r26-sa0:out/20261115-224747/us/", "render-closing-r26-sa0:fold/"]
terms = []
+++
**What ran.** Every program is a `probe --coords` fill (pa0 = (y << 16) | x, 2048 instances) over
eight (r1, source 2) pairs, one value stored to its own scratch dword a pair. The writer is chosen
as
E513 chose a quad: `mov r7, pa0`, `xor.testtaz.chan0 !c0, p0, r7, r9` (r9 = the writer's pa0) and
`!p0 br #m` over the body, whose branch is decided per 2x2 quad from its top-left lane (E513 [HW]).
The plan's one lane (63, 31) is an odd lane and would select nothing, so the second writer is the
quad whose top-left lane is (62, 30) (pa0 = 0x001e003e; its fourth lane is (63, 31)). uc: c-e521
(E1061's u-ctl-e521 program byte for byte, every instance, E521's eight pairs into r10) and
c-one-r10
(the branch form, quad (0, 0), E1061's u-sa0 pairs into r10, stored from r10). us:
`iaddu32.testtaz.chan0
sa0, p0, r1, r2`, `mov r3, sa0`, `stad [r29,+#k], r3` per pair, the eight pairs of E1061's u-sa0 row
(r1 = 0x8000, 0x8001, 0xabcd, 0xffff, 0x7fff, 0xffff8000, 0x1234fedc, 0xffffffff) or eight new ones
(r1's low half 0x8000-0xffff, r1's high half and source 2 drawn with seed 26126), then `idf drc0,
bif`,
`wdf drc0` and `o0 = r10` in every instance: s-00-a and s-00-b (quad (0, 0), E1061's pairs, the same
program twice), s-6331-a (quad (62, 30), the same), s-new-a and s-new-b (quad (0, 0), new pairs),
s-new-6331 (quad (62, 30), new pairs).

**Frozen verdict (as printed).** `out/20261115-224747/score-uc.txt`: "CONTROL c-e521: H-E521 8/8
dwords: PASS", "CONTROL c-one-r10: H-ZX 8/8 dwords; H-SX 1/8 dwords: PASS", "SUMMARY: uc: cannot
tell:
no row decided" (uc has no held-out row; its controls are the gate, "gate us on uc: open").
`score-us.txt`: "ROW s-00-a (heldout): H-ZX 8/8 dwords; H-SX 1/8 dwords; H-MIX 8/8 dwords a pair's
value, 0 not their own: held H-ZX" and the same for the other five rows (H-SX 1/8 on s-00-b and
s-6331-a, 0/8 on the three new-pair rows), "SUMMARY: us: dwords H-MIX (heldout) is not supported: 0
held, 6 FAILED, 0 cannot tell of 6", "SUMMARY: us: dwords H-SX (heldout) is not supported: 0 held, 6
FAILED, 0 cannot tell of 6", "SUMMARY: us: dwords H-ZX (heldout) (6 of 6 rows decided)".

**Results [HW].** s-00-a read 0x00010000, 0x7fff8001, 0x0000abce, 0x0000fffe, 0x00010000,
0x1234d678, 0x8000fedc, 0x0001ffff (E521's zero-extended sums of the eight pairs, each at its own
dword; the pairs 0 and 4 share a value, as E1061 noted); the other five rows read their own H-ZX
values likewise, the new pairs for example 0x8fb31087, 0x3b8dfae8, 0x6d1b0eb5, 0x873ffcc3,
0xa5ef08a9, 0xef93f9c8, 0xa71a1c03, 0x443f0159 in both writers' rows. No dword outside the eight
changed. c-e521 read E521's kept values (8 of 8, o0 uniform 0x11116789); c-one-r10 read the sums of
the u-sa0 pairs in r10 and its pixels `0xc0de0001 x2044, 0x0001ffff x4`: the four lanes of the
quad (0, 0) wrote r10 and the 2044 other instances did not. Job times 389 to 463 microseconds in us,
single samples. No job failed or hung and the kernel log shows no BIF fault (the resets printed
BIF_FAULT 0x0).

**What it shows.** [HW] With one writer quad alone writing sa0, `iaddu32` writes
(r1 & 0xffff) + source 2 into it, as it does into r10, o0, i0 and a scratch dword (E521, E1061), on
six rows over two sets of eight pairs and two quads; H-SX and E1061's mixture read nowhere. [infer]
So E1061's sa0 row (two of eight dwords holding other pairs' values, four values among its pixels)
came from the fill's instances writing one shared sa0 at different times, which is why a lone
writer reads its own values; the sharing itself (one sa0 for the fill's instances) stays Q098's and
Q129's, this row does not read it. [HW] The branch of E513 selects a quad of four lanes: the
pixels of c-one-r10 say exactly four wrote. The other clause of Q126, which extension the test of
iaddu32 reads, is not observable by any test: E498's flag rules (p always true, n never, z true for
(0, 0) only, the sum counted with its carry) give the same flag for every pair under zero and sign
extension of r1, since both extended values and source 2 are non-negative below 2^32 and their
33-bit sum is zero only for (0, 0) [infer, an arithmetic consequence of E498's measured rules, no
run].

**What it does not show.** One lane alone (the writer is a quad of four lanes that write the same
value; whether they run in lockstep is not told, since the rows read no mixture); the value written
into sa0 by an instance of another quad position than (0, 0) and (62, 30); the forms E1061 left
(immediates other than #1 and #127, other constants and destinations g, pa and o other than o0, the
predicate a masked test leaves, masks on the other tests); that sa0 is shared among instances.
