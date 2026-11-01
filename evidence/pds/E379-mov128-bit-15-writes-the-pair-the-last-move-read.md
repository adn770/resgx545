+++
id = "E379"
claim = "mov128 with bit 15 writes to both halves of its destination row the ds0 pair that the last mov32 or movs read from a data row (rows 0-23): row 4's pair in E261 is the one the template's last mov32 from a data row read (ds0[9]); with each of bits 23:16, 9, 7, 1 and 0 also set, bits 23:16 and 1:0 together, source rows 0, 4 and 24 and destination ds[48] the same pair is written; a movs to mr or to douta from ds0[2] or ds0[6] names that pair instead, as does a mov32 from ds0[2], while a movs from the temporary pair ds0[50], ds0[51], a not of a temporary (ds0[48-55] or ds1[48-55]), a mov32 from ds1[9] and a mov64 from mr01 leave it; three runs of every case, and the same with another set of markers"
unit = "pds"
method = "probes/pds/mov128-bit15.toml (written by tools/usse-asm/pds_bits.py table --mov128) on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: pds_bits.s as a 64x32 fill's PDS secondary program, every input dword its own marker (ds0[n] 0xA00000nn, ds1[n] 0xB00000nn; a second probe 0xC0000n0n and 0xE0000n0n), the sixteen temporaries complemented first, then the case's lines and the mov128 word as a raw .word; the sixteen temporaries passed to the task and stored; pds_bits.locate names the dword each value came from; 21, 5 and 9 cases, each three times"
tiers = ["HW"]
date = "2026-11-03"
data = ["pds-mov128-bit15"]
terms = ["PDS_MOV128.LASTPAIR"]
+++
**Results.** Every case gave the same readback in its three runs (105 jobs).

| case (mov128 ds[52], ds[4] with bit 15, unless said) | ds[52] row read back |
|---|---|
| control, bit 15 clear | ds0[4], ds0[5], ds1[4], ds1[5] |
| bit 15 alone; with each of bits 16-23, 9, 7, 1, 0; with 23:16; with 1:0 | ds0[8], ds0[9], ds0[8], ds0[9] |
| source rows 0, 4 and 24; destination ds[48] (into ds[48]) | ds0[8], ds0[9] in both halves |
| another set of markers (bit 15 alone, bit 16, row 24, ds[48]) | that set's ds0[8], ds0[9] |
| `movs mr, ds0[6], ds0[7], ds1[6], ds1[7]` first | ds0[6], ds0[7] twice |
| `movs mr, ds0[2], ds0[3], ds1[6], ds1[7]` first | ds0[2], ds0[3] twice |
| `movs douta, ds0[6], ...` first (no mr write) | ds0[6], ds0[7] twice |
| `movs mr` from ds0[2-3], then `movs douta` from ds0[6] | ds0[6], ds0[7] twice |
| `movs mr` from ds0[2-3], then `mov64 ds0[48], mr01` (reads 0, 0) | ds0[2], ds0[3] twice |
| `movs mr` from ds0[50-51] (temporaries), then `not ds0[50], ds0[50]` | ds0[8], ds0[9] twice |
| `movs mr` from ds0[50-51], then `mov32 ds0[50], ds0[2]` | ds0[2], ds0[3] twice |
| `movs mr` from ds0[2-3], bit 15 clear | ds0[4], ds0[5], ds1[4], ds1[5] |

Before the case's lines the template copies ds0[2..9] and ds1[2..9] to the temporaries with
sixteen `mov32`s, the last from a `ds0` data row being `mov32 ds0[55], ds0[9]`, then complements
the sixteen temporaries with `not`. So the pair is the last one a `mov32` or `movs` read from a
data row, and it does not change with the reads of temporaries, of `ds1`, of `mr01`, nor with the
`not`s. The data rows are read-only (pds_isa 8.1), so the pair named and its value are one.

A side reading: `not ds0[6], ds0[6]` left ds0[6] as it was and wrote ds0[54] (the temporary of the
same row), three runs, as a `mov16` into a read-only row does (pds_isa 8.7).

**Not shown.** Which other instructions or rows set or keep the pair: a `mov32` from `ds0[3]` to
`ds0[8]` or from `ds1` rows other than 9 (the template ran them, but each was followed by a later
read that decides the result), a `movs` from other pairs, `movsa`, a `not` of a data row, `mov64`
from `mr23`, `mov16`, the ALU, `mul`, the tests, `load`/`store`, a plain `mov128`; and what the pair
holds at the start of a program before any read. The simulator stops there.
