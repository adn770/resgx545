+++
id = "E145"
claim = "The kernel logs of the two runs of pds/memory hold 37 (first run) and 38 (follow-up run) BIF fault lines, one for each PDS case that faulted, in order; the status is 0xd2000 for the store faults (21 and 22) and 0x92000 for the 16 rwfence faults of each run; the 36 cases that faulted in both runs have the same status, address and SB in both, and the same CID in 32; the value (CR_BIF_FAULT) splits into the fields CID (3:0) and SB (8:4) as follows: SB is 2 or 3 in all 75, with 2 for rwfence after a store and 3 for rwfence with no store before it, and CID is 0 in all 16 faults under one page directory in each run"
unit = "pds"
method = "the kernel logs kept by the runner for the two runs of probes/pds/memory.toml on the laptop, linux fork with the debug option on (pds/memory/kernel.log and followup/pds/memory/kernel.log): each 'BIF fault <status> at <value> (PD <directory>) stalls job N, recovering' line, tied to the failing cases of the same run's reports by order; the value split with the field positions of the terms CR_BIF_FAULT.CID and CR_BIF_FAULT.SB"
tiers = ["HW", "DDK"]
date = "2026-11-01"
data = ["pds-memory", "pds-memory-followup"]
terms = ["CR_BIF_FAULT", "CR_BIF_FAULT.CID", "CR_BIF_FAULT.SB"]
+++

**What runs.** The cases of E143 and E144, in both runs. Each fault the driver sees is logged as a
line with the status, the value of the fault register and the page directory of the context, then
the job number, and after it the reset ("SGX reset: BIF_FAULT 0x0 ...", the register read as 0
after the reset). The first run's log holds 37 such lines and its reports list 37 failing cases;
the follow-up run's log holds 38 and its reports 38. Taken in order they pair one to one, and the
pairing is exact: in each run the job number of every line is a constant (80653 in the first run,
80774 in the follow-up run) plus the position of the failing case in the table order of the 89
cases plus 2 for each table before its own (the render check before and after a table). The log
does not name the case, so the tie is by order and by these job numbers. The fields are read with
the positions of the terms `CR_BIF_FAULT.CID` (bits 3:0) and `CR_BIF_FAULT.SB` (bits 8:4); the
address is bits 31:12. A case with registers stored at its end is a store fault; one without is an
`rwfence` fault (E143), and the status agrees with that in every line of both runs.

**Results.** Counts are first run, then follow-up run.

Status and address.

- Status 0xd2000: the store faults (21 and 22: the 20 programs that fault in both runs, E144, and
  the one or two that fault in one run only). Status 0x92000: the 16 `rwfence` faults in each run.
- Store faults: address bits 31:12 are 0x10 in 18 and 19 faults, 0x11 in 2 and 0x14 in 1. These
  are the pages of the first store of the program: 0x10 for stores in the first page of the mapping
  at 0x10000, 0x11 for the store at dword 1024 first (pds-memory-mem4 cases 5 and 6, stores at
  dwords 1024 and 1032) and 0x14 for the store at dword 4096. In the 1 + 1 program that stores at
  dword 288 and then at dword 1024 the address is the first page (0x10), and in the one that stores
  at 1024 and then at 288 it is 0x11.
- `rwfence` faults: address bits 31:12 are 0 in all 16 of each run (page 0).
- Bits 11:9 are 0 in all 75 values.

SB (bits 8:4) is 2 or 3 in all 75, by the program that faulted:

| SB | store faults (first run / follow-up run) | `rwfence` faults (16 in each run) |
|---|---|---|
| 2 | totals of 2 dwords: one store of 2, and 1 + 1 (12 / 12 faults); 2 + 8 (1 / 0) | `rwfence` after a store in the same program (10 faults) |
| 3 | totals of 3 or 4 dwords: 3, 4 and 2 + 1 (8 / 8 faults); one store of 1, and 1 and nine `nop`s (0 / 2) | `rwfence` in a program with no store before it: the pairs of `rwfence`s and `load`, `rwfence`, `store` (6 faults) |

The 6 SB 3 `rwfence` faults all ran right after faulted jobs. The programs without a store before
the `rwfence` complete when they run after completed jobs (E144), so these runs do not separate
"right after a fault" from "no store before it". The `rwfence` programs with a store before it
have SB 2 whether they ran after a fault (five of pds-memory-mem and -mem2 and -mem3) or not (the
other five). The SB of the 36 cases that faulted in both runs is the same in both.

CID (bits 3:0):

- First run: 0 (16 faults), 1 (11), 2 (4), 7 (2), 11 (2), 3 and 4 (one each). Follow-up run: 0
  (16), 1 (11), 2 (4), 3 (2), 4, 7, 8, 11 and 15 (one each).
- There are 22 page directories among the 37 lines of the first run and 23 among the 38 of the
  follow-up run. One directory, 0x35ae9000, appears 16 times in each, in store faults only, and CID
  is 0 in all 16 of each run; the other directories (21 and 22) each appear once. No directory but
  0x35ae9000 appears in both runs. CID 0 occurs only under that directory.
- Of the 36 cases that faulted in both runs, 14 have the repeating directory in both, 2 have it in
  one run only (pds-memory-mem2 cases 1 and 5, where the other run has another directory, in one
  case the directory 0x0 with CID 15), and the other 20 have a different directory in each run.
  The CID is the same in 32 of the 36 and differs in pds-memory-mem2 cases 1 and 5,
  pds-memory-mem5 case 1 and pds-memory-mem6 case 0.
- CID 1 is the CID of 11 `rwfence` faults in each run, the 11 that ran right after a faulted job
  (the same programs in both runs, each under its own directory); the five `rwfence` faults that
  ran after a completed job or first in their table have CID 7, 2, 2, 3 and 3 in the follow-up
  run and 7, 2, 2, 11 and 3 in the first.
- Store faults have CID 0 (16), 2 (2), 4, 7 and 11 in the first run, and 0 (16), 2 (2), 4, 8, 11
  and 15 in the follow-up run.

**Reading.** SB separates the `rwfence` faults by whether a store came before the fence, in 32 of
32, and the store faults by the program that failed with no simple rule in the total: 2 dwords give
2 and 3 or 4 dwords give 3, but a store of 1 dword (two programs, follow-up run) gives 3 and 2 + 8
(one, first run) gives 2. CID is a context number that differs between jobs' directories; for the
`rwfence` faults it is 1 when the job before had faulted. Both are readings of these values with the
field positions of the terms.

**Not shown.** What SB encodes (the kind or the size of the request is a guess), and what makes the
value in CID: that it is a slot the kernel picks for the context is not shown, since the one
directory that repeats has CID 0 and eleven different directories share CID 1. Why the `rwfence`
faults after a fault have CID 1 is not tried apart from this correlation. The faults that happen
in one run only (E144) are 3 of the 75 lines.
