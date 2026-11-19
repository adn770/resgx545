+++
id = "E1152"
claim = "r38-n3c-s1 stage tim (N3c R2 th, module 77917296, stock firmware, flagged, user present): a client fill's PDS program (the recorded pds-timer-tim-host) did movs tim of 0x00abcde0 under regtimeline sampling 0x0acc; the host's 0x0acc, a running count in all 8531 stored samples before, changed to 0x00abcde0 at 13.13 ms on the timeline's clock and no later sample differed, snap9 after the job read 0x00abcde0, and the program's tim stores read back 0x00abcde0: every control passed, 'N3c-R2 RULE: V0-HOLDS: the host sees the PDS write (expected)'; the first host read of 0x0acc after a PDS tim write, so the PDS's tim is the host's CR_EVENT_TIMER"
unit = "pds"
method = "r38-n3c-s1 (render/closing-r38-n3c-s1), stage tim of the question-closing pass (round 38: session S1 of closing29/n3c/design.md, N3c, row R2 th, the instrument under E1150's inference; flagged class, the user present with a reset ready: the row stops the EDM's tick by design until the stage's last reset), dataset render-closing-r38-n3c-s1; attempt out/20261119-092626 (stage tim at 09:26:51, after stage own's disarm, E1151; rc 0); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 77917296568EB311B89B0DA installed and loaded alike, linux fork r37-kernel 4f35fc20ffa9; stock firmware, own_arm off), one job after the kit's reset and health pair: `~/regtimeline 0.06 0.005 0x0acc -- ~/sgxfive-test-t30 probe --temps 32 --pds 36 --use bins/sa_dump.bin bins/pds-timer-tim-host__0.bin` (regtimeline sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803, r33-tim2's binding, read only; t30 sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7; the bins byte copies of resgx545-data pds/timer/pds-timer-tim-host/bins/ at 31ec9b2f, sha256 3968221c7f275002bae8be8edc83c83523c3abb1aef4b22f45b06166533c87f5 and a8315ccebfc0d83ba9780cb5f34c5099aa3534d678c4a610b7a5e968bcf557ca; `--pds 36` the recorded harness's data dwords, where the design wrote `--pds 4`, README 'Deviations'), snap0 and snap9 kept, snap9 read right after the job and before any reset; then the stage's reset and the kit's health pair (both exact), and stage post (the t30 triangle and fill, both diff 0); freezes: FROZEN.sha256 327cdaea6ef7f8eedd077410687714f6ed0b6c029173804436119d1c1e5a9412 (57 files), PREDICTIONS.sha256 adecdbe9a12d6db25dbb1a3cb72335099057edb1df1a2c79e533ef822346373e (3 files), pins in FROZEN.commits (the kit at 2ce7fc7; the recorded bins and raw.txt and r33-tim2's kept t1d timelines at data 31ec9b2f; t30's source 42c4de7); the frozen predictions predictions/tim.tsv (gen/make.py), the rule score/score.py, run by the driver (out/score-tim.txt) and again by hand on the kept directory (fold/reproduce-tim.out, the same lines); readings past the scorer's from the kept files, by hand (fold/FOLD-NOTES.md), not frozen"
tiers = ["HW"]
date = "2026-11-19"
data = ["render-closing-r38-n3c-s1:out/20261119-092626/tim/", "render-closing-r38-n3c-s1:out/20261119-092626/post/", "render-closing-r38-n3c-s1:fold/"]
terms = []
+++
**What ran.** The recorded probe `pds-timer-tim-host` (probes/pds/timer.toml): a 64x32 fill
whose PDS secondary program does `movs tim, ds0[48], ...` with ds0[48] = 0x00abcde0 (bit 24
clear: the counter is loaded and stays, doc/isa/content/pds/probe/inputs.md), then stores the
ALU's `tim` to scratch after 0 to 64 `nop`s (+0x008 to +0x014, +0x028 to +0x034). It was made
for a host read of 0x0acc, but its recorded run kept only the PDS's own reads (E1150's
inference). Here `regtimeline` sampled 0x0acc from 5 ms before t30 started for 60 ms, storing a
sample only when it differed from the last.

**Frozen verdict (as printed).** By the driver (out/score-tim.txt) and again by hand
(fold/reproduce-tim.out):

```
ROW th: class ok; timeline 8532 stored of 18199 samples, rc 0, ivl 3296 ns; change at 13132015 ns to 0x00abcde0 (0 stored after it); pre 8531 samples; snap9 0x0acc 0x00abcde0; scratch tim 0x00abcde0 0x00abcde0 0x00abcde0 0x00abcde0 0x00abcde0 0x00abcde0 0x00abcde0 0x00abcde0
SUMMARY: tim: controls: every control passed
N3c-R2 RULE: V0-HOLDS: the host sees the PDS write (expected)
```

**Results [HW].**

- Controls: `ivl` (TOTAL / samples 3296 ns, inside E1133's 2500..5000) and `pre` (8531 stored
  samples before the change, every one a running count) passed.
- The timeline: 0x0acc ran down from 0x01041bc2 (the first stored sample) to 0x01038477 at
  13126201 ns, then read 0x00abcde0 at 13132015 ns, 5.8 us later; no later sample differed, so
  it held 0x00abcde0 to the timeline's end. snap0 (before the job) read 0x010352eb, running;
  snap9 (after the job, before any reset) 0x00abcde0.
- The probe: job time 1013 us, o0 2048 of 2048; scratch +0x000 and the eight `tim` stores read
  0x00abcde0, as the recorded run's raw.txt.
- After the stage's reset the counter ran again: stage post's p1-tri snap0 read 0x0acc
  0x01053594 and p2-fill snap9 0x0101ed1f; both draws `diff: 0`.

**What it shows.** The host's read of CR_EVENT_TIMER (0x0acc) is the register a client PDS
program's `movs tim` writes: the running count gave way to the written value within one sample
interval of the fill's job and stayed there, in the host's reads as in the PDS's, until the
reset. The 0x0acc the host sampled as the firmware's running timer (E1131, E1133) and the `tim`
the PDS loads and reads back are one register, measured, where E1150 and the PDS books had the
host's side from the register names [GPL].

**What it does not show.** That a program started by an `emitpds` from an EDM task would write
it the same way: no emitted program's `movs tim` has been seen to run (E1150), so E1150's reading
B-1 still rests on that much [infer]. When within the job the PDS wrote it (the timeline's clock
is the host's, and the write is dated only within 5.8 us of a sample); one job.
