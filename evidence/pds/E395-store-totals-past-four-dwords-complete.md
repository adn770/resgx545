+++
id = "E395"
claim = "PDS stores with no rwfence totalling 11, 13, 14, 15 and 17 dwords complete the job (total 11 faulted in one of three runs, the others in none), totals of 1 dword (from ds1, and followed by nine nops) and of 10 (2 then 8) complete in all five runs each, and a total of 2 faults in every run, also with an rfence between the two stores; the kernel logged BIF status 0xd2000 at 0x10020 for the faults of total 2 and 0x1002e for the total-11 one"
unit = "pds"
method = "probes/pds/store-totals.toml on the laptop over the cable, linux fork b5a86838ae59 with the debug option on, the scratch mapped at 0x10000 (vm_low): pds_dump.s as a fill's secondary program with the case's stores to 0x10200, 0x10300 and 0x10400; totals 11, 13, 14, 15, 17 three runs, 1, 1 + nine nops and 10 five runs, 2 and 2 with an rfence two runs"
tiers = ["HW"]
date = "2026-11-03"
data = ["pds-store-totals"]
terms = []
+++
**Results.** 34 jobs: 5 faulted (the four total-2 jobs and one total-11), each logged once.
E144's one-run faults (one dword, one dword and nine nops, 2 then 8) did not recur in five runs.

**Not shown.** The rwfence cases and page 0 mapped (Q059).
