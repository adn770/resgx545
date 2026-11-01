+++
id = "E261"
claim = "pc.0 reads the reading instruction's index plus 3, or plus 2 or 1, never more nor less, in 399 reads over 27 programs: back to back it reads less at instructions 26-27 in ten of twelve runs, whatever the nops before, and at 19-20 in two; abs's ds1[n] takes n from bits 15:10; mov128's source row reaches 31, rows 24-31 the temporaries, and with bit 15 set mov128 writes ds0[8], ds0[9] to both halves of its destination whatever its source row, and with swap at row 2; nop's bit 2 does not change the fetch pc"
unit = "pds"
method = "probes/pds/fetch-pc.toml, encoding-bits-followup.toml and encoding-bits-mov128.toml on the laptop, linux fork with the debug option on, as fills' PDS secondary programs (pds_dump.s, pds_bits.s): 16 mov32 reads of pc.0 a program, each into its own temporary, after 0-3 nops, with 0-14 nops between reads, after one instruction of each kind, across taken branches and a call, and after loads with nops or fences (the scratch at 0x10000), each case three times; abs ds0[52], ds1[n] at n 16, 17, 19, 20 with and without bit 15; mov128 with bit 15 at source rows 0-31 into ds[52] and at destinations ds[48], ds[50], ds[52], ds[54] with rows 2 and 31, row 2 also with swap, the temporaries complemented first so that a read of them shows; nop with and without bit 2, five times each; one run of each table"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = [
    "pds-fetch-pc", "pds-encoding-bits-followup", "pds-encoding-bits-mov128",
    "vectors-pds-knowledge",
]
terms = []
+++

**The fetch pc.** The reads sit at instruction 16 onward (the template's sixteen copies first).

- Sixteen reads back to back, after 0, 1, 2 or 3 `nop`s, three runs each (192 reads): index + 3,
  except two consecutive reads at index + 2: at instructions 26 and 27 in ten of the twelve runs,
  whatever the `nop`s before, and at 19 and 20 in two (one with one `nop`, one with three).
- Reads with 0 to 14 `nop`s between them, rising and falling, three runs each (96 reads): index +
  3 except at up to four reads a run at + 2, and the first read at + 1 or + 2; a read k `nop`s
  after another reads k + 1 more, so a `nop` takes one slot.
- One instruction of each kind between reads (`mov16`, `mov64`, `mov128`, `add`, `mul`, `shl`,
  `not`, `abs`, `tstz`, `alum`, `rfence`, `rwfence`, `movs douta`, `mov32`, `bra` to the next),
  three runs (48 reads): + 3, but + 2 after `add` and after `mov32` in all three runs, and in the
  third run + 1 at the first read and + 2 after `mov64` and after `alum` as well.
- Across taken branches and a call (30 reads, the three runs alike): + 2 at the first read, at
  the targets of branches over 1 and over 3 `nop`s, in the called routine, after its return and
  at the target past it; + 3 at the target of a branch to the next instruction and + 2 at the
  read after it; + 3 at the target of a branch over 7 `nop`s and at the read after it.
- Loads with `nop`s instead of a fence, then `rfence`, then `rwfence` (33 reads): + 1 to + 3.

No read in any of the 27 programs was more than 3 or less than 1 ahead of its index: the
vectors made from these runs (vectors.py) all match the simulator's index + 3 with the hardware's
value up to 2 below.
[infer] The fetch runs up to three instructions ahead and falls one or two behind mostly at
fixed places of a program: back to back at instructions 26-27 whatever the `nop`s before them,
which with the 36-dword data segment are dwords 62-63, the last two before a 64-dword boundary;
the branch program reads alike in all three runs. Some runs fall behind elsewhere (two of twelve
back to back, some first reads, the third kinds run), so the place is not all of it (Q062).

**`abs` of `ds1[n]` (bit 15).** Under `alum signed`: `ds1[16]` gives 0x600 and with bit 15
0x66666667 (abs of `ds1[48]` = 0x99999999); `ds1[17]` 0x700, with it 0x55555556 (`ds1[49]`);
`ds1[19]` 0x170086e2, with it 0x7ffffff5 (`ds1[51]` = 0x8000000b); `ds1[20]` 0x17000a66, with it
0x33333334 (`ds1[52]` = 0xcccccccc). Bit 15 adds 32 to `n`: the field is bits 15:10, as `not`'s.

**`mov128`.** With the sixteen temporaries complemented after the copy, the controls give: row 2,
the data's C, D, K, L; row 24, `ds0[48..49]` and `ds1[48..49]` complemented; row 27, `ds0[54..55]`
and `ds1[54..55]` complemented: rows 24-31 are the temporaries, and the decoder, which stopped at
row 15, reads them. With bit 15 set, all 32 source rows into `ds[52]`, and rows 2 and 31, and row 2
with `swap`, into `ds[48]`, `ds[50]`, `ds[52]`, `ds[54]`, write 0x77777777, 0x0000ff01, 0x77777777,
0x0000ff01 to the destination row: G and H, which the data holds in `ds0[8]`, `ds0[9]` (row 4) and
the temporaries hold complemented. Nothing else in the row changed.

**`nop`'s bit 2.** Three `pc.0` reads after a `nop`, five runs each: the plain `nop` gave 0x14,
0x15 and 0x15 or 0x16 (two runs 0x16), the flipped one the same set (three runs 0x16).
