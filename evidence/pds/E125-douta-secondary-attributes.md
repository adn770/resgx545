+++
id = "E125"
claim = "From a fill's secondary PDS program, douta writes its first word to the secondary attribute named by bits 19:8 of its second word, and all sixteen words reached sa0 to sa15 with the background object's secondary attribute size at 4, 1 and 0 rows; attributes a job does not write read what earlier jobs left, and which earlier job differs between the first and the follow-up run; from the triangle's primary program the markers did not arrive, and markers A read the same sixteen values in both runs"
unit = "pds"
method = "probes pds-douta-secattr-rows-0, -secattr-rows-4, -persist-across-jobs and -primary of probes/pds/douta.toml (douta_words.s: sixteen douta, each with a value and a control word from the case, then doutu of the shader sa_dump.s, which stores sa0 to sa15 to scratch) and the douta readback of probes/pds/alu.toml (pds-alu-readback) on the laptop, linux fork with the debug option on: 64x32 fill with the secondary attribute size poked through bg:1 (the background object's dword 1, bits 24:18) for the rows probes, 64x64 triangle with the state block word 4 at 0x130004 for the primary probe, one run of each case, fresh context each; the douta tables ran twice (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-douta", "pds-douta-followup", "pds-alu"]
terms = []
+++

**What runs.** Each case gives sixteen values (a marker set: A is 0xa0a00000 + k, B 0xb1b10000 + k,
C 0xc2c20000 + k, D 0xd3d30000 + k, E 0xe4e40000 + k for attribute k) and sixteen control words, the
k-th being k << 8 unless the case repeats an attribute; `douta` k writes value k to the attribute
named by bits 19:8 of control word k. The task started afterwards stores `sa0` to `sa15`. The
rows probes poke `bg:1` to 0x130000 (bits 24:18 = 4 rows), 0x70000 (1 row) or 0x30000 (0 rows);
each probe runs its cases in order, one job each. The persist probe runs three jobs: A writes all
16 attributes, B (marker D) writes `sa0` to `sa7` twice over (values 0 to 7, then again 0 to 7 in
the second half), C (marker E) writes `sa8` to `sa11` four times over.

**Results.** Scratch dwords 0 to 15 are the sixteen attributes. In every fill case of both runs the
2048 pixels are all 0x0da7a000, except in the 0 rows case below.

- Rows 0: case 1 (0 rows, markers B) reads all sixteen B markers in order, in both runs; the
  preceding job (4 rows, markers A) read all sixteen A markers. In the 0 rows case 2016 of the 2048
  pixels read back are 0x0da7a000 and 32 are other values, among them B markers (2 pixels each of
  0xb1b10000, 0xb1b10001 and 0xb1b10004); the same in both runs.
- Rows 4: 4 rows with markers A and with markers B read all sixteen markers of each; 1 row with
  markers C also reads all sixteen C markers, not only `sa0` to `sa3`. Same in both runs.
- Persist, both runs: job A reads the sixteen A markers. Job B reads D markers 0 to 7 in `sa0` to
  `sa7` and 0xa0a00008 to 0xa0a0000f (job A's) in `sa8` to `sa15`. Job C reads E markers 8 to 11
  in `sa8` to `sa11`, job A's 0xa0a0000c to 0xa0a0000f in `sa12` to `sa15`, and 0x00000006 in
  `sa0`. The two runs differ in `sa1` to `sa7` of job C: the first run reads job A's markers 1 to 7
  (0xa0a00001 to 0xa0a00007), the follow-up run reads job B's D markers 1 to 5 in `sa1` to `sa5`,
  then 0x00000000 in `sa6` and 0x3f800000 in `sa7`.
- Primary program of the triangle (state word 4 at 0x130004): in both runs markers A read
  0x00000002, 0x22222222, 0x33333333, ... 0xeeeeeeee, 0xffffffff and 0x11111110 in `sa0` to
  `sa15`, none a marker. Markers B read in the follow-up run the same sixteen values as markers A;
  in the first run they read 0x00000002 in `sa0` and fifteen other values, none a marker and none
  those of markers A (0x14000200, 0x0100d975, 0x04000004, 0x00130004, 0x24000080, four times
  0x42000000, twice 0x3f000000, 0, 0x00043000, 0x3727c5ac, 0x01555620). In each case the 4096
  pixels are 3034 of 0xff203040 and 1062 of 0x0da7a000 (the triangle).
- The values 0x22222222 to 0xffffffff and 0x11111110 in `sa1` to `sa15` of markers A are, attribute
  for attribute, the inputs B to P that the programs of `pds-memory` pass to `sa1` to `sa15` with
  `douta` (E142), and `sa0` reads 0x00000002 where that table has the input A, 0x11111111.
- The 52 probes of `pds-alu` pass sixteen words with `douta` the same way (control words
  0x000 to 0xf00); `pds-alu-readback` reads the eight distinct words 0x11111111 to 0x88888888 in
  dwords 0 to 7 and again in 8 to 15, and a set of edge values (0, 0xffffffff, 0x80000000,
  0x7fffffff, 1, 0xfffffffe, 0xffff, 0xffff0000) likewise, in both runs.

**Not shown.** The rows probes did not leave a case with fewer than sixteen words arriving, so
what the secondary attribute size limits is not shown, and bits 24:18 of `bg:1` were poked, not
read back. Whether the size matters for tasks that read more than sixteen attributes is not tried.
The persist probe shows that values are kept from earlier jobs, not which job's values a given
attribute takes: job C's `sa1` to `sa7` differ between the two runs, and `sa0` of job C (0x6) is
no value any job of the probe wrote. The primary program writes no marker the task can read, but
why the task reads the memory table's inputs and not the markers the earlier probes of this table
left in the same attributes is not shown; the match of values is not a trace of which job left
them, and the first run's markers B values are not explained. One run of each case in each run.
