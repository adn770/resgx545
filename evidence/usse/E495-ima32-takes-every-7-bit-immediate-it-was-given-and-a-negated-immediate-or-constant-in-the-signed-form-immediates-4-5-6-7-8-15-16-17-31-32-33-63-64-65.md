+++
id = "E495"
claim = "ima32 takes the seven-bit immediates 4, 5, 6, 7, 8, 15, 16, 17, 31, 32, 33, 63, 64, 65, 100, 125 and 126 (17 values; with E469's 0, 1, 2, 3 and 127, 22 of the 128 values have run in source 2 and 21 in source 3, where 3 was not run) in source 2 and in source 3, giving a * imm + c and a * b + imm (68 of 68 cases, two triples for each value and source), `.neg` negates in two's complement on the ten forms run, `.s` with #1.neg and #5.neg in source 2, #1.neg and #127.neg in source 3, c56.neg and c3.neg in source 2 and c56.neg in source 3, and `.u` with #5.neg and #127.neg in source 2 and #127.neg in source 3 (80 of 80 cases, eight triples each; leaving the `.neg` out fits 12 of the 80), and a dependent reader of an ima32 result sees it with and without `.nosched` on the writer after 0, 1, 2, 3, 4, 5, 6 and 8 nops, for an ima32, a mov and an xor reader (48 of 48 cases, one case per writer, distance and reader)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1124 (sha256 58907b06a8e9030472a809cd669d2c3823946fd67aaf4775f942704a90f6a5ae): probes/usse/ima32-forms.toml probes imm-range (68 cases), s-neg (80) and nosched (48) (dump.s); the campaign runner once for the table, no probe.py first run; the three probes were recounted from the readbacks (the model computed from the r1-r3 values the case dumped: 68, 80 and 48 of 68, 80 and 48)"
tiers = ["HW"]
date = "2026-11-08"
data = ["usse-ima32-forms"]
terms = ["Universal Scalable Shader Engine (USSE)", "REGTYPE.FPCONSTANT"]
+++

**What runs.** imm-range: `ima32.u r10, r1, #N, r3` and `ima32.u r10, r1, r2, #N` for the 17 values
of N, over (a, c) = (0xdeadbeef, 0x80000001) and (0xffffffff, 0x7fffffff) in source 2 and (a, b) =
(0xdeadbeef, 0x12345) and (0xffffffff, 3) in source 3. s-neg: the ten forms above, `ima32.s r10, r1,
#1.neg, r3` and so on, over eight triples (0, 0, 0), (1, 1, 1), (0xffff, 0x10000, 5), (0x7fffffff,
3, 0x80000000), (0x80000000, 2, 0xffffffff), (0xffffffff, 0xffffffff, 1), (0x12345678, 0x9abcdef0,
0xdeadbeef) and (7, 0x10001, 0), the register an immediate or a constant replaces not being read; c3
reads 0x3f800000 and c56 0xffffffff (E469). nosched: `ima32.nosched.u r11, r1, r2, r3` and `ima32.u
r11, ...`, then 0, 1, 2, 3, 4, 5, 6 or 8 `nop`, then `ima32.u r10, r11, #1, #0`, `mov r10, r11` or
`xor r10, r11, r1`.

**Results.** All three probes settled on the model: the reader's result is a * b + c (or its xor
with r1) in each of the 48 cases, with no stale 0xa4a5a6a7 anywhere; 68 of 68 immediates; 80 of 80
negations.

**What it shows.** [HW] The seven-bit immediates of E469 hold across the range (17 more values),
`.neg` is a two's-complement negation also for `.s` on an immediate or a constant (E470 ran `.u` on
those), and a dependent reader of an ima32 result needs no gap or `.sched` at the distances run,
with or without `.nosched` on the writer.

**What it does not show.** The immediates not run: 9 to 14, 18 to 30, 34 to 62, 66 to 99 and 101 to
124 (106 of the 128 values), and 3 in source 3. The `.neg` forms not run: `.s` with #127.neg in
source 2, with #5.neg in source 3, with c3.neg in source 3 and with any other constant, `.u` with
#1.neg and with a constant, and `.neg` with a repeat or a dual-issue form. A reader at the distance
7, a `.nosched` on the reader, writers other than `ima32.u`, and a reader in a loop. Narrows Q127
(`.neg` with `.s` on an immediate and a constant, the immediates 4 to 126) and Q052 (`.nosched` on
an ima32 writer and distances above 3: answered for the nops listed); both stay open for what is not
listed.
