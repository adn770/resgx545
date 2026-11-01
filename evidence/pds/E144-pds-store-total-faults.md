+++
id = "E144"
claim = "A PDS program with stores and no rwfence faults when its stores total 2, 3 or 4 dwords, however they are split, after every dword has landed and the program has reached its end (20 programs, in both runs), and completes when they total 5 to 9, 12, 16 or 18 (16 programs, in both runs) and in 12 of the 15 programs that total 1 or 10; the other three fault in one run only (two of total 1 in the follow-up run, one of 2 + 8 in the first); a job with rwfence run right after a faulted job faults whether or not it has a store (11 of 11, in both runs)"
unit = "pds"
method = "probes pds-memory-mem to pds-memory-mem6 of probes/pds/memory.toml on the laptop, linux fork with the debug option on and the kernel's vm_low option: the scratch mapped a second time at 0x10000, the fill's secondary program pds_dump.s runs stores of 1 to 8 dwords from ds0[48-55] or ds1[48-55] at several offsets and pages, split in up to five stores, then the shader sa_dump.s stores the registers; each case a fill of its own, in table order; two runs (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-memory", "pds-memory-followup"]
terms = []
+++

**What runs.** A store takes 1 to 8 dwords of a bank from the address in its word; the table varies
the dword count, the offset (dword-aligned, 8-byte and 16-byte aligned), the page (the first,
the second at dword 1024 and the fifth at dword 4096 from 0x10000) and the split of a total over
several stores. A job that faults loses its context and the table goes on with the next case. A
table's first case follows the table's render check, which completed; "right after a faulted job"
below means the job before it in the same table faulted.

**Results.** Programs with stores and no `rwfence` (51 of the 89 cases of the table), by total of
dwords stored:

| total | stores | first run | follow-up run |
|---|---|---|---|
| 2 | one of 2 (8 programs: from ds0 and from ds1, at dwords 128, 144, 193, 194, 196, 1032, 440 and 4096); 1 + 1 (adjacent; on two pages in either order; with an `rfence` between) | 12 fault | 12 fault |
| 3 | one of 3; 2 + 1 | 2 fault | 2 fault |
| 4 | one of 4 (from ds0 and from ds1, at several offsets, and a repeat) | 6 fault | 6 fault |
| 1 | one of 1 from ds0; one of 1 with no fence; one of 1 and `rfence` (2 programs); a store then a load of its address (with neither fence, with an `rfence` before the load, after it, and both; 4 programs); a load then a store of 1 (with and without `rfence`; 2 programs) | 10 complete | 10 complete |
| 1 | one of 1 from ds1; one of 1 followed by nine `nop`s | 2 complete | 2 fault |
| 5 to 9 | one of 5, 6 or 7; 4 + 1; five of 1; one of 8 (from ds0 and ds1, 4 programs); 2 + 2 + 2 + 2; 4 + 4; 8 + 1; 1 + 8 | 13 complete | 13 complete |
| 10 | 8 + 2; 8 + 1 + 1 | 2 complete | 2 complete |
| 10 | 2 + 8 | fault | completes |
| 12 to 18 | 8 + 4; 8 + 8; 8 + 8 + 2 | 3 complete | 3 complete |

- In every one of the 20 programs of total 2 to 4, and in the three that fault in one run only,
  every dword landed in the scratch and the registers were stored at the end of the job, so the
  program ran to its end before the job failed. The 8 + 8 + 2 program, which completes, lands all
  18 dwords (the readback shows 32 and counts 2 more).
- The page and the alignment do not matter: 2 dwords fault at every offset and page tried, and 1 + 1
  on two pages faults as it does on one.
- The total decides, not a single store or the count of stores: 1 + 1 + 1 + 1 + 1 (5) and 2 + 2
  + 2 + 2 (8) complete where 1 + 1 (2) and 2 + 1 (3) fault. The totals 9, 12, 16 and 18 complete,
  so it is not the total modulo 8 either. Total 1 and total 10 are the exceptions: three of the 15
  programs of those totals fault in one run each, so for them the total does not decide.
- The programs that fault in one run only: `store` of 1 dword from ds1 and `store` of 1 dword
  followed by nine `nop`s fault in the follow-up run and complete in the first; `store` 2 and then
  `store` 8 faults in the first run and completes in the follow-up. Their completing neighbours
  (a store of 1 from ds0; 8 + 2) are the same in both runs.
- Apart from these three, the two runs give the same outcome and the same scratch contents in the
  other 86 cases of the table.

**After a fault.** The jobs of pds-memory-mem6 in order; the two runs give the same outcome for
every job:

| job | outcome |
|---|---|
| `store` 1, `rwfence` | faults |
| `rwfence` twice (2 jobs) | fault, fault |
| `store` 1, no fence | completes |
| `rwfence` alone | completes |
| `store` 8, `rwfence` | faults |
| `load`, `rwfence`, `store` | faults |
| `store` 1, `rfence` | completes |
| `rwfence` twice | completes |
| `store` 2 | faults |
| `rwfence` twice | faults |

- A job with `rwfence` that ran right after a faulted job faulted, in both runs: 11 of 11. Five
  have a store before the `rwfence`: the two stores of 1 dword and `rwfence` and a load of
  pds-memory-mem, the repeat of store, `rwfence`, load of pds-memory-mem2, and the store of 8, the
  store of 1 with eight `nop`s and the store of 1 with `rfence`, each followed by `rwfence`, of
  pds-memory-mem3. Six have none: `load`, `rwfence`, `store` and the `rwfence` pair at the end of
  pds-memory-mem3, and in pds-memory-mem6 the `rwfence` pair after the first fault, the pair after
  that, `load`, `rwfence`, `store` after the store of 8, and the pair after the store of 2.
- A program with no `rwfence` that ran right after a faulted job completed unless its stores total
  2 to 4 dwords: 13 such programs completed in the first run and 12 in the follow-up run, among
  them the store of 1 with no fence and the store of 1 with `rfence` of pds-memory-mem6.
- The same kinds of program complete after completed jobs, in both runs: `rwfence` alone, `rfence`
  then `rwfence`, `rwfence` then `rfence`, two `rwfence`s adjacent or eight `nop`s apart,
  `rwfence` then a store (5 programs of pds-memory-mem4), and the reruns of `rwfence` twice, of
  `load`, `rwfence`, `store`, and of a load through `rwfence` into a mov (3 programs of
  pds-memory-mem5). The `load`, `rwfence`, `store` program and the `rwfence` pair had faulted in
  pds-memory-mem3, run right after the faulted store and `rwfence` jobs, in both runs.
- After the last two faults of pds-memory-mem3, the first program of pds-memory-mem4 (a store of 8
  and a store of 1) completed, in both runs.

**Not shown.** Where the faults land is in E145. Why the totals 2 to 4 fault is open. What makes
the three one-run faults is not shown: the same program completed in the other run after the same
earlier jobs, so the state a faulted job leaves does not explain them. Two runs.
