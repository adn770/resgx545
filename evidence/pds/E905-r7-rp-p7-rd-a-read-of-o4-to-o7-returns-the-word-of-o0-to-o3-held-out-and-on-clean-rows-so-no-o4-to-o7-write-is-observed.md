+++
id = "E905"
claim = "r7-rp stages p7-rdc and p7-rd (Q276, 48 jobs, E878's readback rerun with the class share taken over the own-source words): in E709's command (state block word 4 at 0x00030001) a `mov` from o1 to o3 inside the instance reads back that output's own word and a read of o4 to o7 reads the word of o0 to o3, the register number modulo 4, so no read of o4 to o7 shows a word written there: R6's rd-1 to rd-7 replicated the vector S S S A0 A4 A4 A4 (H-MOD4) at own-source shares of 0.905 to 1.000 with every rival class at 0, n-rd-4 and x-rd-4 read o0's word (A0) as in R6; held out, x-rd-6 and x-rd-7 (o6 and o7 written with tags of their own) read o2's and o3's words and n-rd-5 (no o5 write) o1's; the clean rows, which write only o0 (word A) and o_j (word B) and read o_j, read word A for o4 (cl-4, 1062 of 1062 TRI pixels in both jobs) and for o5 to o7 no word of the job (cl-5 to cl-7: background, zero and another configuration's words, never word B), and cl-p4 (cl-4 with `p1 or.skipinv o4` under the g25 test, k = 0) read word A on every lane; R6's bridge controls passed (c-u tag-2 fraction 0.990, c-all4 5:1, c-ow and c-rd-0 1.0 of TRI, c-prd-0's lanes as frozen); frozen verdict 'H-MOD4 held (17 of 17 entries): rd vector S S S A0 A4 A4 A4 (H-FOUR, H-MOD4) replicated; n-rd-4 A0, x-rd-4 A0; x-rd-6 A4 (o2's word), x-rd-7 A4 (o3's), n-rd-5 A4 (o1's); cl-4 A0 (word A); cl-5 X (no word of the job), cl-6 X (no word of the job), cl-7 X (no word of the job) (not word B); cl-p4 1:2,1:2,1:2,1:2 (word A on every lane)'"
unit = "pds"
method = "r7-rp stages p7-rdc and p7-rd of the question-closing pass, round 7 (decisions R7-2 a; plan closing7/a/exp-pixel-r7.md sections 1.4 and 3.4, user decision 4 a), dataset render-closing-r7-rp, on the laptop (host cedar), 2026-11-12, one attempt out/20261112-205431 (started 20:54:31 Mac time, run-r7r.log; 143 jobs in nine stages, s0 first, the session gate, which passed 4 of 4: the default 64 x 64 triangle exact with t4, t6 and t7 and E831's z-ctl-34x18-y storing 924 with t4), kernel 7.3.0-resgx545, module srcversion 41E2F5C756F96D20F7109A4 (fork 3f0b3e74, installed = loaded, knobs at their defaults at every stage start, read only), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a; tools ~/sgxfive-test-rgn4 (t4, sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a), round 6's t6 (built from resgx545 d9b2969, sha256 97df5c0ebf5bff2786a59b302e9a8a722bad36f0ef2f5dba11b6f2957f4ad98c) and t7, built by the lead on the build host from resgx545 1c64f3a, which allows odd widths (lead/build_tool7.sh, source pinned in TOOL7SRC.sha256, sha256 f2df4f99add18f011a3607dc3a73ac42cdfab3ec730d1e1f8cd7621761643375 in TOOL7.sha256, the slot run/freeze_r7.sh tool7 filled once, checked on the laptop before every stage); tables, predictions, models, scorers and runner frozen before the first job (FROZEN.sha256 33237f0d..., PREDICTIONS.sha256 c4be8ddd...; FROZEN.commits pins the resgx545 files read at 1c64f3a and data 830641e6); every stage ran to its end with health ok after it, no stop, no lead decision during the run and no reboot. Scored by the frozen score/score_r7.py in the run (out/ATT/score-STAGE.txt); at the fold (2026-11-12) the same scorer re-run on the kept files gave output byte-identical to the kept one for every stage (p7-rd's once its first line, the absolute path of the kept p7-rdc directory, names the run's tree), and the 944 kept files decompress to the raw sha256 the laptop logged (fold/reproduce.sh, fold/reproduce.out). Rows (t4): E878's p6-rd shape, `probe --tri pixel --temps 32 --pixels --dump-render --width 64 --height 64 --vtx-coords 2 --blk 4=0x00030001` with E709's pds_iter_xy and vtx_coords, each configuration an x job and a y job; stage p7-rdc, R6's 14 bridge controls (c-e709, c-u, c-all4, c-ow, c-rd-0, c-prd-0 at k 1 and 7, R6's programs byte for byte), gated the stage and passed; p7-rd: the replicates rd-1 to rd-7, n-rd-4 and x-rd-4 (R6's programs byte for byte, hashes pinned), held out x-rd-6, x-rd-7 and n-rd-5, the clean rows cl-4 to cl-7 and cl-p4 (new programs assembled with R6's method and new markers 0x1f0 to 0x1ff); scorer score_rd7.py (R6's reader with R6's modules copied): a word is own-source when it decodes to the pixel itself, a configuration reads class L when L holds at least 0.85 of the own-source words in both jobs and no other model class more than 0.02, fewer than 300 own-source words is cannot tell, a replicate whose top label differs from R6's voids its entry; the clean rows by R6's original rule (one class at 0.90 of all TRI pixels in both jobs) and cl-p4 by R6's lane rule; the scorer was replayed before the freeze on R6's kept p6-rd as its fit set (the vector and the own-source counts of E878's post hoc reading, 0.903 to 1.000) and on a doctored rd-5 that must not read H-MOD4. Every job class ok"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-rp:out/20261112-205431/p7-rdc/", "render-closing-r7-rp:out/20261112-205431/p7-rd/", "render-closing-r7-rp:out/20261112-205431/s0/", "render-closing-r7-rp:bins/", "render-closing-r7-rp:fold/"]
terms = ["PDS_SIZE.BITS17_16"]
+++
**What ran.** E878 read each output register back inside the instance (`mov r10, oN`, then
`o0 = r10`) and its frozen verdict was cannot tell: the class share was taken over all 1062 TRI
pixels, of which 113 to 134 hold words other sources' `o1` to `o3` writes displaced there. Read
after that run, `o1` to `o3` read back their own words and `o4` to `o7` the words of `o0` to `o3`
(H-MOD4). This stage reran it with the share taken over the own-source words, added three held-out
configurations and four clean rows that write no `o1` to `o3`, so no displaced word can land, and a
predicated clean row.

**Frozen verdict (as printed).** `H-MOD4 held (17 of 17 entries): rd vector S S S A0 A4 A4 A4
(H-FOUR, H-MOD4) replicated; n-rd-4 A0, x-rd-4 A0; x-rd-6 A4 (o2's word), x-rd-7 A4 (o3's), n-rd-5
A4 (o1's); cl-4 A0 (word A); cl-5 X (no word of the job), cl-6 X (no word of the job), cl-7 X (no
word of the job) (not word B); cl-p4 1:2,1:2,1:2,1:2 (word A on every lane)`; the gate: `gate PASS;
c-all4 5:1; TRI 1062`.

**Results [HW].** Top label and its share of the own-source words, x job then y job
(`out/20261112-205431/score-p7-rd.txt`):

| row | reads | class | x | y | R6's top |
|---|---|---|---|---|---|
| rd-1 | o1 | S | 2:1 949/949 | 2:1 1032/1044 | 2:1 |
| rd-2 | o2 | S | 3:1 940/940 | 3:1 940/1038 | 3:1 |
| rd-3 | o3 | S | 4:1 923/923 | 4:1 951/1037 | 4:1 |
| rd-4 | o4 | A0 | 1:2 932/932 | 1:2 951/1049 | 1:2 |
| rd-5 | o5 | A4 | 2:2 905/916 | 2:2 1031/1044 | 2:2 |
| rd-6 | o6 | A4 | 3:2 921/921 | 3:2 939/1037 | 3:2 |
| rd-7 | o7 | A4 | 4:2 937/937 | 4:2 943/1032 | 4:2 |
| n-rd-4 | o4, not written | A0 | 1:2 939/942 | 1:2 943/1038 | 1:2 |
| x-rd-4 | o4, tag 13 | A0 | 1:2 934/935 | 1:2 947/1044 | 1:2 |
| x-rd-6 (held out) | o6, own tag | A4 | 3:2 950/950 | 3:2 946/1043 | |
| x-rd-7 (held out) | o7, own tag | A4 | 4:2 923/923 | 4:2 925/1014 | |
| n-rd-5 (held out) | o5, not written | A4 | 2:2 938/938 | 2:2 1025/1042 | |

Every rival class held 0 own-source words in every row (shares 0.905 to 1.000). The clean rows, by
R6's rule over all 1062 TRI pixels: cl-4 read word A (1:2) at 1062 of 1062 in both jobs; cl-5, cl-6
and cl-7 read no word of their job (background 814, 571 and 405 to 351 pixels, zero words 133 to
455, words of marker 0x1f5, another configuration's, 60 to 201) and never word B; cl-p4 read word
A on all four lanes. The bridge controls passed as frozen (c-u 0.990 of 487 sources, c-all4 5:1,
c-ow 1:1 and c-rd-0 1:2 at 1.0 of TRI, c-prd-0's lanes 1:2, 1:1, 1:2, 1:2 at k 1 and 1:2 on all
four at k 7).

**What it shows.** In this command a read of `o4`, `o5`, `o6` or `o7` inside the instance returns
the word of `o0`, `o1`, `o2` or `o3`, whether the higher register was written, with which tag, or
not at all: held out where o6 and o7 carried their own tags and where o5 was not written, and on
clean rows where o4 to o7's only possible source is the program's own write. With E871 (no own
word of o4 to o7 on any pixel) nothing observes a write to o4 to o7 here: a write that is not
stored and a register that aliases o0 to o3 for reads cannot be told apart by any read we have
[infer]. cl-p4 shows that the predicated write `p1 or.skipinv o4` is not observable either: o4
reads o0's word on every lane.

**What it does not show.** Whether the hardware stores the o4 to o7 writes somewhere no read reaches
(E709's command only, state block word 4 at 0x00030001); the predicate's effect on an o4 write,
which by R6-6 a, carried by user decision 4 a, is retired as not observable; what o5 to o7 hold on
the clean rows beyond "no word of the job". Why the lane of the OR's o3 word depends on the job
(E880) was not run here.