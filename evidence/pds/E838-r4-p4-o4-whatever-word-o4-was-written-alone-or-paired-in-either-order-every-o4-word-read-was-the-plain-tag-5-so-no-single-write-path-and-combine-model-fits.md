+++
id = "E838"
claim = "R4-pixel stage p4-o4 (Q276, 36 jobs in E808's p-c3 shape: a triangle's pixel program writing tagged words to o0 to o7 in E709's four-output setup, the words at bits 3:0, a job marker at bits 15:6, x and y jobs decoding to source pixels): the 8 controls passed (G-o4 on c-e709 and c-o4-u, c-o4-u and the swapped c-o4s-u reading tag 5 as E808, G-o1 tag-2 fraction 0.994 of 486 sources) and the replicate of c-o4-u read its class; in the 7 held-out value configurations (A3 = tag 13 alone, A4 = tag 5 with bit 4 alone, A then A4, A4 then A, A then A5, A5 then A, A3 then A4; 14 of 14 jobs) every o4 word read was the plain A (tag 5, bits 5:3 clear, the job's marker, 22 to 63 words a job, no A3, A4 or A5 word), so none of the 12 frozen models (single-write path V1 drops bit 3, V2 refuses a word with bit 3, V3 as written, by combine rule last, first, and, or, min) fits; frozen verdict 'family REFUTED: no (single-write path, combine rule) model fits the value rows; a new reading is needed'; the 12 predicate jobs (6 configurations, also all tag 5) are cannot tell by the frozen gate (the bit-4 pairs read one class in both orders)"
unit = "pds"
method = "R4-pixel stage p4-o4 of the question-closing pass, round 4 (decision R4 9a, plan closing4/pixel/exp-pixel-r4.md section 3.4), dataset render-closing-r4-pixel, on the laptop (host cedar, direct cable), 2026-11-11, attempt out/20261111-205726 (stage started 20:57:26 Mac time, the first stage; run.log), kernel 7.3.0-resgx545, module srcversion 99CD90DA26E3AFF9C450517 (the linux fork's branch resgx545 at a2788bd8, the rgn4 module; installed = loaded), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a (core 545 rev 0x1000d, DDK 1.7.17 build 862890 in the health lines), tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, TOOL.sha256), not rebuilt; freeze FROZEN.sha256 f9b0fa03... and PREDICTIONS.sha256 c939d0f5... before the first job, FROZEN.commits pinning the resgx545 files read at 5a13042; a debugfs reset before each job, STATUS2 0x400 after each reset, no fault, every job class ok, health ok after the stage; each job `probe --tri pixel --temps 32 --pixels --dump-render DIR --width 64 --height 64 --vtx-coords 2 --blk 4=0x00030001 --slot pixpds=pds_iter_xy.bin:12 --slot vtxuse=vtx_coords.bin PROGRAM` with r4o-CFG-x.bin or -y.bin from bins/ (gen/r4_o4.py: or.skipinv writes of marker << 6 | variant << 4 | tag; c-e709 is E709's own program unchanged); predictions frozen in predictions/p4-o4.tsv; scored by the frozen score/score_r4.py p4-o4 (score/score_o4.py, o4model.py; scorekit copied from resgx545); the kept score-p4-o4.txt and gate-p4-o4.txt were reproduced byte for byte at the fold (2026-11-11); the word histograms below are a post hoc reading at the fold (fold/posthoc_o4_bits.py and its output), not frozen"
tiers = ["HW", "infer"]
date = "2026-11-11"
data = ["render-closing-r4-pixel:out/20261111-205726/p4-o4/", "render-closing-r4-pixel:fold/"]
terms = ["PDS_SIZE.BITS17_16", "Universal Scalable Shader Engine (USSE)"]
+++
**What ran.** E808 found every o4 word tag 5 whether the program wrote 5' (tag 13, bit 3 set) last
or first, so neither "the last write wins" nor "the first write wins" fits, and the predicate
clause of Q276 could not be read. The round 4 reading listed three single-write paths (V1 the path
drops bit 3, V2 a word with bit 3 does not land, V3 the word lands as written) and five ways two
writes combine (last, first, AND, OR, the smaller); 12 of the 15 pairs fit E808. Stage p4-o4 tells
them apart with words that differ in other bits: A = tag 5, A3 = tag 13, A4 = tag 5 with bit 4,
A5 = tag 5 with bit 5, each job's marker at bits 15:6, an x and a y job a configuration.

**Frozen verdict (as printed).** `controls (value rows): PASS`, `controls (predicate rows, adds
G-o1): PASS`, `replicate c-o4-u: class A vs A: same`, `value survivors (0 of 12): none: no model
of the family fits`, `predicate rows: cannot tell (the bit-4 pairs read one class in both
orders)`, `rows: the o4 family reads is not supported: 6 held, 1 FAILED, 0 cannot tell of 7`,
`SUMMARY: family REFUTED: no (single-write path, combine rule) model fits the value rows; a new
reading is needed`; `gate p4-o4: PASS`.

**Results [HW].** The o4 words a job (tag 5 or 13 with its variant bits, x job / y job):

| configuration | o4 writes, in program order | set | read | words x / y |
|---|---|---|---|---|
| c-e709 | E709's program | control | A | 39 / 32 |
| c-o4-u | A3, A | control | A | 34 / 27 |
| c-o4s-u | A, A3 | control | A | 34 / 35 |
| c-u | A (G-o1: tag-2 fraction 0.994 of 486) | control | A | 34 / 23 |
| v-a3 | A3 | held out | A | 63 / 36 |
| v-a4 | A4 | held out | A | 45 / 47 |
| v-a-a4 | A, A4 | held out | A | 37 / 46 |
| v-a4-a | A4, A | held out | A | 26 / 36 |
| v-a-a5 | A, A5 | held out | A | 44 / 40 |
| v-a5-a | A5, A | held out | A | 40 / 39 |
| v-a3-a4 | A3, A4 | held out | A | 28 / 36 |
| pa-k0, k3, k7 | p1 A, !p1 A4 | held out | A | 22 to 56 |
| ps-k0, k3, k7 | !p1 A4, p1 A | held out | A | 22 to 56 |
| c-o4-u rep | A3, A | replicate | A | as c-o4-u |

Every job's marker proof passed (the words carry the job's marker, x m and y m + 1). The frozen
predictions: V1 reads A4 for v-a4, V2 reads no o4 word for v-a3 and A4 for v-a4, V3 reads A3 for
v-a3; the combine rules split the paired rows. Every model needs v-a4 to read A4: it read A.

**Read at the fold, post hoc (not frozen).** Over the 36 kept images the non-background words
carry tags 1 (33571), 2 (17631), 3 (2099), 5 (1340), 6 (201), 7 (16), 12 (68) and 15 (5), and
no word of tag 4 or 8; in E709's own program (c-e709) also tags 1, 2, 3, 5 and 6 only. No word of
any job has bit 4 or 5 set, and every tag-5 word's low 16 bits are exactly the job's marker << 6 |
5, whatever o4 was written (`fold/posthoc_o4_bits.txt`). The staged program of v-a4 does write the
word with bit 4: its `or.skipinv o4` encodes the immediate 0x4255 (marker 0x109), assembled again
at the fold and found in the frozen binary.

**What it shows and does not.** What the image shows at the tag-5 pixels does not follow o4's
write: a program that writes only A4, or only A3, gives the plain A word, which no instruction of
that program wrote to o4. So no model in which o4's own write lands (with bit 3 dropped, refused,
or two writes combined) fits, and the predicate clause cannot be read from these words. Two
readings fit, neither tested [infer]: the path that brings o4 out clears bits 5:3 of the word
(it keeps the tag's bits 2:0 and the marker); or the tag-5 words are not o4's at all but a
combination of two other outputs, tag 1 (o0) OR tag 4 (o3) being 5, which would also explain why
no tag-4 word is ever read. A run that changes o0's or o3's tag and leaves o4 alone separates
them. Not shown: which instances write o4, whether the predicate gates `p1 or.skipinv o4`, why
the pair counts wander (22 to 63 words).
