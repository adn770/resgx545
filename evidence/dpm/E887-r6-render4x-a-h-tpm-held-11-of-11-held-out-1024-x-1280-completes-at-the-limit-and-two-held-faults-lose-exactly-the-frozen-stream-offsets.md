+++
id = "E887"
claim = "R6-render4x set A, stages s0 and a (16 jobs, one attempt, 6 faults, no stop): H-TPM held out, 11 of 11 rows decided: on the rgn4 module a four-array 4x job of the full triangle faults iff the end of its target's tail-pointer entries, 4 x (Z(2tx - 1, 2ty - 1) + 1) with y on the even bits, passes the td.rgn of its context's maximum; 1024 x 1280 (end 0x13000 at td.rgn 0x13000, and its replicate), 992 x 1280 and 512 x 1536 completed on their own maximum and 1024 x 1024 and 1024 x 800 on a 1024 x 1280 maximum with 0 wrong pixels, where size rules of E868 said fault; 1024 x 1296, 1040 x 1280, 1024 x 1536 and 1024 x 800 on 2048 x 1024 faulted with E845's word (0x0100 at 0x10000011); two held faults, 1024 x 800 and 1280 x 768, lost exactly the frozen stream offsets as sets (43, header 0 among them, and 511); of H-TPM's eight variants only TPM-y-rgn survives; s0's three controls and a4 (1024 x 768 on 2048 x 1024, at the limit) passed"
unit = "dpm"
method = "R6-render4x set A, stages s0 (3 controls, fault limit 1) and a (13 rows, fault limit 8) of the question-closing pass, round 6 (decisions R6-2 a, R6-5 a; plan closing6/render4x/exp-render4x-r6.md section 2), dataset render-closing-r6-render4x, attempt out/20261112-144822 (s0 14:48:22, a 14:49:05 Mac time; driver log run-r6x-A.log), on the laptop (host cedar), 2026-11-12, kernel 7.3.0-resgx545, module srcversion 99CD90DA26E3AFF9C450517 (fork resgx545 a2788bd8, the rgn4 test kernel, the boot of rounds 5 and 6 before the reboot; installed = loaded, debugfs defaults checked at each stage start), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a); s0 the three controls of E845 unchanged; each a row `tri --tri-full --keep-going --keep-overflow --wait-ms 20000 --width W --height H --max-width MW --max-height MH --aa4` with E824's words (cmd:1=0xe0000000, cmd:10=0xeaa26e26, cmd:13=0x80000002, cmd:16=0xeaa26e26), --dump-render and the register snapshots, h1 and h2 with hold_recovery Y and their held TA data and parameter buffer kept; a debugfs reset before each job, render_rgn_arrays 0 and render_pb_pages 0x422 read back, the fill and the strict health triangle after each of the 6 fault-class events (a2, a3, a5, a14, h1, h2, each BIF_INT_STAT bits 15:0 0x0100 and BIF_FAULT 0x10000011), no 'recovery failed' line, health ok at each stage's end; a1r ran as a1 completed; the stage ran to its end (6 of its limit 8). H-TPM [E870, a post hoc fit on one dump], its seven variants, round 5's eleven dead rules and the held faults' lost offsets (predictions/h.tsv, by header position from the maximum's td.rgn) frozen before the first job (FROZEN.sha256 5fbd64f7..., 333 files; PREDICTIONS.sha256 15e50eda...; FROZEN.commits pins the seven resgx545 files the freeze names to commits on main, frozen against main d9b2969 and verified at the fold against its files; the generator's twin scan read resgx545-data main e5cdaf0a, postrun/data-view.txt); scored by the frozen score/score_r.py in the run (score-s0.txt, score-a.txt) and re-run on the kept files on 2026-11-12 with byte-identical output; postrun/verdict-A.txt is the verdict the driver names. The entries' end and td.rgn of the table below are the frozen tables' (gen/rules.py)"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r6-render4x:out/20261112-144822/s0/", "render-closing-r6-render4x:out/20261112-144822/a/", "render-closing-r6-render4x:postrun/"]
terms = ["CR_TE_AA", "CR_TE_TPC_ADDR", "Parameter Buffer (PB)", "CR_BIF_FAULT", "CR_BIF_INT_STAT", "region header"]
+++
**What ran.** E870 read H-TPM from E869's one held dump: the 4x tail pointers are one dword per tile
of the doubled grid (16 x 8 pixels) at TA-data offset 4 x Z(x, y), Z the bit interleave with y on
the even bits; a four-array 4x job faults iff the end of its target's entries passes the `td.rgn` of
its context's maximum, and a held fault loses the stream offsets of the in-target headers whose word
1 lies at an in-target entry. It fitted the 26 outcomes on record, all known when it was written.
Stage a froze it on rows where it disagrees with the size rules: sizes it calls complete past 1024 x
768 (a1, a12, a13 on their own maximum; a8, a9 on a larger one), sizes just past its limit (a2, a3,
a14) and 1024 x 800, which a9 runs on a taller maximum, on a wider one whose `td.rgn` stays 0x7000
(a5), with two held faults (h1, h2) whose lost offsets were frozen as sets. a4, 1024 x 768 on 2048 x
1024 (end equal to `td.rgn`), was the premise control.

**Frozen verdict (as printed).** s0: `controls {'s0-1x-1024x768': 'PASS', 's0-4x-288x144': 'PASS',
's0-4x-1024x768': 'PASS'}; later stages open`. a: `H-TPM: a four-array 4x job faults iff the end of
its target's Z-order tail-pointer entries (y on the even bits) passes the td.rgn of its context's
maximum, and a held fault loses exactly the frozen stream offsets (a1, a8, a9, a12, a13 complete
where K-OR and other dead size rules said fault; a2, a3, a5, a14 fault; h1 and h2 set equal) (11 of
11 rows decided); variants of the Z-order rule no decided row contradicts: TPM-y-rgn; dead size
rules: none`.

**Results [HW].**

| job | target on maximum | entries end, `td.rgn` | outcome | scene pages, TA data |
|---|---|---|---|---|
| a4 (control) | 1024 x 768 on 2048 x 1024 | 0x7000, 0x7000 | complete, 0 wrong | 193, 274432 |
| a1, a1r | 1024 x 1280 own | 0x13000, 0x13000 | complete, 0 wrong (both) | 321, 233472 |
| a12 | 992 x 1280 own | 0x12fe0, 0x13000 | complete, 0 wrong | 313, 233472 |
| a13 | 512 x 1536 own | 0x12000, 0x13000 | complete, 0 wrong | 193, 172032 |
| a8 | 1024 x 1024 on 1024 x 1280 | 0x8000, 0x13000 | complete, 0 wrong | 257, 233472 |
| a9 | 1024 x 800 on 1024 x 1280 | 0x7ac0, 0x13000 | complete, 0 wrong | 201, 233472 |
| a2 | 1024 x 1296 own | 0x13ab0, 0x13000 | fault 0x0100 at 0x10000011 | - |
| a3 | 1040 x 1280 own | 0x18560, 0x13000 | fault, same word | - |
| a5 | 1024 x 800 on 2048 x 1024 | 0x7ac0, 0x7000 | fault, same word | - |
| a14 | 1024 x 1536 own | 0x14000, 0x13000 | fault, same word | - |
| h1 (held) | 1024 x 800 own | 0x7ac0, 0x7000 | fault; lost set equal (43) | 201 written |
| h2 (held) | 1280 x 768 own | 0xc800, 0x7000 | fault; lost set equal (511) | 241 written |

h1 lost the offsets from 0x7000 to 0x7ab0, header 0 among them (frozen: yes); h2 from 0x7ffc to
0xc7f0, header 0 intact (frozen: no). The completed rows have 0 region headers off the doubled-grid
rule from the maximum's `td.rgn` and nothing non-zero below it. The scorer's comparison columns:
a1 contradicts the dead K-H, K-OR, K-P and K-AREA, a12, a13, a8 and a9 K-H and K-OR, and the faults
the four TPC rules and some K rules; of the variants, x on the even bits or a limit at the room's
end, the OTPM or the state page each misses a decided row. Reported, not scored: a12's scene used
313 pages where U4 gave 311 (`DIFFERS`); every other completed row matched U4. Explore (printed by
the frozen scorer): a3 had 218240 right pixels before its fault, a2, a5, a14 none; in h1's held
dump no header has a zero word 0 (header 0 aside) and 42 have word 0 bit 27 set, and against a9 (its
completed twin on the larger maximum) 43 headers differ in word 0 and none in a non-zero word 1;
in h2's, 189 headers of in-target tiles have a zero word 0 and 401 have bit 27 set.

**What it shows.** [HW] H-TPM predicted all eleven held-out rows, where it disagrees with every
size rule: 1024 x 1280 completes exactly at its limit, a target one tile row taller or one tile
column wider faults, and 1024 x 800 completes or faults by its context's maximum alone. Two held
faults lose exactly the offsets the rule names, as sets, one with header 0 and one without. Of the
eight variants only the frozen one (y on the even bits, limit `td.rgn`) fits every decided row.
[infer] On the rgn4 module a four-array 4x job needs its target's Z-ordered tail-pointer entries to
end at or before the region headers; where they pass them the TA's tail-pointer writes over the
headers take the stream offsets with them, and a zero offset sends the 3D to the request base.

**What it does not show.** That a kernel giving more room ends the fault (E889); the 189 word-0
losses and bit 27 (seen again here, not scored), the 4096-wide residue of E828 and E846 (no
4096-wide row ran); why a12's scene took two pages over U4 (one row, read from the scorer's
report). One run each (a1 twice), one boot.
