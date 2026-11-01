+++
id = "E529"
claim = "With enc[39] = 0 (the o join, chan0) the two parts of the class 9 test field are ORed and a part that is absent from the field counts as true: the rule (zero part: tanz if bit 41, else taz if bit 40, else true; sign part: pat if bit 43, else nat if bit 42, else true; p0 = zero part OR sign part) fits the 90 cases of and r1, r2 over the 15 field values 1 to 15 and six input pairs (90 of 90, a rule read from those 90 readbacks, so a fit to them: the first prediction, the parts ORed with an absent part false, fitted 75 of 90, the parts ANDed 48 and the OR of the set conditions 75, and the runner's verdict was NONE) and predicted, written before the run, all 270 cases of a fresh run on or and xor with registers and and with #7 (three probes, 15 values over six other input pairs each: 90 of 90, 90 of 90, 90 of 90); in particular every one-part field (1, 2, 4, 8) and the fields 3 and 0xc read true for every input of the 90 cases, which is the 'a one-part test is always true under the o join' reading"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e): probes/usse/rawjoin-o.toml probe usse-rawjoin-o-and (the first run, 90 jobs, kept: NONE) and probes/usse/rawjoin-o2-or.toml, rawjoin-o2-xor.toml, rawjoin-o2-and7.toml (probes usse-rawjoin-o2-or-fields, -xor-fields, -and7-fields, 90 jobs each, one file and one campaign run for each), all raw .long words of and/or/xor.testtaz.chan0 !c0, p0, r1, r2 (or #7) with enc[43:40] set to the field and enc[39] cleared; raw tables, run last, one probe at a time with a health triangle after each, no job failed to recover; the first table's prediction was written before the run (the E499 pair rule with the two parts ORed and an absent part false; the alternatives: the parts ANDed, the join bit ignored); the rule was read from the 90 readbacks of the first run and written down before the second tables ran, and the second tables ran with it as the hypothesis; recounted by a script outside the kit (75 for the first prediction, 48 for the parts ANDed, 75 for the OR of the set conditions and 90 for the rule on the first run; 90, 90, 90 on the second)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-rawjoin-o", "usse-rawjoin-o2-or", "usse-rawjoin-o2-xor", "usse-rawjoin-o2-and7"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

**What runs.** The word of and.testtaz.chan0 !c0, p0, r1, r2 (0x48081181000C0082) with enc[39]
cleared (the join bit of E499's table: `o` is enc[39] = 0, `a` is 1) and enc[43:40] = 1 to 15, run
as .long followed by mov r10, #0; p0 mov r10, #1. First run (and, r2): pairs (0, 0), (1, 1), (5, 3),
(0x7fffffff, 0xffffffff), (0x80000000, 0x80000000), (0xffffffff, 0xffffffff), results 0, 1, 1,
0x7fffffff, 0x80000000, 0xffffffff. Second runs: or with r2 over (0, 0), (1, 0), (0, 0x80000000),
(0x7fffffff, 1), (0xf0f0f0f0, 0x0f0f0f0f), (0x80000000, 0x80000000); xor with r2 over (0, 0), (5,
3), (0xffffffff, 0xffffffff), (0x7fffffff, 0x80000000), (0x80000000, 1), (0x12345678, 0x12345678);
and with #7 over r1 = 0, 7, 0xffffffff, 0x80000000, 0xfffffff8, 0x7ffffff8. The input pairs of each
form give these result classes: first run zero, positive and negative; or, xor: zero, positive,
negative; and #7: zero and positive only (no negative result).

**Results.** First run readings by field (six pairs, 1 = p0 set): 1, 2, 3, 4, 8, 0xa, 0xb, 0xc, 0xe,
0xf all 111111; 5 = 100011; 6 and 7 = 011111; 9 and 0xd = 111100. The prediction (the E499 pair rule
with the parts ORed) fitted 75 of 90: it was wrong in 15 cases, all in the fields 1, 2, 3, 4, 8 and
0xc, where the field has one part or the zero or sign part is absent (taz alone, for example, read
true for the five nonzero results). The rule above, read afterwards, fits 90 of 90 of them. The
second runs: 90 of 90 each on or, xor and and #7 (the runner's verdict SETTLED on the rule in all
three); the first prediction fits 74, 73 and 74 of 90 there and the parts ANDed 46, 44 and 46.

**What it shows.** [HW] A test word with enc[39] = 0 does not behave as E499's rule with the parts
ANDed: the join bit matters. The o join ORs the parts and a part absent from the field is true, so a
field of one part (and the fields 3 and 0xc, whose second part is absent) is always true under the o
join: for these words the test carries no information. With both parts present the OR is taken (5,
6, 7, 9, 0xa, 0xb, 0xd, 0xe, 0xf), but only the fields 5, 6, 7, 9 and 0xd tell the rule from 'always
true': there the zero part and the sign part are not complementary and the readings are 100011 (5),
011111 (6, 7) and 111100 (9, 0xd). The fields 0xa, 0xb, 0xe and 0xf have the zero part tanz and the
sign part pat, read 111111 on every input run (zero, positive and negative results), and the OR of
those two conditions is true for every result class run, so these four are tautologies that the data
cannot tell from an always-true word. The a join (enc[39] = 1) is E499's AND. [infer] An absent part
is true under both joins: under AND that leaves the other part (E499's a join), under OR it makes
the word always true, and the one-part fields read so. The assembler's `t` ("true") fits that
reading (`.testtaz` is "true AND zero", `.testtoz` "true OR zero", which is always true). That the o
join is the same field read through an or-gate is an inference from the 360 cases, and the rule
rests on five informative fields (5, 6, 7, 9, 0xd) times four forms. The assembler writes both
joins: `and.testtoz.chan0 !c0, p0, r1, r2` and `and.testnoz.chan0 ...` assemble with enc[39] = 0 (a
run of usse-asm on the host after the data, no hardware), so the rule covers words the assembler can
write; E499's 732 words, run as raw words, all had enc[39] = 1.

**What it does not show.** Chan fields other than chan0 with the o join (E530 ran the a join), the
shifts, the 8-bit and 16-bit lane operations, the other classes' tests, the field value 0,
immediates other than #7, and input pairs beyond those listed (the and #7 probe has no negative
result, the first run's pairs give two positive and two negative of six). The rule was read after
the first run, so the first run's 90 are a fit; the 270 of the second runs are a prediction. Narrows
Q137 (the o join and its two-part reading).
