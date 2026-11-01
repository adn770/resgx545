<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Flow control: `ba`, `br`, `lapc`, `bexception`

Class 31 with `enc[54:52]` = 0 and the operation in `enc[40:38]` **[RE]**: 0 `ba`, 1 `br`,
2 `lapc`, 3 and 4 the `pclink` moves (*Moves*), 5 `nop` (*Synchronisation and misc*);
`bexception` sits next to them. The branch flags are `.nosched`, `.synce`/`.syncent`,
`.savelink` and `.mon`; `ba` and `br` take the full predicate.

- **`ba #n`** jumps to instruction `n`; **`br #k`** by a signed offset from the `br` itself
  **[HW]**; `.savelink` makes either a call, which writes `pclink` even when its predicate is false
  (one case run, `p0 ba.savelink`); **`lapc`** returns to `pclink` **[HW]** (E475, E476). See
  *Program counter, calls and the end of a program* for the evidence.
- **A quad whose instances disagree** on a predicated branch goes, all four instances, where its
  top-left instance goes, without masking **[HW]** (E089): in a triangle, the first covered instance
  under `phas`'s `parallel` and instance 0 under `perinstance` (E112). **`.synce`** and **`.mon`**
  hang a fill; **`.syncent`** and **`.nosched`** change nothing there **[HW]**.
- **`bexception #n`** jumps to instruction `n` and **`bexception.rel #k`** (bit 38) by `k`
  from itself, under the full predicate: a branch with `ba`'s and `br`'s fields **[HW]**
  (E108). The `.rel` spelling is ours. With every field 0, the bare `bexception` the reference
  disassembler prints, it jumps to instruction 0 and hangs a fill (E100). What `enc[51]` adds
  to the branch, and what `.synce`, `.syncent` and `.mon` are for, is **[open]**.

**In the firmware [RE].** 954 `ba` (591 predicated, 232 calls), 12 `br`, 74 `lapc`. The kernel
CCB dispatch jumps to its handler by moving the handler's address into `pclink` and running
`lapc`.

<!-- @example usse ba.savelink #0x00000100 -->

<!-- @example usse p0 ba #0x00000010 -->

<!-- @example usse br -#0x00000003 -->

<!-- @example usse p0 bexception.rel #0x00000004 -->

<!-- @group usse class=31 pat='ba\{|br\{|bexception|lapc' -->
