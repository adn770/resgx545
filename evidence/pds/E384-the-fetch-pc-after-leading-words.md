+++
id = "E384"
claim = "pc.0 read sixteen times back to back after 0, 1, 2, 3, 4 and 8 leading words of 0 ((p0) movs mr, ds0[0], ...) is the reading instruction's index plus 3, the leading words counted as instructions, or 1 below at a pair of reads, in all 480 reads of 30 jobs (five runs each): with 1 to 4 leading words one pair sits at instructions 24-25 (dwords 60-61) in 14 of 20 runs and one among the first four reads in 19; with none at 26-27 (two runs), 19-20 (two) or nowhere (one); with 8 at 35-36 in all five"
unit = "pds"
method = "probes/pds/fetch-pc-pad.toml on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: pds_dump_pad.s as a 64x32 fill's PDS secondary program (36 data dwords, --pds 36), the leading words, the sixteen copies of the template, then sixteen mov32 reads of pc.0 into the temporaries; five runs of each count. The table ran with the leading words written as .word 0 data lines; the run passes case 0's data size for every case, so they ran as instructions (the words saved with the run are the ones the table now spells as instructions)"
tiers = ["HW"]
date = "2026-11-03"
data = ["pds-fetch-pc-pad"]
terms = []
+++
**Results.** Read k (0-15) sits at instruction 16 + N + k for N leading words. The read minus
(16 + k), per read, one line per run:

| N | runs (each digit a read) |
|---|---|
| 0 | 3333333333223333 (2), 3332233333333333 (2), 3333333333333333 |
| 1 | 4334444334444444 (3), 4433444444444444 (2) |
| 2 | 5445554455555555 (5) |
| 3 | 6556655666666666 (3), 6556666666666666, 5566666666666666 |
| 4 | 7667667777777777 (3), 7667777777777777, 6777777777777776 |
| 8 | 11 at every read but 10 at reads 11 and 12 (5) |

So every read is its index + 3 or + 2, the leading words counted: `pc.0` = index + 3 holds.

The baseline varies. With no leading words the lag pair sat at instructions 26-27 in two of the
five runs, at 19-20 in two and nowhere in one, where E261's back-to-back programs put it at 26-27
in ten of twelve runs; this table did not repeat those programs, so the landed count stands and
the place of the pair is not fixed by the program alone.

**Not shown.** What places the lag pairs; whether the leading `(p0) movs mr` words ran or were
skipped (p0 is not set before them).
