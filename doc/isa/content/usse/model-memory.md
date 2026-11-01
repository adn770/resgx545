<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Memory, data fences and the register file

- **Loads complete asynchronously.** A load (`ld*`, `eld*`, `ldr`, the samplers) names a data fence
  counter, `drc0` or `drc1` (two bits for `ldr` and the samplers, `drc0`-`drc3`), and `wdf drcN`
  waits until the loads counted on it have landed **[RE/HW]**. In a fill one `wdf drc0` covers every
  load outstanding on `drc0`, whether `ldad`, `ldad.fetchN` (the whole fetch) or `ldr`: 1, 2, 4, 8
  and 16 independent `ldad`, five mixes with fetches of 2, 4, 8 and 16 dwords and `ldr`, and, in the
  growth runs, 24, 32, 48, 64, 80 and 100 distinct `ldad` on `drc0`, 32, 64 and 100 on `drc1` and 2,
  4, 8, 12 and 16 `ldad.fetch16` (256 dwords) were all complete after the one `wdf`, and no limit on
  the number outstanding was seen up to 100 distinct `ldad` on one counter and 16 `ldad.fetch16`
  **[HW]** (E478), nor up to 192 distinct-line `ldad` on one counter, the first 100 into `r4` to
  `r103` and the rest reloading `r4` onward with other lines (104, 112, 128, 160 and 192 on `drc0`,
  128 and 192 on `drc1`: each of 8 sampled registers held the line of its last load, 7 of 7 jobs,
  the 4 or 5 reloaded registers read per job; E518). Three more cases, 128, 160 and 200 `ldad`
  reloading the same eight lines into eight registers, were complete too (27 of 27 cases in all, one
  run each), but they issue the same loads again, so a lost or late reload would leave the registers
  unchanged: they cannot show a lost reload; E518 can, for the reloaded registers it read (5 of 92
  at 192), and saw none lost. 200 distinct loads in one program were not run. A load is not complete
  without the `wdf` in the sense that one `ldad` read by a `stad` still holds the register's old
  value after 0, 1, 2, 4, 8, 16 or 32 `nop`s and four `ldad` after 0 or 16 (9 of 9); an ALU
  instruction (`ima32.u r11, r10, #1, r12`) reads the old value after 0, 1, 4, 16, 32 and 48 `nop`s
  too (6 of 6, E517), so the reader has no interlock whichever it is; a load not waited for had
  landed when a `stad` read it after 40, 100 and 128 `nop`s and not after 48 and 64 (one sample
  each, a timing effect **[infer]**), so no instruction count stands in for the `wdf`; and a `mov`
  to the register issued after the `ldad` and before its `wdf` is overwritten by the load (4 of 4),
  while one after the `wdf` wins (E517; the texture unit and the dual-issue secondary as readers
  were not run, Q052, Q146). A `wdf` with nothing outstanding returns at once and hangs nothing (11
  of 11 cases: as the first instruction, on a counter never used, twice in a row, on all four
  counters, and after an `idf drcN, bif` with nothing stored; E480). **A `wdf drcN` does not wait
  for the loads of the other counters [HW]** (E479): loads of another counter issued after the
  waited ones were still in flight in 10 of 10 runs (four `ldad` on `drc1` after two `ldr` on
  `drc2`, `wdf drc2` only) and in 2 of 10 (four `ldad` on `drc0` after four on `drc1`, `wdf drc1`
  only), and complete in the runs that had waited on four `ldad` first (28 of 30), so what has
  landed depends on timing: each counter counts its own loads **[infer]**, and a program waits on
  every counter it used. The counts of ten runs are those of scratch runs recounted by the reviewer;
  the data hold one run of each case (2 of the 8 cases show the markers in it). All this was
  measured in client pixel tasks; the EDM task of ours of E534 shows the same for a result `stad`
  followed by a load, a `wdf` and two more stores and then the flag the host reads with no `idf`
  (18 of 18) and for a `wdf` with no load outstanding between a `str` and an `ldr` (18 of 18, 15 of
  which could show a change, and none did), and no more (Q197). The firmware almost always follows
  its loads with a `wdf` before using the data (711 `wdf drc0`, 96 `wdf drc1`), and our programs
  wait with `wdf drc0` for the attribute DMA the PDS started.
- **`idf drcN, bif`** appears 124 times in the firmware, mostly right before a `wdf` on the same
  counter, after stores **[RE]**: it looks like a fence that makes earlier memory writes visible
  (through the BIF, the memory interface) and is counted on `drcN` **[infer]**. In a fill no
  measured case needed it **[HW]**: a `stad` and a later load of the same dword, all 2048 instances
  of the fill storing the same value to that dword, returned the stored value with no `idf` in 16 of
  16 cases (`ldad`, `.bypassl1`, `.fcfill`, `eldd`, `.bpcache`, on `drc1`, after two stores and
  after sixteen; E481), and the dword the host read held the stored value after seven short programs
  (one or sixteen `stad`) that ended with no fence, an `idf` only, a `wdf` only, both, or a `nop`
  (E480). Both show a dword that every instance wrote with one value, so by themselves they do not
  show that one instance sees its own store. **An instance sees its own unfenced `stad`, and its
  store changes the dword the host reads with no fence [HW]** (E512): with each of the 2048
  instances of the fill storing a value of its own to a dword of its own, the load returned the
  instance's own value in 2048 of 2048 pixels in each of nine cases (`ldad`, `.bypassl1`, `.fcfill`,
  `drc1`, a `wdf` only between, two stores where the load returns the later value, an `idf` and its
  wait between, and the `idf` at the end) and 2048 dwords changed (32 values read) in the seven
  cases that ended with no `idf` and no fence. A load of another instance's store returns it when
  that instance ran earlier (the x and y neighbours in its quad: 2048 of 2048, n ^ 65 not run;
  lower-numbered instances of other quads: 1024 of 1024 in each of three masks; the right 32 columns
  of the 64 x 32 target reading the left 32: 1024 of 1024) and in part when it runs later (64 of
  1024 at no delay, 792 and 984 after 64 and 192 `nop`s for the next quad in x, none for 32 columns
  on): a rule of timing and of the order of the tiles, the left half first **[infer]** (E514), and
  no case needed an `idf`. The `idf` in the storing instance, the host reading during the job, a
  texture fetch of the stored data are **[open]** (Q143, Q134); an EDM task's own store lands with
  no `idf` before the flag the host reads (E534). `str` then `ldr` is ordered for two registers in
  an EDM task of ours (E534, below). The `pixelbe` and reserved modes of `idf` are **[open]**.
- **Addresses.** Loads and stores take a base register and an offset counted in elements of
  the access size (4 bytes for `d`, 2 for `w`, 1 for `b`) **[DDK/HW]**; the addressing modes
  and the fetch rule are in *Loads and stores*. Addresses are device virtual addresses of the
  task's memory context **[HW]**.
- **The SGX register file** is not memory: `ldr rD, #idx` and `str #idx, src` read and write
  the SGX register at offset `idx × 4` **[RE/HW]**. A client pixel shader on our render node
  reads any register this way; a client store to the one register tried was dropped
  (measured on our render node). **In a firmware (EDM) task of ours a `str` to 0x0814 or 0x0a78 is
  seen by the next `ldr` of that register and by the host, with no fence and at every distance
  run [HW]** (E534: 318 of 318 runs, 0 to 16 instructions between and a second `ldr` 64 `nop`s
  later, a `wdf`, an `idf`, both or neither, two `str`; an earlier `ldr` is not changed by a later
  `str`; four fresh loads, and the replicates within a load are not independent). It is **[open]**
  for a client `str` (no client `str` was seen to change a register, Q134), for a register whose
  write has an effect, with a job running, and for the register-index forms (Q154).
- **Caches.** `ci`, `cf` and `cfi` invalidate, flush, or flush and invalidate the levels their
  last operand names (L0 and L1, L2, or all three) **[infer]**, from the names the reference
  disassembler prints; the cache mode flags of loads and stores (`.bpcache`, `.fcfill`,
  `.bypassl1`) are discussed under *Loads and stores*.
