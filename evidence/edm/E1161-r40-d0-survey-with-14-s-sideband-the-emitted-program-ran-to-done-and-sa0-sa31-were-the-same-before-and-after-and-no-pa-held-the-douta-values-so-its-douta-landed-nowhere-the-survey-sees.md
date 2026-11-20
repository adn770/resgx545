+++
id = "E1161"
claim = "r40-d0-survey stage own (row D0, a landing survey, module 0CDFCDB7, fork f9453424bf71, emitsb14d, image crumb3 at fw14, form=fw14, s2 0, flagged, user present): E1160's job with a survey: our EDM task emitted the word with #14's sideband 0x843 on the first tick pass that saw the command; T read 0x005a3305, S1 0x5a5a3304, M4 0x5a5a3302 and run id 1, state 2, done: every control passed (PG, E0, T0, B, P0, P1), 'Q128-D0 RULE: D0-HID' held as predicted; sa0-sa31 read identical before the emit and in the started task after the program ran (sa0-sa2 0x32004000 0x32005000 0x32002000, sa3-sa21 and sa24-sa31 zero, sa22 0x32000000, sa23 0x05f17000), and pa0-pa15 of the started task held no V0 or V2; so the program's douta wrote nothing to any sa this survey could tell apart from the values already there and nothing to pa0-pa15 (inferred: it landed outside what D0 reads, or onto sa0 and sa2, which already held its values); post's triangle and fill exact"
unit = "edm"
method = "r40-d0-survey (render/closing-r40-d0-survey), stage own and post of the question-closing pass (round 40: row D0, closing29/n3e/design.md sections 1.2 and 3.1, E1160's job with a landing survey; flagged class, the user present with a reset ready), dataset render-closing-r40-d0-survey; attempt out/20261119-191743 (19:17:43, rc 0; stages own and post); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 0CDFCDB73D76F39FE9E593C installed and loaded alike, linux fork r39-kernel f9453424bf71 built on cachix (closing29/kernel39c/deliver/f9453424bf71/manifest), the boot of r39-n3d-z (E1156), no rebuild and no boot for the session; stock firmware), the kit's owntask job kind (kit/ = resgx545 555d8eb, its fwtask_run.py byte for byte): our task owntask/emitsb14d.blob (asm/fwtask/emitsb14d.s, sha256 52c6c8a23db4540d338799ac2b73438f5a0b92dbc68a2b51e8fb0119990867d1, asm/fwtask/fwtask.map at 555d8eb, branch r40-d0; emitsb14 plus stores only: sa0-sa31 into page dwords 128-159 before the emit, sa0-sa31 and pa0-pa15 into 160-191 and 192-207 in the started entry; the kernel's verifier accepted it unchanged, own_code 1988 bytes, the fork's KUnit suite on the Mac shim 34 of 34: closing29/r40-s-logs/d0-shim-emitsb14d.log) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=fw14` after the stage's reset and health pair (the kernel's arm line: pds2=0, emit image 0x30011100), then one row c1-a of tester command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command), the results page, the registers (snap0, snap9) and the gate kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 afba7bc6474423f103f2d6c97d65676956ae1115ed702648bb1b676729739b61 (48 files), PREDICTIONS.sha256 30bf9f1b1408727dfc621da87c3087e1c0d4283a5368c860caf91d87621795c4 (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsb14d.s and fwtask.map at 555d8eb; r35-sa's and r36-n3's kept snapshots at data 9fce0b99; t30's source 42c4de7); the frozen predictions predictions/own.tsv (D0-HID predicted), the rule score/score.py, run by the driver (score-own.txt, score-post.txt) and again by hand (fold/reproduce-own.out, reproduce-post.out, the same lines); the SURVEY lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband 0x843 is a fact of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW", "infer"]
date = "2026-11-19"
data = ["render-closing-r40-d0-survey:out/20261119-191743/own/", "render-closing-r40-d0-survey:out/20261119-191743/post/", "render-closing-r40-d0-survey:fold/"]
terms = []
+++
**What ran.** E1160's job (sideband 0x843, `s2` 0, tick pass, crumb3 in #14's page) with the blob
emitsb14d: emitsb14 plus stores only, so that the host could read the secondary attributes sa0-sa31
as the issuing task saw them before the emit, and sa0-sa31 and pa0-pa15 as the started entry saw
them after crumb3's `douta` writes (V0 and V2, the values the program sends, E1156). The arm logged
`own_code: 1988 bytes accepted` and `own task armed: ... pds=crumb3 pdsat=fw14 pds2=0 form=fw14`.

**Frozen verdict (as printed).** By the driver and again by hand:

```
SUMMARY: own: controls: every control passed
Q128-D0 RULE: D0-HID: all ran; landing HID: post sa4-sa31 = pre and no V0 or V2 in pa0-pa15: the douta landed nowhere D0 can see (sa0/sa2 own values) [predicted: held]
X0 qualifier: 0x5a5a3303 (the issuer went on past the emit)
SURVEY (printed, not scored): land HID; pre/post sa differ at none
SUMMARY: post: the stock firmware drew the triangle and the fill exactly after the disarm
```

**Results [HW].**

- Controls PG, E0, T0, B, P0 and P1 all passed.
- c1-a: X0 0x5a5a3303, S1 0x5a5a3304, M4 0x5a5a3302 and run id 1, state 2, T 0x005a3305; 8
  ticks from the command write (37.9 ms); alive false by design (the program's first `tim` write
  is a stopped 0).
- sa0-sa31 identical before the emit and after the program ran: sa0-sa2 0x32004000 0x32005000
  0x32002000, sa3-sa21 and sa24-sa31 zero and unchanged, sa22 0x32000000, sa23 0x05f17000.
- pa0-pa15 of the started task held no V0 or V2 (pa0 and pa2 are not them: the same reading as
  E1156's).
- Post: the triangle and the fill exact.

**What it shows [infer].** The program ran (E1160's state again) and none of the places the survey
reads took its `douta` values apart from what was there: no sa changed, so a write to sa3-sa31
did not happen or wrote what was already there (zero or the same words), and no pa of the first 16
holds V0 or V2. The only secondaries that hold V0 and V2 are sa0 and sa2, which held those words
before the emit, so a landing there is not told apart from no landing. So the `douta` landed
nowhere D0 can see; which of those it is, is inferred from the readings, not read.

**What it does not show.** Where the `douta` land (the destination bank, whether sa0 and sa2 took
them, or whether the write was dropped); the sideband's bits; whether another nonzero value runs;
what stops the tick with sideband 0; one job only.

**Correction 2026-11-20:** Row L (E1163, r40-n3e-l) wrote two markers with `douta` to attributes
24 and 26 from the same job and read them in the started entry's pa12 and pa14, with sa24 and
sa26 unchanged: an emitted program's `douta` lands in the primary attributes of the task its
`doutu` starts, not in the issuer's secondaries. This record's design assumed the secondaries
(closing29/n3e/design.md section 1.2): its scorer compared pa0 with V0 and pa2 with V2 and
searched pa0-pa15 for them, as the landing of crumb3's two `douta`, which name attributes 0 and 2
(asm/fwtask/pds/crumb3.s, controls 0 and 0x200). The readings above stand. The reading of them
changes: the alternative "onto sa0 and sa2" is not supported (L's markers left the sa alone), and
the pa that attributes 0 and 2 map to was not known when D0 was frozen. pa = n - 12, which fits
L's two points, puts them below pa0, outside what D0 reads, which fits these readings [infer];
pa = n/2 would put V0 in pa0 and V2 in pa1, and D0 read 0x00000000 and 0x00043000 there. So the
`douta` landed outside pa0-pa15 [infer]; where, is open. The claim is not contradicted (it gave
"outside what D0 reads" as one of its two inferred readings) and is left as it was.
