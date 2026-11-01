+++
id = "E127"
claim = "In a fill's PDS secondary program, all six load and store cases (loads at 0, 0x40, 0x1000 and 0x10000, a store then a load with and without a fence) fault the job, movs to mr, tim, ir0, slc, douts and a movsa on douta complete it and write nothing that the attributes read back show (the ir0 case reads the tile position), and movs to doutc faults it"
unit = "pds"
method = "probes pds-load-store-addressing and pds-load-store-ports of probes/pds/load-store.toml (pds_dump.s: the operation under test runs in the fill's secondary PDS program, which then passes ds0[48-55] and ds1[48-55] to the shader with douta, and the shader stores them to scratch) on the laptop, linux fork with the debug option on: 64x32 fill, one run of each case, fresh context each"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-load-store"]
terms = ["CR_BIF_INT_STAT", "PORT.DOUTU"]
+++

**What runs.** The 64x32 fill's secondary PDS program copies 16 input dwords into temporaries,
runs the operation under test, passes the 16 temporaries on with `douta` and ends with `doutu`.
The shader stores them to the scratch buffer, so the buffer shows what the temporaries held.

The addressing probe has six cases: `load` of four dwords with the operand 0, 0x40, 0x1000 and
0x10000 (each followed by four `mov32` of the loaded temporaries), a `store` of a temporary to
0x100 then `rwfence` then `load` from 0x100, and the same without the fence. The ports probe has
seven: `movs` to `mr` (then `mov64` of `mr01` and `mr23` into temporaries that held 0), to `tim`
(then `mov32` of `ir1.1`), to `ir0` (then `mov32` of `ir0.0`), to `slc`, to `doutc` and to
`douts`, and a `movsa` on `douta`. The inputs were two marker dwords 0x0c0ffee0 and 0x0c0ffee1
and the same as 0x0c0ffee2 and 0x0c0ffee3 in the second bank, zeros elsewhere.

**Results.**

- All six addressing cases fail with "job faulted, context lost (Input/output error)"; the scratch
  buffer is unchanged in each. The cases differ in the operand, in whether a store came first and in
  the fence, and none of that changes the outcome. The data holds no fault address and no value of
  `CR_BIF_INT_STAT`, so the page or the requestor of the fault is not recorded here.
- `movs` to `doutc` faults the job in the same way.
- The other six port cases complete (`o0` written on 2048 of 2048 pixels) and the markers come out
  where they were put (0x0c0ffee0 and 0x0c0ffee1 in the first two dwords, 0x0c0ffee2 and 0x0c0ffee3
  in dwords 8 and 9). The `mr` case reads 0 from `mr01` and `mr23`, but the destination temporaries
  held 0 already, so a read of 0 and no write look alike. The `tim` case reads 0 from `ir1.1`, and
  `ir1` reads 0 in a fill with or without a write to `tim` (E128), so it says nothing about `tim`.
  The `ir0` case reads 0x403 from `ir0.0`, a tile position (E128) and not the 0x0c0ffee0 that was
  written. The `slc`, `douts` and `movsa` cases leave all 16 dwords as the inputs were.

**Not shown.** Why the loads and stores fault, and at which address, is not in this data, which has
only that the job fails. This table maps nothing in the first MiB of the PDS's address space
(the table needs no vm_low option). E143, E144 and E145 run loads and stores with the scratch
mapped at 0x10000: loads there complete, a store of 1 dword and of 5 or more completes in most
programs, and `rwfence` after a store faults, with the fault values of E145. They are read here
only as the setting of this table's cases, which address 0, 0x40, 0x1000 and 0x10000 unmapped and
end a store with `rwfence`; the cases here were not rerun with a mapping. Whether the fault is the
load, the store or the program after it is not separated, since each case is one job. `doutc`
could fault for a reason of its own. `tim` was only written, not read, in the ports probe; a read of
`tim` after a `movs` is in E128. One run of each case.
