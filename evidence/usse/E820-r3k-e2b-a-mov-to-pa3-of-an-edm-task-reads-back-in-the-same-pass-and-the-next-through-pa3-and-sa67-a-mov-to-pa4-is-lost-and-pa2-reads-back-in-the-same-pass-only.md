+++
id = "E820"
claim = "R3k stage e2b (K1, 15 jobs of pa_write2.s, Q098, no stop; the first run of the verifier's mov to pa2, pa3 and pa4): the controls held (R x3: pa0 to pa4 read E748's words and the next pass the same; S: a marker written to sa67 read back through pa3 in the same pass and the next; Z67 and Z68 put E748's words back); a marker written by mov to pa3 was read in the same pass through pa3 and sa67 and in the next pass (M, M and M, M) in 3 of 3 jobs, H-D alias; a marker written by mov to pa4 was read through neither pa4 nor sa68 in the same pass or the next (old, old and old, old) in 3 of 3, H-B lost; a marker written by mov to pa2 was read through pa2 and sa66 in the same pass (M, M, 3 of 3, H-D) and neither in the next pass (old, old, 3 of 3, not frozen); the neighbours were unchanged in every job; frozen verdict 'write direction: consistent with none, refuted [H-D alias, H-B lost, H-P private]'"
unit = "usse"
method = "R3k session K1 (stage e2b; decision R3-K3, Q098), dataset edm-closing-r3k-events, 2026-11-10, kernel 7.3.0-resgx545, the new module of round 3 (fork resgx545 8fc748b0, srcversion 230E0EF50FFFD606C53AE3C, installed = loaded, checked at each preflight; gma500_gfx.ko sha256 06bf58db6e1c78f2bd9858bcc7b9e63d752786e098e50b5c67345ce69f2ceb78 as recorded in env.json), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, the laptop (host cedar) on the home LAN, not the direct cable, rebooted into the new module at 18:48 (boot-test-kernel.sh then test-session.sh, health ok); the final run of session K1 in one driver call from 19:29:52 Mac time (out/r3-kev.log: f 19:29:52, t 19:30:07, kb 19:30:19, e2b 19:30:56, e3h 19:31:10, e3a 19:31:23, e3b 19:31:39), each stage gated on the previous stage's kept stage.json; the task pa_write2 (sha256 0374a24ebcf03a16..., 201 instructions, our own source: S2's pa_write with three commands more, accepted by the landed verifier at 7aaa017 with its mov-to-pa row, pa2 to pa4 only, never pa0 or pa1) armed in slot 0 once at the stage start; per job the task reads pa0 to pa4 and sa64 to sa68 in one pass, writes the marker M by the command's instruction (cmd 1 none, cmd 2 mov sa67, cmd 4 mov pa3, cmd 5 mov pa4, cmd 6 mov pa2, cmd 3 mov sa68), reads again in the same pass and logs the next pass's words; the markers 0x5a670001 (s), 0x5a430004 (c4), 0x5a440005 (c5), 0x5a420006 (c6) and, for the restoring rows, E748's own words 0x04000004 (z67) and 0x00030001 (z68); R x3, S, C4 x3, C5 x3, C6 x3 (last of the three, sa66 being rewritten by PDS #13 each event), Z67, Z68; stop budget 0 (a tick stop would end the stage), none; exit 0, 15 jobs, health ok; scored by the frozen score/score_r3.py e2b (out/score-e2b.txt). Freeze history of the session (FROZEN.sha256 over every generator, scorer, runner, table, blob and prediction; PREDICTIONS.sha256 1f32e767... throughout): 1527b62e... (FROZEN.pre-logfix.sha256) until K0's second attempt, 463c251b... (FROZEN.pre-armlog.sha256; K0's four stages and K1's first attempt ran under it) until K1's first attempt, 1d6a3ad2... (FROZEN.sha256; K1 ran under it); each refreeze was made after a failed attempt and before the next one, with the mock test first, and changed no prediction file"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r3k-events:out/e2b/"]
terms = ["Event Data Master (EDM)", "Universal Scalable Shader Engine (USSE)"]
+++
**What ran.** E748 showed that in an EDM task pa_n names sa_(64+n) for reads (pa0 to pa4 equal
sa64 to sa68) and that a write to sa67 or sa68 is read back through pa3 or pa4. The direction pa
to sa was unmeasured because the verifier refused a `mov` to pa. The new verifier row allows it
for pa2 to pa4. Three hypotheses for what a `mov` to pa_n does in an EDM task: H-D it aliases (the
sa reads M too and the next pass keeps it), H-B it is lost (as in a fill, Q098: neither reads M),
H-P a private register (pa_n reads M, sa_(64+n) the old value).

**Frozen verdict (as printed).** `SUMMARY: e2b: R/S/Z controls held; write direction: consistent
with none, refuted ['H-D alias', 'H-B lost', 'H-P private']; stops 0 []; Q098 rows: fit: 6 held, 0
FAILED, 0 cannot tell/void; held out: 18 held, 15 FAILED, 0 cannot tell/void; refuted ['H-B lost',
'H-D alias', 'H-P private']; replicate: 36 held, 30 FAILED, 0 cannot tell/void; refuted ['H-B
lost', 'H-D alias', 'H-P private']; control: 9 held, 0 FAILED, 0 cannot tell/void`. The scorer
tests each hypothesis against all three registers together, so "refuted" for all three means no
single hypothesis fits the three registers; per register one of them does.

**Results [HW], the three jobs of each held-out row agreeing.**

| row | instruction | marker | same pass: pa_n, sa_(64+n) | next pass: pa_n, sa_(64+n) | neighbours | fits |
|---|---|---|---|---|---|---|
| c4 x3 | mov pa3, M | 0x5a430004 | M, M | M, M | pa4, sa68 unchanged | H-D |
| c5 x3 | mov pa4, M | 0x5a440005 | old, old (0x30001) | old, old | pa3, sa67 unchanged | H-B |
| c6 x3 | mov pa2, M | 0x5a420006 | M, M | old, old (not frozen) | pa3, pa4, sa67, sa68 unchanged | H-D (same pass) |

The controls: R x3 read E748's words (pa2 0x01061a70, pa3 0x04000004, pa4 0x00030001, sa0
0x32004000) and the same next pass; S (`mov sa67, 0x5a670001`) read M through pa3 and sa67 in the
same pass and the next; Z67 and Z68 wrote E748's words back and read them.

**What it shows and does not.** In an EDM task of ours a `mov` to pa3 is the same register as sa67
(read back in the same pass and the next, 3 of 3), a `mov` to pa2 is the same register as sa66 in
the pass and the next pass finds the old value (3 of 3; sa66 is rewritten by PDS #13 for each
event [infer], not tested), and a `mov` to pa4 is lost, in both passes (3 of 3), neither pa4 nor
sa68 changing. So the direction pa to sa is not one rule for pa2 to pa4: pa3 and pa2 alias, pa4
does not [infer: pa4's write is lost as a fill's pa writes are, E380; why pa3 and pa4 differ is
not shown, nor whether an encoding difference of the destination number is the reason]. Not shown:
pa5 and above, pa0 and pa1 (refused by the verifier), an event that is not a tick, a fill (the
question's own case).
