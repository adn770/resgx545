+++
id = "E850"
claim = "Offline reading of kept images (Q276; no new job, post hoc against E838's reading, no held-out row): E838's reading 'the path that brings o4 out clears bits 5:3 of the word' is refuted on the kept data of E808 and E838: in E808's p-c3 (words marker * 16 + tag, so the marker's two low bits sit at bits 5:4) the 44 of 58 jobs whose marker has a non-zero bit there held 1525 tag-5 words, all 1525 with the job's whole marker and none with bits 5:4 cleared, and E838's bridge control c-e709-x (E709's own program, every output word 0xcfN) read 0xcf5 at all 39 of its tag-5 words; so bits 5:4 of the tag-5 word are kept when every output carries them and absent when only o4 does (E838's v-a4), which no rule local to o4's word gives [infer]; of a family of 821 bitwise models declared before the check (OR, AND, XOR over every subset of one instance's o0 to o7, and MUX of bits 2:0 of one output with bits 5:3 of another), 9 reproduce the tag-5 word in all 8 kept configurations: OR(o0, o3), AND(o4, o6), XOR(o0, o2, o6), XOR(o3, o5, o6) and MUX(bits 2:0 of o4, bits 5:3 of o_i) for i = 0, 2, 3, 5, 6; no kept job changes o0, o2, o3, o5, o6 or o7, so nothing kept separates the nine"
unit = "pds"
method = "Offline, 2026-11-12, round 5 planning of the closing pass (plan closing5/pixel/exp-pixel-r5.md sections 1.1 to 1.3, user decision R5-1 a: land the offline result before any freeze), no laptop, no job; two standard-library scripts read the published kept images: closing5/pixel/o4_offline.py (sections A to F of closing5/pixel/o4_offline.out) over E808's p-c3 (render-closing-r3-pixel, attempt out/20261110-160415/p-c3, markers bins/c3-markers.tsv, 58 marker jobs) and E838's p4-o4 (render-closing-r4-pixel, attempt out/20261111-205726/p4-o4, markers bins/p4o4-markers.tsv, 36 jobs), counting per job the tag-5 words that carry the job's marker, the marker with its two low bits cleared, or another; closing5/pixel/o4_family.py (closing5/pixel/o4_family.out) declares the bitwise family in its docstring and code before it checks it against 8 kept configurations written out from E808's and E838's generators and words (R4 base, v-a3, v-a4, v-a-a5, c-e709-x; R3 o4s-u, k5 and k7, k3); the reading 'clears bits 5:3' was stated by E838 on 2026-11-11, before this count, and the family was declared before its check, but neither is a frozen prediction of a run: post hoc on kept data; both scripts re-run at the fold from their published copies (cited/closing5/pixel in resgx545-data) with output byte-identical to the kept .out files; E838's own fold/posthoc_o4_bits.txt (first line, c-e709-x low6 0x31 to 0x36, 1539 words of marker 0x33) agrees"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r3-pixel:out/20261110-160415/p-c3/", "render-closing-r4-pixel:out/20261111-205726/p4-o4/", "render-closing-r4-pixel:fold/", "cited-scratch:closing5/pixel/"]
terms = ["PDS_SIZE.BITS17_16", "Universal Scalable Shader Engine (USSE)"]
+++
**What was read.** E838 left two readings of the tag-5 words of E709's setup [infer]: the path that
brings `o4` out clears bits 5:3 of the word (R-CLR), or the tag-5 words are not `o4`'s at all but a
combination of other outputs, tag 1 (`o0`) OR tag 4 (`o3`) being 5. Both rest on one fact of
E838's value rows: whatever `o4` was written, the word read was the plain tag 5 with the job's
marker. The kept images of E808 and E838 hold words in which the bits above the tag are set in
every output, which tells the two apart without a new job. Nothing here was frozen before a run:
the count is post hoc against a reading stated before it (E838, 2026-11-11), and the family below
was declared before its check.

**Results [HW], read from kept images.** From `closing5/pixel/o4_offline.out`:

| data | words | bits 5:4 kept | cleared | other |
|---|---|---|---|---|
| E808 p-c3, 44 jobs with marker bits at 5:4 (of 58) | 1525 tag-5 | 1525 | 0 | 0 |
| E838 c-e709-x (E709's program, o4 = 0xcf5) | 39 tag-5 | 39 (0xcf5) | 0 | 0 |

E808's words are `marker * 16 + tag`, so the marker's two low bits sit at bits 5:4 of every word of
a job, the tag-5 words included; per job 21 to 51 tag-5 words, every one with the job's own marker
(section A). E838's c-e709-x writes 0xcf0 | tag at every output, so every word of that job has bits
5:4 set: 1539 of 1539, tags 1, 2, 3, 5 and 6 (section B; E838's `fold/posthoc_o4_bits.txt` agrees).
c-e709-y and the 34 marker-layout jobs of E838 (marker at bits 15:6) have none.

Other facts of the same files (sections C to F): every tag-5 and tag-6 pair decodes to an (even x,
even y) source (1114 and 63 pairs) and every high half is the exact coordinate of one pixel, so a
tag-5 word does not mix two instances' coordinates; E808's k5 and k7 jobs, whose `o1` word is 12
at every instance, still read 35 to 45 tag-5 words a job; an `o0`-only program (E808's c-rd-pa)
leaves no displaced word (1062 own, 0 other); words with tags no instruction wrote occur, tags 13,
14 and 15 in E808 (6, 4 and 88 words) and 5 tag-15 words in E838's c-v-a3-x, the one job whose
`o4` word is 13 (13 OR 2 is 15).

**The declared family [infer].** `closing5/pixel/o4_family.py` declares, before its check, OR, AND
and XOR over every non-empty subset of one instance's `o0` to `o7` (765 models, a single output
once) and MUX(i, j), bits 2:0 of `o_i` with bits 5:3 of `o_j` (56), and checks them against 8 kept
configurations: E838's base, v-a3, v-a4 and v-a-a5, c-e709-x, and E808's o4s-u, k5 and k7, and
k3. Nine of 821 reproduce the tag-5 word in all eight (`closing5/pixel/o4_family.out`):

| model | how it gives tag 5 |
|---|---|
| OR(o0, o3) | tag 1 OR tag 4 |
| AND(o4, o6) | 5 AND 7; 13 AND 7 is 5 too |
| XOR(o0, o2, o6), XOR(o3, o5, o6) | an odd count keeps the marker |
| MUX(o4; o0), MUX(o4; o2), MUX(o4; o3), MUX(o4; o5), MUX(o4; o6) | o4's bits 2:0, another's 5:3 |

Refuted on the way: every model that reads `o1` (E808's k5 and k7), `o4` as written (E838's
v-a4), and any XOR of an even count (the marker would cancel). The nine have nine different
predictions for a walk that puts bit 4 on one output at a time (the plan's stage p5-o4).

**What it shows.** R-CLR is refuted: bits 5:4 of the tag-5 word are kept when every output carries
them (E808's markers, E709's 0xcfN) and absent when only `o4` carries them (E838's v-a4, 92 words).
No rule local to `o4`'s own word does both; what decides those bits is what the other outputs
wrote [infer from the two facts]. E838's second reading (OR of `o0` and `o3`) survives, with eight
kin of the declared family. Refuted by: a tag-5 word in those 44 jobs with the marker's low bits
cleared (none).

**What it does not show.** Which of the nine models holds, or whether the true rule is in the
family at all (it was declared, not derived): no kept job changes `o0`, `o2`, `o3`, `o5`, `o6` or
`o7`. Where `o4`'s own word lands, whether the predicate gates `p1 or.skipinv o4`, and why pair
counts wander (22 to 63) stay open (Q276). The family check is a fit over kept configurations,
not a held-out test.
