+++
id = "E1172"
claim = "r40-n3e-b11 stage own (row B11, module 83FBFD86, fork 423b436e7f80, emitsb_sbc43, image crumb3 at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): B0's job with bit 10 of the sideband set too (the firmware's #11 value), two attempts: both T read 0x005a3305, S1 0x5a5a3304, M4 0x5a5a3302 and run id 1, state 2, every control passed, 'Q128-B11 RULE: B11-DONE' (H-DM predicted RUN: held); both times the kit's owntask gate after the ok end failed on the fill ('diff: 2048 of 2048 pixels, first (0, 0) 0xdeadbeef expected 0xff336699') with the triangle exact, rc 16, and fill and triangle were ok after the kit's reset; the started entry's sa differed from the issuer's (sa1 0x04400000, sa3-sa11 float-like words, sa12-sa27 the words of pa0-pa15) and its pa read V0 and V2 in every fourth pa as B1's (attempt 2: pa0 0x00000003, pa2 0x32411000); that bit 10 leaves state that breaks the next fill until a reset is inferred"
unit = "edm"
method = "r40-n3e-b11 (render/closing-r40-n3e-b11), stage own of the question-closing pass (round 40: row B11, closing29/n3e/design.md section 3.3; flagged class, the user present with a reset ready), dataset render-closing-r40-n3e-b11; attempts out/20261120-074024 (07:40:24) and out/20261120-084102 (08:41:02, the user's choice), each ending rc 16 at the kit's owntask gate after an ok end, post not run; on the laptop at home (kernel 7.3.0-resgx545, module srcversion 83FBFD860D4E0D4CE691F48 installed and loaded alike, linux fork r40-kernel 423b436e7f80 built on cachix 2026-11-19 (closing29/kernel39c/deliver/423b436e7f80/manifest; red rc 1 and series 12 of 12 PASS, closing29/r40-n3e-logs/cachix-wait.log; the fork's KUnit suite on the Mac shim 40 of 40, closing29/r40-n3e-logs/shim-r40-kernel.log), the one-shot boot of 2026-11-19 at about 23:00, post-boot draws ok; stock firmware), the kit's owntask job kind (kit/ = resgx545 b8528c0, branch r40-n3e, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43.blob (asm/fwtask/emitsb_sbc43.s, sha256 211bb43872a3d6c0c36b0c40baa711fe8f31a1422a13c9f4ec9f3e8e6f5893bf, asm/fwtask/fwtask.map at b8528c0; emitsb14d with only the emit word changed, emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=sbc43` after the stage's reset and health pair (the kernel's arm line: pds2=0, emit image 0x30011100), then one row c1-a of tester command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), the results page, the registers (snap0, snap9) and the gate kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 46e799193ceb816026d95e57059d9bbc51065fe0c0ad5dc05b62459c929b19c9 (49 files), PREDICTIONS.sha256 4ff3ae9e284f6d620cb66b3cfb12101f63930e7d801bfd59f8a5526f6563f675 (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsb14d.s, asm/fwtask/emitsb_sbc43.s and fwtask.map at b8528c0; r35-sa's and r36-n3's kept snapshots at data 9fce0b99; t30's source 42c4de7); the frozen predictions predictions/own.tsv, the rule score/score.py, run by hand on the kept directory (fold/reproduce-own*.out: the stage stopped, so the driver did not score it); the SURVEY lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW", "infer"]
date = "2026-11-20"
data = ["render-closing-r40-n3e-b11:out/20261120-074024/own/", "render-closing-r40-n3e-b11:out/20261120-084102/own/", "render-closing-r40-n3e-b11:fold/"]
terms = []
+++
**What ran.** B0's job (E1162) with one change, the emit word: blob emitsb_sbc43, armed at
`form=sbc43`, sideband 0xc43 (bit 10 with 0x843's bits, the firmware's #11 value). Two attempts
on the same freeze, the second at the user's choice.

**Frozen verdict (as printed).** By hand on each kept directory (fold/reproduce-own-*.out; the
gate's stop ended the stage, rc 16), the same lines both times:

```
SUMMARY: own: controls: every control passed
Q128-B11 RULE: B11-DONE: all ran (sideband 0xc43 reads RUN; H-DM predicts RUN; H-ALL: no prediction)
X0 qualifier: 0x5a5a3303 (the issuer went on past the emit)
```

**Results [HW].**

- Both attempts: controls PG, E0, T0 and B passed; X0 0x5a5a3303, S1 0x5a5a3304, M4 0x5a5a3302
  and run id 1, state 2, T 0x005a3305; 8 ticks; BIF_FAULT 0.
- Both attempts: the kit's owntask gate after the ok end failed: fill `diff: 2048 of 2048 pixels,
  first (0, 0) 0xdeadbeef expected 0xff336699`, triangle `diff: 0 of 4096`; rc 16, the kit's
  recovery, after which fill and triangle were ok (c1-a.health2, c1-a.fill2,
  closing29/r40-n3e-logs/health-after-b11.log). Every other DONE row's gate passed (E1162-E1164,
  E1166, E1168). Post not run.
- SURVEY, both attempts: the started entry's sa differed from the issuer's: sa1 0x04400000 (pre
  0x32005000), sa3 0x3f800000, sa4 0x3f400000, sa5 0xbec00000, sa7 0x3f800000, sa8 0xbec00000,
  sa9 0x3f400000, sa11 0x3f800000, sa22 0x32002000 (pre 0x32000000), and sa12-sa27 the same words
  as pa0-pa15 of the same entry, sa28-sa31 going on in that pattern; sa0 and sa2 unchanged.
- pa0-pa15: attempt 1 as B1's (V0 in pa0, pa4, pa8 and pa12, V2 in pa2, pa6, pa10 and pa14);
  attempt 2 the same but pa0 0x00000003 and pa2 0x32411000.

**What it shows.** Bit 10 does not stop the start: 0xc43 runs the program and its entry to done
(2 of 2) **[HW]**. After it, the next fill failed in 2 of 2 and a reset cured it; that bit 10
leaves state that breaks the next fill until a reset is **[infer]**. The entry it started read
other secondaries than the issuer's, with sa12 onwards holding its own pa0 onwards **[HW]**.

**What it does not show.** What the state is; whether the EDM's own secondaries changed (the
post `sa` are read by the started entry); why attempt 2's pa0 and pa2 differ; what bit 10 means.

**Correction 2026-11-20:** Round 41 (closing29/n3f/design.md) read what this record inferred. In rows X
(E1174, 0xc43) and Y (E1175, 0x403) our entry 0 read the EDM's own secondaries after the emit, in
a second job: they equal the post words above in all 32, so the "other secondaries" the started
entry read are the issuer's own bank, rewritten by bit 10: sa12-sa27 take the started entry's
pa0-pa15, sa1 and words of sa3-sa10 change, sa0 and sa2 stay (crumb3) [HW]. sa13 then holds pa1,
0x00043000, and the next fill (X, Y) and the next triangle (T, E1177) fault through the EDM's list
at page 0x00043000 until a reset [HW]; with sideband 0x843 the bank stays as it was and both run
(C, E1173). This record's two fills failed the same way: its kept kernel logs read `BIF fault
0xd0400 at 0x4300f (PD 0x0)` in both attempts, and the triangle after it ran on the stock
firmware after the watchdog's recovery reset, so "the triangle exact" says nothing of bit 10's
state. The readings above stand; the inferred "bit 10 leaves state that breaks the next fill until
a reset" is now read: the state is the rewritten sa12-sa27, and the fault page is the one sa13
holds. Why the fault follows sa13 is still inferred. The claim is not contradicted and is left as
it was.
