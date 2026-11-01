+++
id = "E259"
claim = "Of the 281 bits the 27 PDS forms left unmapped, the 136 of the 17 data-operation forms (movs, movsa, mov16, mov64, mov128, the ALU group, mul, both abs, both not, both tstz, both tstn, shl, shr) and the 28 of load, store and the fences were flipped one at a time: each left the readback as the unflipped word did, except abs ds1[n]'s bit 15, which changed the value read, and mov128's bit 15, which changed the four dwords it writes"
unit = "pds"
method = "probes/pds/encoding-bits.toml and encoding-bits-memory.toml (written by tools/usse-asm/pds_bits.py) on the laptop, linux fork with the debug option on: each probe runs one form's base instruction in pds_bits.s as a 64x32 fill's PDS secondary program over sixteen marked temporaries and passes them to sa_dump.s; case 0 is the base word, each other case the word with one unmapped bit flipped as a raw .word; load, store and the fences with the scratch mapped at 0x10000 (vm_low); a case's readback (o0 and the changed scratch dwords) compared with case 0's by pds_bits.py eval; one run, 164 flipped cases and 20 bases"
tiers = ["HW"]
date = "2026-11-02"
data = ["pds-encoding-bits", "pds-encoding-bits-memory"]
terms = []
+++

**What runs.** Inputs A-H go to `ds0[48..55]` and I-P to `ds1[48..55]` (0x11111111, 0x22222222,
0x80000003, 0, 0x55555555, 0x66666666, 0x77777777, 0x0000ff01; 0x99999999, 0xaaaaaaaa, 0,
0x8000000b, 0xcccccccc, 0xdddddddd, 0xeeeeeeee, 0x00010203), so a changed source, destination
or predicate shows in one of the sixteen. The bases write `ds0[52]` (and its neighbours):

| form | base | unmapped bits | read |
|---|---|---|---|
| `movs`, `movsa` | `movs douta, ds0[50], ds1[10], ...` after the sixteen | 4 | none |
| `mov16` | `mov16 ds0[105], ds1[49].h` | 23:17 | none |
| `mov64` | `mov64 ds0[52], ds1[48]` | 23:17, 9:8, 1:0 | none |
| `mov128` | `mov128 ds[52], ds[4]` | 23:15, 9, 7, 1:0 | 15 |
| ALU | `add ds0[52], ds0[49], ds1[49]` | 16, 9:7 | none |
| `mul` | `mul ds0[52], ds0[49].l, ds1[49].l` | 8:7 | none |
| `abs` ds1 | `alum signed`, `abs ds0[52], ds1[3]` | 23:15, 9, 7 | 15 |
| `abs` | `alum signed`, `abs ds0[52], ds0[50]` | 16:9, 7 | none |
| `not` ds1, `not` | `not ds0[52], ds1[3]`, `not ds0[52], ds0[50]` | 23:16, 9, 7; 16:9, 7 | none |
| `tstz`, `tstn` (4) | p0-p2 false, the test sets p0, then `(pN) mov32` | 23:16, 9, 7:3 (`ds1[n]`); 16:9, 7:3 | none |
| `shl`, `shr` | `shl ds0[52], ds0[49], 4` | 15, 7 | none |
| `load` | `load 0x10100, ds0[52-53]`, `rfence` | 23 | none |
| `store` | `store 0x10100, ds1[48-55]` | 23 | none |
| fences | `load 0x10100, ds0[52-53]`, then `rfence` | 26:1 | none |

The tests' unmapped bits are 23:16, 9 and 7:3 in the `ds1[n]` forms and 16:9 and 7:3 in the
others. Every base gave what its operation predicts (the load base `ds0[52]` = 0xd0000040, the
store base the eight dwords at scratch dword 64). Every job completed. The two bits read:

- `abs ds0[52], ds1[3]` with bit 15: `ds0[52]` = 0x07000305 instead of 0x55555556 (abs of J), the
  stale content of a read-only row past the data segment; E261 shows the bit is the sixth bit of
  the `ds1` index.
- `mov128 ds[52], ds[4]` with bit 15: `ds0[52]`, `ds0[53]`, `ds1[52]`, `ds1[53]` = 0x77777777,
  0x0000ff01, 0x77777777, 0x0000ff01 instead of C, D, K, L; E261 maps it.

`mov32`'s unused bits (23:17, 8, 0) and `alum`'s (23:1) were not run again: the earlier records
of `pds-moves-mov32-spare` and `pds-alu-alum-spare` measured them.
