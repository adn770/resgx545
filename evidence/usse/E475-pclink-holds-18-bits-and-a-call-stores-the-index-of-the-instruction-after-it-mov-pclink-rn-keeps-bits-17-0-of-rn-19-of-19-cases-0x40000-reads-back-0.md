+++
id = "E475"
claim = "pclink holds 18 bits and a call stores the index of the instruction after it: mov pclink, rN keeps bits 17:0 of rN (19 of 19 cases, 0x40000 reads back 0, 0x7fffffff 0x3ffff, 0x80000000 0, 0xa5a5a5a5 0x1a5a5; the whole 32 bits come back for no value above 0x3ffff), ba.savelink and br.savelink store the index of the next instruction (calls with the next instruction at index 20, 40, 64, 127 and 128, and a predicated call taken: 9 of 9) as an absolute index counted from the program start of a fill (the code base of a placed program: E476), a predicated ba.savelink whose predicate is false still writes pclink (one case, p0 ba.savelink with p0 clear: the preset 0x77 read back 0x15, the index after the call, with the call not taken; br.savelink, other predicates and !pN were not run), and a lapc after mov pclink, rN uses the new value with no instruction between them (19 of 19 cases with 0 to 3 instructions between, with and without .nosched on the move and on the lapc: the stale link of the call never used); pclink is not reset between jobs: a reader job reads the value a writer job left in 94 to 98 percent of its 2048 pixels (the ten reader jobs of usse-pclink-pixels, after five writers) and 0xeb3 or 0x98 in the others, which are aligned 2 x 2 quads of pixels (every deviant pixel has its x^1, y^1 and diagonal neighbours deviant too)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/link.toml (dump.s, 6 probes and 66 cases: ba-savelink-read 10, pclink-roundtrip 19, pclink-initial 3, lapc-gap 19, filler-control 3, control-e091 1, pclink-leftover 11) and probes/usse/pclink.toml (1 probe, 15 jobs, every pixel kept); the link table lost four cases of the plan (calls with the next instruction at index 255, 256, 257 and 300) because sgxfive-test refuses programs of over 256 words ('not 1 to 256 USSE words'): the first run of the 59-case table stopped at case 7 of ba-savelink-read with that message and its output was not kept by the runner, so nothing of it is in the data, and the table was rerun with the four cases dropped (55 cases, joined by the 11 cases of pclink-leftover, which first ran in an earlier table, to make the 66 of the dataset); the dropped cases are the calls at 255, 256, 257 and 300 that the question text of probe usse-link-ba-savelink-read (\"calls at indices up to 300\") still names, as it ran; two runs of every probe (probe.py outside the data, the campaign runner the dataset); the readbacks are the same in 58 of the 66 shared cases, and the 8 that differ are the reader jobs of pclink-initial (3) and pclink-leftover (5 of its 6): their pixel mixtures vary from run to run, the majority value agrees; over the nine fill tables (the datasets other than pclink and the placed ones) runs 1 and 2 agree in 1828 of the 1844 cases they share, and the 16 that differ are cross-job readers (pclink-initial 3, pclink-leftover 5, pflow-leftover 8), whose 2048-pixel mixtures vary (the author's tally: run 1 is not kept in the data; the 1844 and the 16 are consistent with the datasets); in the first run by probe.py the third pclink-initial job read 0x98 in the scratch word, which in the second is one of the minority values of every job; pclink-pixels ran once (campaign)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-link", "usse-pclink"]
terms = ["Universal Scalable Shader Engine (USSE)", "Event Data Master (EDM)"]
+++

**What runs.** Each case is a fill whose program does the instructions under test and stores r10-r17
and r1-r8 to scratch (dump.s) with r10 as the pixel. ba-savelink-read: `mov r14, #0; mov r12, #R;
ba.savelink #L; R: ...; L: mov r14, pclink; ba #E`, R the assembler's index of the instruction after
the call (r12 holds it for the comparison), in cases 0 to 6 with `ba.savelink` at R = 20, 20
(`br.savelink` as the control), 20 (`mov.nosched` read), 40, 64, 127, 128; case 7 a taken `p0
ba.savelink` and case 8 an untaken one with `mov pclink, r7` (0x77) before; case 9 two calls in a
row. roundtrip: `mov pclink, r1` then `mov r10, pclink` for r1 = 0, 1, 0x123, 0xffff, 0x10000,
0x3ffff, 0x40000, 0x7fffffff, 0x80000000, 0xffffffff, 0xa5a5a5a5, 0x5a5a5a5a, with `.nosched`,
nops between, and a second read. lapc-gap: after a call, `mov pclink, r5` (r5 the index of a marker
word), 0 to 3 `nop`s (or `mov r11, #1`), then `lapc`; r10 = 0x600D when the new link was used,
0x5741 for the call's stale link, 0xFA11 when it fell through. initial: `mov r10, pclink` first
in the program, three jobs. leftover and pixels: a writer job (`mov pclink, r1; mov r10, pclink`),
then a reader job (`mov r10, pclink`), five pairs, then a second reader.

**Results (campaign run).**

- ba-savelink-read: r14 (the link read in the routine; r15 in cases 7 and 8, where r14 keeps its
  preset) is the index of the instruction after the call in all 9 cases with a call taken: 0x14,
  0x14, 0x14, 0x28, 0x40, 0x7f, 0x80, 0x15 (taken `p0`) and 0x15 (second of two calls, which
  overwrote the first, 0x13). `br.savelink` stores the same index as `ba.savelink`. Case 8 (`p0
  ba.savelink` with p0 clear): r11 = 2 (the instruction after the call ran) and r15 (the link read
  after it) = 0x15, not the preset 0x77: the call was not taken and pclink was written. This is the
  only false-predicate case: one case of one form.
- roundtrip: r10 is `r1 & 0x3ffff` in 19 of 19 cases (the 32-bit reading fits 9: the values up to
  0x3ffff). 0x123 (E090) fits both.
- lapc-gap: r10 = 0x600D in 19 of 19, so `mov pclink` is seen by the next instruction's `lapc` at
  once; 0x5741 never.
- filler-control: three, eight and forty dependent increments land (3, 8, 40): the counter method
  works. control-e091: the known call and return of E091 works.
- initial (first instruction `mov r10, pclink`): three jobs after the roundtrip probe, whose last
  write was 0xffffffff (0x3ffff), read 0x3ffff in the scratch word and, in the 2048 pixels, 0x3ffff
  1920, 1920 and 1968 times, 0xeb3 64, 64 and 4 times and 0x98 64, 64 and 76 times (the first run by
  probe.py: scratch word 0x3ffff, 0x3ffff, 0x98).
- leftover (five writers of 0x12345, 0x2abcd, 0x155, 0x3ffff and 0, each followed by a reader and
  the last by a second reader): the writers read back their own value in all 2048 pixels; each job's
  scratch word is the expected one (11 of 11: the writer's own value, and the reader's the
  writer's), and a reader's pixels are the writer's value 1976, 1980, 1948, 1972 and 2000 times with
  0xeb3 in 72, 68, 64, 76 and 48 pixels (and 0x98 in 36 more for the third); the second reader the
  same as the reader before it (2000 and 48).
- pixels: 15 jobs (writer, reader, reader, five times, writers 0x12345, 0x2abcd, 0x155, 0x3ffff,
  0xabcd): the ten readers have 1932 to 2000 pixels at the writer's value (94.3 to 97.7 percent), 48
  to 68 at 0xeb3 and, in two readers, 52 and 44 at 0x98; the pixels that differ are aligned 2 x 2
  quads (x and x^1 in the rows y and y^1; for the two readers after the first writer, 16 and 12
  quads: 64 and 48 pixels), and the set of quads differs from job to job, the two readers after one
  writer sharing only some of them (24 pixels of the 64 and the 48, for 0x12345).

**What it shows.** [HW] pclink is 18 bits wide, so the 32-bit round trip of a firmware that saves
and restores it is exact for the indices it holds and drops anything above bit 17; `ba.savelink` is
the same as `br.savelink` (the index of the next instruction); a call whose predicate is false still
writes pclink (one case, `p0 ba.savelink`; whether `br.savelink`, other predicates or a placed
program do the same is not run), so a conditional call clobbers the link, at least in that form;
`mov pclink, rN; lapc` needs no gap and no `.nosched`. pclink is state of the hardware, not of the
job: a job that reads it before writing it reads what an earlier job (usually the last) left, for
about 96 percent of its instances, and the rest read values left by other code (0xeb3 and 0x98 are
not values any of these jobs wrote [infer]: the firmware's own use of pclink or of earlier jobs). A
task must write pclink before it reads it.

**What it does not show.** A false-predicate call in forms other than the one case above
(`br.savelink`, `!pN`, the other predicates, a placed program). Calls from an index of 255 or more
(the tool takes 256 words; the placed-program runs of E476 reach other indices by `lapc`, not by a
stored link read back). That the stale-link test is clean for `mov pclink, rN` after a `br.savelink`
call (the lapc-gap cases follow a call whose link is stale, which is the case that matters). What
wrote 0xeb3 and 0x98 (Q125). The value of pclink at the start of a firmware (EDM) task (Q124).

**Correction, 2026-11-08 (11.25).** The measurements above are unchanged; the false-predicate
statement is replaced by E491: a call that is not taken writes pclink in all 16 not-taken calls of a
fill table (`ba.savelink` and `br.savelink` under p0, p1, p2 and p3, `!p0` and `!p1`, presets 0x77,
0 and 0x3ffff, next instructions at indices 24, 48 and 84), in the 3 not-taken calls of a chain and
in 10 jobs of five programs placed at 0x10000 and 0x1ff000, and the model's reading that it does not
fits 0 of 29 cases; so 'one case of one form' no longer holds, though `!p2`, `!p3` (refused by the
assembler), `lapc`, a repeat and firmware tasks were not run. E500 ran the 15 jobs of
usse-pclink-pixels three more times: the deviant pixels are aligned 2 x 2 quads in every job of
every run and the 0xeb3 count is 64 in 29 of 40 reader jobs, so 'the set of quads differs from job
to job' holds literally (the sets are not identical) and the positions repeat in part from run to
run, but two reader jobs of one run also share 1 to 16 quads (E500), so the positions are neither
fixed nor independent across jobs or across runs, and no control compares jobs for dependence on the
job before; 'pixels ran once' is replaced by four runs.
