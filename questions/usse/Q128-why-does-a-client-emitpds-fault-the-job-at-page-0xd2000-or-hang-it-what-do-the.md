+++
id = "Q128"
question = "why does a client emitpds fault the job at page 0xd2000 or hang it, what do the s0, s1 and s2 operands of the started PDS program become (it saw ir0.0 2 or 3 whatever s2 was), and what in the control word's addend the PDS uses (0xFFF to 0x2000 left the fill's own value, 0x100 did not): why does the addend, from 0xFFF to 0x2000, leave the fill's own dword 0x403 where 0x100 gives 3 or 2, and what does 0x800 do"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E488", "E513", "E520", "E1148", "E1149", "E1150", "E1151", "E1152", "E1153", "E1154", "E1155", "E1156", "E1157", "E1158", "E1159", "E1160", "E1161", "E1162", "E1163", "E1164", "E1165", "E1166", "E1167", "E1168", "E1169", "E1170", "E1171", "E1172", "E1173", "E1174", "E1175", "E1176", "E1177", "E1178", "E1179", "E1180", "E1181", "E1182", "E1183", "E1184", "E1185", "E1186", "E1187", "E1188", "E1189", "E1190", "E1191", "E1192", "E1193", "E1194", "E1195", "E1196", "E1197", "E1198", "E1199", "E1200", "E1201", "E1202", "E1203", "E1204", "E1205", "E1206", "E1207", "E1208", "E1209", "E1210", "E1211", "E1212", "E1213", "E1214", "E1215", "E1216", "E1217", "E1218", "E1219", "E1220", "E1221", "E1222", "E1223", "E1224", "E1225", "E1226", "E1227", "E1228", "E1229", "E1230", "E1231", "E1232", "E1233", "E1234", "E1235", "E1236", "E1237", "E1238", "E1239", "E1240", "E1241", "E1242", "E1243", "E1244", "E1245", "E1246", "E1247", "E1248", "E1249", "E1250", "E1251", "E1252", "E1253", "E1254", "E1255", "E1256", "E1257", "E1258", "E1259"]
terms = []
+++

E488: in 24 of 24 client fills that executed an emitpds (a copy's shader, one instance emitting),
the PDS program the emit named ran (18 of 19 ir0.0 probes) and the job then faulted with `BIF fault
0xd2000` (22 times), 0x92000 once (sideband 0x1) or hung (two emits in a row). The started
program's ir0.0 was 3 (16 probes) or 2 (2), ir0.1 2, ir1.0 and ir1.1 0, and none of s2 = 0, 1,
0xFFFFFFFF, 0xE17D0001 appeared in ir0 or ir1; E146's reading of s2 as ir0 is not supported.

Narrowed in 11.27: the emit was executed by a quad of four lanes, not one instance (E513: a test of
`pa0` selects a whole 2 x 2 quad). The addend matters (E520, 39 probes, all faulted (37) or hung
(2)): 0xFFF, 0x1000, 0x1001, 0x1010, 0x1100 and 0x2000 left the fill's own 0x403 in 12 of 12 probes,
in two orders, where 0x100 read 3 or 2 (11 of 11), 0x800 read 0x401 and 0x400, and 0x10 read 3 once
and 0x400 once; Q145 asks why.

What is open: where the fault's page (0xd2000) comes from (the emitted program's data fetch, its
doutu, or a PDS state a client task lacks), what ir0 of a started program is (a task counter?), what
s2 becomes (none of ir0.0, ir0.1, ir1.0, ir1.1 of the program), and what the control word's low bits
are for beyond the window of E520 (0x100 started the program; the PDS uses the addend). To settle
it: an emitted program that stores more than one input word (not 2 to 4 dwords: E144; 5 or more, or
one store per word) and the other PDS registers, with s0 varied bit by bit and a program placed
where page 0xd2000 is mapped; for the EDM's own use of the operands, phase 12's firmware.

Noted 2026-11-09: near duplicate of Q145, not merged (Q128's question includes what the control
word's addend of an emitpds does (E520), which is Q145's). A merge or a fold decides which text
survives.

**Correction 2026-11-11:** Q145 is merged into this question (retired as folded into Q128; a fold is
not an answer), and its question is now a clause of the one above. Its question was: why does the
control word's addend of an emitpds, from 0xFFF to 0x2000, leave the fill's own dword 0x403 where
0x100 gives 3 or 2, and what 0x800 does.

Its text: E520: 3 or 2 at 0 to 0x400 and at 0x4000 and above (24 of 27 probes outside the window),
0x403 at 0xFFF, 0x1000, 0x1001, 0x1010, 0x1100 and 0x2000 (12 of 12), 0x401 and 0x400 at 0x800 (2
probes) and 0x400 at 0x10 in one of its two probes, the 10 base probes interleaved among them
reading 3 or 2; every job faulted or hung. What is open: what the addend is (an offset the PDS adds
to an address, [infer]), the values between those run, what the 0x400 bit of the stored dword marks
(it was also read at the addend 0x10 once), and whether the 0x800 and 0x10 readings repeat. To
settle it: the addends 0x7FF to 0x801, 0x1FFF to 0x2001, 0x3FFF; a PDS program that stores more than
one input word. Q145's evidence (E520) and terms (none) were already in this question. Both files
noted on 2026-11-09 that a merge decides which text survives; this is that merge.

Narrowed 2026-11-18 (E1148, r36-n3, flagged): the firmware's own emitpds form (`.tasks.taske`, the
kernel's control word 0x01000100, its image's address >> 4 and 0), run from an EDM task of ours with
the kernel's PDS image (douta to attributes 0 and 2 with the values sa0 and sa2 hold, doutu our
entry 1), left no write of the started entry 1 within 200 ms in its one job, and the EDM's tick
stopped within that window with no BIF fault (post hoc); the kit's reset restored exact draws. So
from an EDM task the form neither faulted the bus as a client's did (E488) nor started our task
visibly. Not shown: whether the emitted program ran at all, or ran and its doutu did not start our
task (the design's [infer] U1 = U2 = 0, TRC 8 and code index in U0), or started it and entry 1
stopped before its first store; what stopped the tick; where an emitted douta lands (pa or sa) stays
open.

Narrowed 2026-11-19 (E1149, E1150, r37-n3b-a and r37-n3b-b, flagged, N3b of
closing29/n3b/design.md): the same form from our task emitsb (E1148's emitsa with a store right
after the emitpds and one as entry 1's first work), one job with each image. Measured [HW]: the
issuing task went on past the emitpds in both (X0 written), the started entry 1 never made its first
store in both, and the EDM's tick stopped within 10 ticks of the command write in both, with no BIF
fault; the reset recovered. With the crumb image (E1150), whose first instruction writes a stopped 0
to `tim`, CR_EVENT_TIMER (0x0acc) still counted after the stop. Inferred from that [infer]: the
emitpds issued by our task stops the EDM's tick with the emitted PDS program never executing its
first instruction, so E1148's causes (2), the program ran and its doutu did not start our task, and
(3), entry 1 started and stopped before its first store, are excluded. The inference is that a `movs
tim` from an emitted program writes the 0x0acc the host reads: `movs tim` was measured only from a
client fill's PDS program, read back through the PDS (doc/isa/content/pds/probe/inputs.md), and the
host's 0x0acc only as the firmware's running timer (E1131, E1133); if it is false, E1150 cannot tell
whether the program ran, (1) from (2), and only E1149's readings stand. Open: why the emitted
program does not start from an EDM task (the PDS, an emit queue the stopped EDM no longer serves, or
the form), what stops the tick, and where an emitted douta lands (pa or sa), never reached.

Narrowed 2026-11-19 (E1151, E1152, r38-n3c-s1, flagged, session S1 of closing29/n3c/design.md):
two rows, one job each. R1 (E1151): our task emitsn, emitsb with the emitpds taken out, ran the
same command to done (X0, M4 and state 2 written, 40 ticks in 38.1 ms, the tick going after it),
so the stop of E1148-E1150 needs the emit [HW]. R2 (E1152): a client fill's PDS `movs tim` of
0x00abcde0 showed in the host's 0x0acc at once and held there to the reset [HW], so E1150's
instrument holds for a client program: the 0x0acc the host reads is the register a PDS `tim`
write loads. E1150's reading that the emitted program never executed its first instruction now
rests only on an emitted program's `tim` write landing as a client's does [infer]. Open: what in
the emit (the program, its page or flags, the control word's rows, the operands or the issuing
pass) stops the tick, why the emitted program does not start from an EDM task, and where an
emitted douta lands (pa or sa), never reached.

Narrowed 2026-11-19 (E1153, E1154, r38-n3c-s4 and r38-n3c-s3, flagged, sessions S4 and S3 of
closing29/n3c/design.md, one boot of module 88ADCEB5): E1149's job with the image changed at the
arm, one job each. R5 (E1153): the halt image, v1's two data rows and a lone `halt`, in the
kernel's own page, stopped the tick within 9 ticks as v1 and crumb did, the issuer going on past
the emit [HW]: the stop needs the emit (E1151) but no instruction of the program. R4 (E1154):
crumb's program with 3 data rows and #14's control word 0x01800100, placed at 0x30011100 in the
firmware's own PDS #14 page with that page's flags, never showed its first `tim` marker and
stopped the tick within 9 ticks [HW; that it never started is inferred as in E1150]: our page,
its flags, the rows and the control word are not the cause. R6 and R7 (sessions s5 and s6) were
not run: the design runs them only after a start (M-T1 to M-DONE). Remaining candidates for why
an emitted program does not start from an EDM task and the tick stops: our `emitpds`'s `s2`
operand or its encoding form, or emitting from our task's timer pass where the firmware emits
from its kick pass. The next step is a user decision (closing29/n3c/design.md, after M-NEVER),
after a facts-only fwsim read of what the stock kick pass does after its #14 emit. Where an
emitted douta lands (pa or sa) stays open, never reached.

Narrowed 2026-11-19 (E1155, E1156, r39-n3d-k and r39-n3d-z, flagged, sessions S1 and S3 of
closing29/n3d/design.md): E1154's job with crumb3 in #14's page, each emit issued on the pass of
a host GETMISCINFO kick. K (E1155: our word, sideband 0, `s2` 0, module 88ADCEB5) scored CANNOT
TELL: the readings were K-NEVER's (T running, entry 1 never stored, the tick stopped) but Δtick
from the kick was 7, outside the frozen band 8-11; read informally [infer], the kick pass alone
did not start the program. Z was then refrozen before it ran, at the user's choice, without the
band. Z (E1156: our word with the firmware's 14-bit sideband 0x843 and `s2` 0x00020000, the
request bit #14 emits with, module 0CDFCDB7) ran: crumb3 reached its last `tim` marker at
0x0acc, its `doutu` started our entry 1 and entry 1 ran to done [HW], the first program emitted
from our task that ran; an emitted program's `tim` lands at 0x0acc as a client's does. So an
emitted program does start from an EDM task when the emit carries #14's sideband and `s2` and
comes from a kick pass. Open: which of the sideband, `s2` and the kick pass decides, alone or
together (row S of the design and the rows that split the sideband from `s2`), and so what
stopped the tick after our other emits; where an emitted `douta` lands (Z: not `pa0` or `pa2`;
`sa0`-`sa3` read the values they hold anyway, so not told); and the client-side parts above.

Settled in part 2026-11-19, the own-task stop (E1157 to E1160, r40-s-sb, -s2, -pass and -sbt,
flagged, module 0CDFCDB7, each changing one thing against Z or S-PASS; this corrects the
narrowing above, which left the sideband, `s2` and the pass open): the cause of the stop after an
emitpds from our EDM task is our emit word's 14-bit sideband being 0. Of six emits of crumb3 in
#14's page, the four with #14's sideband 0x843 ran the program and the entry it started to done,
from a kick pass or a tick pass, with `s2` 0 or the request bit 0x00020000 (E1156, E1157 kick;
E1159, E1160 tick) [HW]; the two with sideband 0 never started it and the tick stopped (E1154
tick and `s2` 0; E1158 kick and `s2` 0x00020000) [HW, infer as E1150], E1155 reading the same
(CANNOT TELL by its band). `s2` and the pass are not needed. Still open here: what the
sideband's bits mean (the firmware's #11 emit carries 0x0c43, #12's and #14's 0x0843; facts of
the data-private read) and whether another nonzero value runs; what stops the tick with sideband
0; where an emitted `douta` lands (every run row: not pa0 or pa2; sa0-sa3 held those values
anyway; a row is sketched in closing29/r40-s-logs/d-row-note.md, not built); and the client-side
parts above (the fault at page 0xd2000, `s0`-`s2` as seen by the program, the addend). Not
retired.

Landing line, 2026-11-19 (E1161, r40-d0-survey, flagged, module 0CDFCDB7; this updates the
"where an emitted `douta` lands" item of the section above): the survey row (emitsb14d, #14's
sideband, `s2` 0, tick pass) ran the program to done again and read sa0-sa31 before the emit and
after, and pa0-pa15 of the started entry: sa0-sa31 identical, sa3-sa21 and sa24-sa31 zero,
sa22 0x32000000, sa23 0x05f17000, and no V0 or V2 in pa0-pa15, as predicted (D0-HID) [HW]. So
the `douta` landed nowhere D0 can see [infer]: sa0 and sa2 are the only secondaries holding
V0 and V2 and held them before, so a landing there is not told apart from none, and no other sa
and no pa0-pa15 took them. Still open: the destination bank (sa0 and sa2, another bank, or a
dropped write), the sideband's bits, what stops the tick with sideband 0, and the client-side
parts above. Not retired.

Sideband bits and landing, 2026-11-20 (E1162 to E1172, r40-n3e-b0, -l, -b1, -b2, -b3, -b4, -b8,
-b9, -b10, -b7 and -b11, flagged, module 83FBFD86 of fork r40-kernel 423b436e7f80, one boot; each
row changes one thing against B0, which reproduced D0 on the new build): from our EDM task, bits
1:0 of the emit's sideband decide the start [HW]. 0 never starts the program and the tick stops
(0x000 E1158, 0x840 E1167, 0x040 E1169, 0x800 E1170); 1 faults the job, BIF_FAULT 0x30011010, the
base of #14's page + 0x10, 0xf0 below our image at 0x30011100, our task not storing past the emit
(0x841 E1165, 0x001 E1171); 2 or 3 run the program and our entry to done (0x002 E1168, 0x842
E1166, 0x003 E1164, 0x843 E1162, 0xc43 E1172). Bits 6, 10 and 11 are not needed; bits 6 and 11
neither with 2 nor with 3. H-DM (bits 1:0 the data master, 3 the event one, needed) is falsified
by 0x842 and 0x002. The combinations not run (0x042, 0x043, 0x802, 0x803, bits 12-13) follow
from the rule only [infer]. B5 (0x043) and B6 (0x803) were built and not run: the design ran them
only if B1 (0x003) never started, and B1 ran. Bit 10 (0xc43, #11's value) ran 2 of 2, and both
times the kit's gate fill after the ok end failed (every pixel 0xdeadbeef) with the triangle
exact, cured by the reset; that bit 10 leaves state that breaks the next fill until a reset is
inferred; the entry it started read other secondaries than the issuer's (sa1 0x04400000, sa12-sa27
the words of its pa0-pa15).

The landing (row L, E1163): an image whose two `douta` sent markers to attributes 24 and 26 put
them in the started entry's pa12 and pa14 and left sa24 and sa26 at 0 [HW]: an emitted `douta`
reaches the primary attributes of the task the `doutu` starts, not the issuer's secondaries.
Any mapping for other attributes is inferred from those two points (pa = n - 12 fits them and
puts crumb3's attributes 0 and 2 below pa0, which fits D0's and B0's empty pa0-pa15; E1161 gets a
correction). With 0x002, 0x003, 0x842 and 0xc43, crumb3's V0 and V2 stood in every fourth pa from
pa0 and pa2 (E1164, E1166, E1168, E1172) where 0x843 put them nowhere in pa0-pa15 [HW]. Still
open: why the landing depends on the sideband and where attributes 0 to 11 go with 0x843; what
bits 6, 10 and 11 do; what bit 10 leaves behind; what stops the tick with bits 1:0 = 0 and what
the fault at #14's page + 0x10 is; the client-side parts above. Not retired.

Bit 10's after-effect, 2026-11-20 (E1173 to E1177, r41-n3f-h1 to -h4, flagged, module 83FBFD86
of fork r40-kernel 423b436e7f80, no rebuild or boot): our entry 0 read the EDM's own sa0-sa31 in a
second job after the emit (command 6, the after-read). With 0x843 they are as before and the next
fill and triangle run (C, E1173). With bit 10, 0xc43 (X, E1174) or 0x403 without bits 6 and 11
(Y, E1175), they equal what the started entry read: sa12-sa27 take the started entry's
pa0-pa15, sa1 and words of sa3-sa10 change (sa1 0x04000010 in X, 0x04400000 in Y and B11), sa0
and sa2 stay [HW]. So bit 10 rewrites the issuer's own secondaries, and the rewrite stays: the
kick and command 6 after it were served. sa13 then holds pa1, 0x00043000, and the EDM's list
faults at that page: the fill (X, Y, and B11's two in E1172) and, run first, the triangle (T,
E1177), with BIF_FAULT 0x0004300f (list 15), until a reset [HW]; in X and Y the fault was already
latched by the end of the row (after job 2's kick), in T and B11 (one job) it came with the gate's
first job. The design's T-HEAD (the render queue's head sa15, page 0x01555000) failed: render and
transfer fault at the same page. That the hardware or the firmware takes sa13 as a page base (the
transfer queue head of the firmware's roles) is inferred. LC (E1176: land, the timer running)
ended CANNOT TELL: its control E0 read the cmd word at the row's end, 6 for the unserved job 2, a
design slip of the scorer; its printed readings fit the predicted early stop (sa0 0, sa2
0x0104b95b, BIF_FAULT 0x0000000f, the tick stopped). Still open: where sa1 and sa3-sa10 come from;
whether the rewrite heals without a reset; whether the timer matters; what bits 6, 10 and 11 mean;
the parts above. Not retired.

Row LC rerun, 2026-11-21 (E1178, r41-n3f-lc2, flagged, the same module, no rebuild or boot): H3's
row with control E0 read in job 1's record read 'Q128-N3F-LC RULE: LC-EARLY', as predicted. With
land (no V0 or V2, the timer running) and 0xc43 the EDM stopped after job 1, BIF_FAULT 0x0000000f
(list 15, page 0), the tick stopped and job 2 was never served [HW], so whether bit 10's rewrite
heals on later stock passes is not readable with land, and LC-FILL, LC-FILLOK and LC-HEAL could not
tell. The printed post words repeat H3's pattern (sa12-sa27 = the started entry's pa0-pa15, sa13 =
pa1 = 0x00043000, sa0 0, sa1 0x04400000, sa2 0x01030b00, not H3's 0x0104b95b); that the copy came
before the stop and that sa13's word is this run's pa1 are inferred, since the started entry's pa
can hold words of earlier rows (E1177). Still open: as above, and which pointer faults at page 0
with land. Not retired.

Attribute 13, sb402 and landv, 2026-11-22 (E1179 to E1183, r42-n3g-g1 to -g3, flagged, module
079DD0D1 of fork r42-kernel ec6511d5de87, built and booted once for the round). The build
reproduced row C (E1179), and the started entry's odd pa read the words of the nine earlier rows
through the boot, pa1 0x00043000 included [HW, printed]. Row M (E1180) sent markers to attributes 13
and 1 with 0xc43: pa1, sa13 and the next fill's fault page took M13 0x005d3000, sa1 took M1 [HW];
row S (E1181) read M13 still in pa1 after three resets, with 0x843 doing nothing to the EDM's sa
[HW]. So the fault page is the word in attribute 13, and 0x00043000 was a stale word there that
none of our rows wrote [HW]; who wrote it is not read. Row Q (E1182): 0x402, bit 10 with bits 1:0 =
2, behaves as 0xc43 and 0x403 (the rewrite of sa12-sa27 from pa0-pa15, the fault at the page in
sa13), and puts crumb3's V0 and V2 in every fourth pa as 0x002 [HW]. Per-job BIF words (K5) put the
fault in M and Q in job 2, the kick and command 6, not after job 1 [HW]; the gate's fill then met a
fault already latched, so its reading alone does not show a fresh fault. H-BLOCK (bit 10 makes the
issuer's sa n read attribute n of one block) is not settled: M's sa1 = M1 fits it, but Q's sa1 read
0x04400000 with no write to attribute 1, so either attribute 1 was rewritten between the rows or
sa1 is not attribute 1 in every case [infer]. Row LV (E1183), land with V0 and V2, stopped early
like LC (E1178) with sa0 = V0 and sa2 = V2, at page 0x04400000, the post sa1, on a stock pass
before job 2 [HW]: V0 and V2 do not prevent the early stop; that it follows a pointer through the
first secondaries is [infer]. Whether the rewrite heals without a reset stays unreadable from our
task (with the tick running the EDM stops first). Still open: where sa1 and sa3-sa10 come from and
whether sa1 is attribute 1; who wrote 0x00043000; which access of job 2 faults; what bits 6, 10 and
11 mean; the parts above. Not retired.

Attribute 1, the tick pass and the kick pass, 2026-11-23 (E1184 to E1187, r43-n3h-n1 and -n2,
flagged, module 079DD0D1 of fork r42-kernel ec6511d5de87, no rebuild or boot; the kit's K6 kick-only
job and K7 per-stage draws). Rows W and W2 (E1184, E1186) sent M1 to attribute 1 with 0xc43 and read
it in `sa1` in the same row, one job and no pass after the emit, with no fault [HW]. Row V (E1185),
landv after W with no client draw between (resets, the register health, the arm's boot, kicks and
ticks only), read `sa1` = M1 still, then stopped early at M1's page, 0x005d100f [HW]: attribute 1
keeps its word without draws, and the early stop's fault page follows `sa1` (LV's 0x04400000 was
LV's `sa1`). Row F (E1187), crumb3 after W2 and one stock fill, read `sa1` 0x01000000 [HW]: one fill
rewrote attribute 1, but not with the slot-3 event word H-EVT predicted (F-FILL4 failed against its
prediction, held); that the top byte is a count is not claimed [infer]. So `sa1` reads attribute 1
in every row that planted it (M, W, W2, V) and a client draw rewrites it; Q's 0x04400000 (E1182)
fits draws between the rows [infer]. In F a bare GETMISCINFO kick pass, our task idle, faulted at
the page in `sa13` (M13) by the time its reply returned, and job 3's kick was not answered nor its
command served [HW]: the kick pass itself faults on the rewritten bank, our after-read is not
needed, and the EDM serves nothing after the first fault; that the gate fills of rounds 41 and 42
met an EDM already stalled since job 2 is [infer]. Still open: what the fill's word means and what
the triangle writes into attribute 1; where `sa3`-`sa10` come from; why land's early stop faults at
page 0 (E1176, E1178); who wrote 0x00043000; what bits 6, 10 and 11 mean; the parts above. Not
retired.

Draw sequences and attribute 1, and land's stop with a planted sa1, 2026-11-24 (E1188 to E1200,
r44-n3i-n1, -n2 and -n3, flagged, module 079DD0D1 of fork r42-kernel ec6511d5de87, no rebuild or
boot; the kit's K8 draw lists). Six plants (rows WA-WD, WL, WF: E1188, E1190, E1192, E1194, E1197,
E1199) put M1 in `sa1` with no fault, as W [HW]. The crumb3 read after each, with a firmware load
and the declared begin draws between, read `sa1` 0x04400000 after fill, triangle (FT, E1189: FT-SAME
held), M1 kept after fill, fill (FF, E1191), 0x02400000 after a triangle alone (T, E1193) and after
triangle, fill (TF, E1195), and with no plant one fill after a fill-then-triangle stage read
0x05400000 (F2, E1196) [HW]. FF-N, T-N, TF-N and F2-N FAILED against their predictions (held),
X-KEEP (FF) and T-K FAILED against their predictions (failed): H-N, the event count, is falsified,
and none of H-LAST, H-K and H-ACC fits the five reads [HW against the frozen predictions]. So the
0x04400000 of the earlier rows is the word a fill then a triangle leave, over any word before [HW, 7
of 8 reads with that sequence, X's 0x04000010 the other]; a triangle writes attribute 1 and a fill
after it leaves the triangle's word [HW]; and a fill does not always write it: one fill after a
plant left 0x01000000 in F (E1187) and M1 in LF (E1200), and two fills left M1 [HW]. Row LM (E1198),
land on W's bank with no draws, read `sa0` = V0, `sa1` = M1, `sa2` = V2 and stopped at M1's page, as
landv did (LM-EARLY1, LM-KEEP and LM-V0 held) [HW]: land's image does not cause a page-0 stop (H-IMG
fails). Row LF (E1200), land after W's plant and one fill, read `sa0` 0x00000002, `sa1` = M1, `sa2`
0x01049b60 and stopped at page 0 (LF-EARLY0 held; LF-SA1 and LF-EVT FAILED against their
predictions) [HW]. So land's stop faults at `sa1`'s page with `sa0` = V0 (LM) and at page 0 with
`sa0` below one page (LF, and LC's `sa0` 0 in E1176 and E1178) [HW]; that the tick pass reads
through `sa0`, then `sa1` (H-SA0), and that LC's page 0 was `sa0`'s, are [infer]. Still open: what
writes `sa1` in some draw sequences and not in others (one fill has left three outcomes); what the
words 0x04400000, 0x02400000 and 0x05400000 mean; where `sa0`'s 2 comes from and whether `sa0` and
`sa2` read attributes 0 and 2; which access of the tick pass reads the page; where `sa3`-`sa10` come
from; who wrote 0x00043000; what bits 6, 10 and 11 mean; the parts above. Not retired.

Second reads, the rebuild images crumbz and landq, and which word land's stop faults at, 2026-11-25
(E1201 to E1233, r45-n3j-n1 to -n6, flagged; N1-N4 on module 079DD0D1 of fork r42-kernel
ec6511d5de87 with no rebuild, N5 and N6 on module EC553F41 of fork r45-kernel b1089172b2e7, which
adds our crumbz and landq images; the kit's K9 counts the CCB commands from the kernel's `ccb_sent`,
the control DK, which passed in every read). Sixteen plants (E1201, E1203, E1205, E1207, E1209,
E1212, E1214, E1216, E1218, E1220, E1222, E1224, E1226, E1228, E1230, E1232) put M1 in `sa1` with no
fault, WJ (E1218) the build control on the new module [HW]. Second reads agree: after a plant, fill,
fill left M1 (FF2, E1202), a triangle alone 0x02400000 (T2, E1204), a triangle then a fill
0x02400000 (TF2, E1206), and one fill M1 (F3, E1210); an unplanted fill after a fill-then-triangle
end read 0x05400000 again (F2b, E1211) [HW, every prediction held]. Two triangles left 0x08400000
(TT, E1208; ZTT, E1231): the second triangle decides the word, so H-FIRST is falsified and H-TRI's
prediction held [HW against the frozen predictions]. Every non-plant word read fits H-KC, one event
entry's pa1 with the count byte K the CCB commands since the load, which K9's counts confirm in
every stage [infer for the entry; HW for the counts]. crumbz, which writes no attribute (ZN, E1219:
V0, M1, V2 kept with no draws), read attributes 0-2 after each list [HW]: a triangle last leaves
`sa0` 0 and an EVENT_TIMER-shaped `sa2` with its word in `sa1` (ZT, ZFT, ZTT: E1221, E1223, E1231),
a fill last leaves `sa0` 2 and a timer-shaped `sa2` and does not touch `sa1` (ZF, ZFF, ZTF: E1225,
E1227, E1229). So the fills' events write attributes 0 and 2, land's running tick does not (R-DRAW
held, R-TICK fails), and attribute 1 takes only a triangle's word in every crumb3 and crumbz read
[HW]. Land read the same: LF2 (E1213) repeated LF's (2, M1, timer) and page-0 stop, LT (E1215) read
(0, 0x02400000, timer) and stopped at page 0 (LT-ONE failed, so LT did not split H-SA0 from H-HIST)
[HW]. One read breaks the pattern: LFF (E1217), land after two fills, read `sa0` 0, `sa1` 0x04000010
and a timer word (LFF-SA1 and LFF-SA0 FAILED against their predictions), where crumb3 and crumbz
read M1 after two fills three times [HW]; 0x04000010 is H-KC's word for the second fill's own slot-3
entry at K 4 (and X's, E1174), so H-TRI's "a fill's entries never write" meets one exception
[infer]. Row Q (E1233), landq writing 0x005d2000 to attribute 0 and M1 to attribute 1 with no draws,
read both back (Q-WRITE) and stopped at 0x005d1000, `sa1`'s page (Q-SA0 FAILED against its
prediction; Q-LOW scored cannot tell by its frozen rule) [HW]. So H-SA0 as "the tick pass reads
`sa0` first and faults at the first unmapped word" is falsified unless 0x005d2000 is mapped; two
readings survive, not told apart: the lowest faulting page is kept, or `sa0` is read first and
0x005d2000 is mapped [infer]. Both fit every stop read: page 0 with `sa0` below one page (LC, LC2,
LF, LF2, LT, LFF) and `sa1`'s page with `sa0` = V0 (LV, V, LM); LC's page 0 (E1176, E1178) is its
triangle's `sa0` 0 under either [infer]. A laptop event, not a row: after the first one-shot boot
onto EC553F41 the laptop hung hard with no oops or panic logged; a second boot ran the routine and
N5 and N6 cleanly; no cause is claimed (render-closing-r45-n3j-n5's fold notes). Still open: why
LFF's read differs from the other reads of fill, fill; why F's one fill read 0x01000000; whether
0x005d2000 is mapped; what bit 22 of the triangle's word means; where `sa3`-`sa10` come from; who
wrote 0x00043000; what bits 6, 10 and 11 mean; the parts above. Not retired.

Sidebands 0x043 and 0x803, two fills again, and where land's stop faults on a new module,
2026-11-25 (E1234 to E1245, r46-n3k-b5, -b6 and -n1 to -n4, flagged, every session on module
10BBF3BF of fork r46-kernel c5094783eb88, one build and one one-shot boot, which adds our landr and
landp images; rows R, P, R2 and P2 of the design, sessions N5-N8, were not run: the user stopped
the round after N4). B5 (0x043) and B6 (0x803), rebuilt on today's kit with an after-read, ran
crumb3 and our entry to done, left the issuer's sa0-sa31 as they were (pre = post = the kick's
after-read) and the next fill and triangle exact, every prediction held (E1234, E1235) [HW, one run
each]: bits 6 and 11 with bits 1:0 = 3 change neither the start nor the bank, so the start rule's
0x043 and 0x803 are now read, not inferred; 0x042 and 0x802 stay [infer]. Printed, not scored, one
read each: with 0x043 no V0 or V2 in pa0-pa15 (as 0x843), with 0x803 V0 and V2 in every fourth pa
(as 0x003); that bit 6 without bit 10 keeps crumb3's words out of the started entry's pa is [infer],
since those pa can hold words of earlier runs. Five plants (E1236, E1238, E1240, E1242, E1244) put
M1 in `sa1` with no fault, WA the build control [HW]. Two fills after a plant kept M1 with crumbz
(ZFF2, E1237) and with land twice (LFF2, LFF3: E1239, E1241), and three fills kept it with land
(LF3F, E1243) [HW]: fill, fill has now read M1 six times against LFF's 0x04000010 once (E1217), so
land's running tick does not make a fill write attribute 1 (H-FL fails; LFF2-FILL2, LF3F-SECOND and
LF3F-LAST failed as predicted) [HW against the frozen predictions], and what LFF read stays
[open]. `sa0` after two fills read 2 with land twice but 0x00040000 with crumbz (ZFF2-KEEP FAILED
against its prediction), against 2 and 0 before (E1227, E1217) [HW]: the list's `sa0` is not known.
Every land read of this round with `sa0` 2 and M1 in `sa1` stopped at 0x005d1000, `sa1`'s page, not
at page 0 (LFF2-PAGE0, LFF3-PAGE0 and LF3F-PAGE0 FAILED against their predictions) [HW], where LF
and LF2 with the same bank after one fill on module 079DD0D1 stopped at page 0 (E1200, E1213). So
"page 0 whenever `sa0` holds a word below one page" (six of six before) is not a rule, and both
readings row Q left, the lowest faulting page kept (R-LOW) and `sa0` read first with 0x005d2000
mapped (R-SA0), predicted page 0 for these stops: neither stands as stated [HW against the frozen
predictions]. The module and the number of fills before land changed together, and no row splits
them [infer]. Q2 (E1245) repeated Q's read and stop at `sa1`'s page with 0x005d2000 in `sa0` on the
new module [HW]: Q's bank now meets the two-read rule. Boot note, not a row: the r46 boot's KUnit
run logged a lockdep "trying to register non-static key" in sgxfive_debug_test_hold_recovery (also
in the netconsole logs of rounds 35 and 44), after which lockdep is off for the rest of each boot
(closing29/r46-n3k-logs/netconsole-r46.log). Still open: what moved the stop's page between the
(2, M1) reads (the module or the fill count); whether 0x005d2000 is mapped (rows P, P2); why LFF
read 0x04000010 and F 0x01000000; where ZFF2's `sa0` 0x00040000 comes from; what bits 6, 10 and 11
mean beyond the start; the parts above. Not retired.

Round 46's addendum: one fill, one triangle, landr and landp on the same boot, 2026-11-25 and -26
(E1246 to E1259, r46-n3k-n9, -n10, -n11 and -n13 to -n16, flagged, module 10BBF3BF, the boot of
B5-N4 with no rebuild, install or boot since, closing29/n3k section 11, decisions G-K all (a)).
Every row read post sa12 = V0, B6's pa0 (E12 held 7 of 7), and every plant (W9-W16: E1246, E1248,
E1250, E1252, E1254, E1256, E1258) put M1 in `sa1` with no fault [HW]. Land after one fill (LFK,
E1247; LFK2, E1251) read `sa0` 2 both times but `sa1` 0x01000000 once and M1 once, and stopped at
`sa1`'s page each time, 0x01000000 and 0x005d1000; land after one triangle (LTK, E1249) read LFK's
(2, 0x01000000), not LT's and ZT's (0, 0x02400000) (E1215, E1221), and stopped at 0x01000000 [HW].
So no land stop of this boot went to page 0 with sa12 = V0 (eleven of eleven, LFF2 to P2, six of
them with `sa0` 2), and one fill does not bring page 0 back: C-FILL (the number of fills moved the
page) is out on this boot [HW, LFK and LFK2]. 0x01000000 is a page the stop faults at [HW, two
reads]. The word `sa1` holds after a single draw is not stable on this boot: after one fill
0x01000000 once and M1 once, two minutes apart, after one triangle 0x01000000 against 0x02400000 in
four earlier reads (E1193, E1204, E1215, E1221), while the kernel's HKC line printed the triangle's
3:22 entry with 0x02400000 at K 2 as before [HW]; the stop's page followed `sa1` every time [HW].
E1204, E1215 and E1221 get appended corrections. That timing decides which word the emit's pass
reads (H-RACE) is the reading carried [infer]; the design's stop rule for LFK and LFK2 disagreeing
held N12-N16 for the user, who then ran N13-N16 and skipped N12 (LFKP, the K pad). landr (R, E1253;
R2, E1257) wrote 0x04400000 and M1, both pages known unmapped, and the stop faulted at M1's, the
lower, not at `sa0`'s (R-SA0 failed) nor at `sa0` + sa12 = 0x36404000 (R-SUM failed) [HW, two
reads]. landp (P, E1255; P2, E1259) wrote V0 and 0x005d2000 and the stop faulted at 0x005d2000: that
page is unmapped where the stop reads it [HW, two reads], and no stop at V0 + V0 = 0x64008000 (P-SUM
failed) [HW]. So Q and Q2 (E1233, E1245) had two unmapped words and kept the lower, as R and R2 did:
"`sa0` read first, 0x005d2000 mapped" is out, and the lowest faulting page (R-LOW) fits every stop
with both words above a page [HW pages; infer reading]. C-E0+ with `sa0` + sa12 read first and
unmapped is out for R's and P's banks [infer: the sums may be mapped]. R-LOW with page 0 unmapped
and attribute 0's 2 read as an address does not fit this boot's (2, ...) stops: either page 0 does
not fault with sa12 = V0 (C-E0), or on this module (C-MOD) or boot (C-BOOT), or 2 is not read as an
address [infer]. Still open: C-K, C-E0 and C-MOD against each other (N12 not run; decision K's
follow-up, a boot on module 079DD0D1 with a high sa12, design section 11.6); what decides the
single-draw `sa1` (0x01000000, M1, 0x02400000) and LTK's `sa0` 2; why LFF read 0x04000010; where
ZFF2's `sa0` 0x00040000 comes from; whether 0x01000000, 0x02400000 and the C-E0+ sums are mapped
elsewhere than where the stop reads; the parts above. Not retired.
