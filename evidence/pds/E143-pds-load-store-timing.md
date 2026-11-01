+++
id = "E143"
claim = "With the scratch mapped in the first MiB, where the PDS reaches, a PDS load's dwords reach its registers only at the next rfence or rwfence (never by the end of the program, and not after four nops), a store takes the register's value at the time it runs, a load after a store reads the stored value, and stores of 8 dwords complete; rwfence after a store faults the job in 10 of 10 programs of the table that have one, in both runs, 5 of them after a completed job or first in their table and 5 right after a faulted job"
unit = "pds"
method = "probes pds-memory-mem, pds-memory-mem2, pds-memory-mem3, pds-memory-mem4, pds-memory-mem5 and pds-memory-mem6 of probes/pds/memory.toml on the laptop, linux fork with the debug option on and the kernel's vm_low option: the 64 KiB scratch is mapped a second time at 0x10000 (the table's low), so the PDS address 0x10000 + 4k is scratch dword k, which the shader sa_dump.s overwrites with the registers at the end; the fill's secondary program pds_dump.s runs loads, stores and fences on ds0[48-55] and ds1[48-55]; two runs, the cases in table order, one job each (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-memory", "pds-memory-followup"]
terms = []
+++

**What runs.** Each case is a fill of its own. The sixteen inputs 0x11111111 to 0xffffffff and
0x11111110 are in ds0[48-55] and ds1[48-55]. Scratch dword 64 (PDS address 0x10100; the table's
labels count dwords from 0x10000) starts as 0xd0000040, so a load from it is told from the
inputs. The shader stores the registers to scratch dwords 0 to 15 at the end of the job; a store
lands elsewhere. In the tables, "after a completed job" means the job before it in the same table
completed; the first case of a table has the table's render check before it, which completed.

**Results.**

**Loads.**

- A load of 1, 4 or 8 dwords with no fence after it: the registers are the inputs, unchanged by the
  end of the job.
- `load` to ds0[50] then `mov32 ds0[51], ds0[50]`: both read 0x33333333, the old value. With
  `rfence` between them, or `rwfence`, both read 0xd0000040. With four `nop`s between, the old
  value.
- A load that is followed by a fence late in the program lands there: `store`, `load` it to
  ds0[48], `rfence` gives ds0[48] = 0x99999999; two loads then `rfence` give 0xd0000040 and
  0xd0000041 in ds0[48] and ds0[49].

**Stores.**

- `load` to ds0[48] then `store ds0[48]`, no fence: the stored dword is 0x11111111, the old
  register. With `rfence` between them it is 0xd0000040, and the register holds that too.
- A store of 8 dwords lands every dword and the job completes in all 4 programs that have one (from
  ds0 and from ds1, at four different offsets), as do the stores of 5, 6 and 7 dwords; every
  dword read back is the register's. A store of 1 dword with no `rwfence` completes in 10 of the
  12 programs that have one (E144 has the two that fault in the follow-up run only).
- `store ds1[48]` then `load` it to ds0[48] and `rfence`: ds0[48] = 0x99999999 and the stored
  dword is 0x99999999, with or without an `rfence` between the store and the load (2 programs).
  With no fence after the load, the register is not changed whether or not an `rfence` is between
  the store and the load, and the stored dword is 0x99999999 (2 programs).

**`rwfence` after a store.**

- Every program with a store and then an `rwfence` faults the job: 10 of 10, in both runs. They are
  a store of 1 dword and `rwfence` (from ds1; from ds0; and as the first case of its own table),
  the same with a load after the `rwfence` (twice, the second a repeat), two stores of 1 dword to
  the same address (ds1[48] and ds1[49]) and `rwfence` and a load, a store of 1 dword
  with eight `nop`s before the `rwfence`, a store of 1 dword with `rfence` and then `rwfence`, and
  a store of 8 dwords and `rwfence` (twice). In each the store's dwords are in the scratch (the
  two stores to one address leave 0x99999999, the first dword's value), but the job does not
  reach the end of the program: the registers are not stored.
- Five of the 10 ran after a completed job or first in their table (the store of 1 from ds1,
  `rwfence` and a load; the store of 1 and `rwfence` from ds1 and from ds0; the one that opens its
  table; and a store of 8 and `rwfence`), and fault. The other five ran right after a faulted job
  (E144 shows that a job with `rwfence` after a faulted job faults whether or not it has a store),
  so for them the table does not separate the effect of the store from that of the earlier fault.
- `rwfence` with no store before it completes when the job before it in the table completed
  (11 programs of these tables, and the two of E142, in both runs): alone (twice), after `rfence`,
  before `rfence`, twice in a row (twice), with eight `nop`s between two, followed by a store;
  `load`, `rwfence`, `mov32` hands on the loaded value like `rfence` does (twice); `load`,
  `rwfence`, `store` stores that value (0xd0000040, once). It faults, in both runs, when the job
  before it in the table faulted (6 programs, listed in E144).

**The two runs.** The follow-up run gives the same outcome and the same scratch contents (the
registers stored at the end and the stored dwords) for every load, store and fence case above,
and its 10 programs of a store and then `rwfence` fault again, without reaching the end of the
program. Three programs of the table differ between the runs, all stores without `rwfence`; they
are in E144.

**Not shown.** Where the faults land is in E145, not here. Why stores of 2 to 4 dwords fault is
E144. A program that loads and then stores the same address was not tried. The first run's data
does not separate the cause of an `rwfence` fault with a store before it from the cause of one
after a fault in 5 of the 10 programs; the 5 that ran after a completed job do.
