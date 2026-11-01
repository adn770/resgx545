<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Loads and stores: `ld*`, `st*`, `eldd`, `eldq`

Classes 29 (loads) and 30 (stores) **[RE]**. The mnemonic is `ld`/`st` plus an address mode and
a data type: `ldad` = load, absolute (`a`), dword (`d`); `l` and `t` are the other address
modes (local and tiled **[infer]**, both **[open]**), `w` and `b` 16- and 8-bit data. The base
is a source-0 operand, the offset a source-1 operand (an immediate or a register), and
`enc[41:40]` picks plain, pre-increment or post-increment addressing. Flags: `.skipinv`,
`.syncs`, `.nosched` (stores), the cache mode (`.bpcache`, `.fcfill`, `.bypassl1`), `.noread`
and `.rangeenable` (stores), and a count used as `.fetchN` (MOE-expand bit `enc[53]` clear)
or `.repeatN` (set). A load can name a range operand (source 2) and always names a data fence
`drc0`/`drc1`.

**Addressing [HW/RE].** Offsets count elements of the data size (4 bytes for `d`, 2 for `w`):

| form | elements accessed | base writeback |
|------|-------------------|----------------|
| `[b,+#k]` / `[b,-#k]` | `b+k` / `b-k` | none |
| `[b,++#k]` (pre) | `b+k` | `b += k` |
| `[b,#k++]` (post) | `b` | `b += k` |
| `.fetchN [b,+#k]` | **`b+k+1` ... `b+k+N`** | none |
| `.fetchN [b,#k++]` | `b+k` ... `b+k+N-1` | `b += N` |

A fetch with a base-plus-offset address starts **one element after** the printed offset:
`ldad.fetch4 r3, [r2,+#1]` loads dwords 2-5 into `r3`-`r6`. This holds for every count from 2 to
16, by immediate and by register offset, and a plain load reads the offset itself **[HW]**
(*E093*). The post-increment fetch was checked on the laptop (the kernel CCB fetch and the
GETMISCINFO reply, `doc/specs/hw_spec.md`) **[HW]**; its writeback follows from the
firmware's loops **[infer]**. Before any `smlsi`, a fetch steps its destination by one register
**[HW]**. After one, it steps by the fourth `smlsi` increment **[infer]**: the firmware sets
`0, 0, 0, 1` before its fetches. A fetch whose registers would run past the task's temporaries
writes **none of them**: with 32 temporaries, `ldad.fetch4 r28` loads `r28`-`r31`, while
`ldad.fetch4 r29` and `r30` leave all four as they were **[HW]** (*E093*; the reason vector `vec1`'s
`ldad.fetch4 r30` left `r31` unchanged). A **register** offset `o` (`[b,+rN]`) is
`(o >> 16) × (o & 0xffff)` bytes, and a fetch starts one element after it too **[HW]** (*Register
offsets of loads and stores*); the firmware has four such stores.

- **A store has a fetch too [HW].** `stad.fetchN [rb,+#k], rs` stores `rs` to `rs + N - 1` in the N
  consecutive dwords `b + k + 1` to `b + k + N`, the one-dword shift of a load fetch (N = 2, 4 and
  16 with `k` = 1 and N = 4 with `k` = 0: 4 of 4 cases, E482; `fetch4` with `k` = 2, 3, 4, 7, 8 and
  15, `fetch8` with 3 and `fetch16` with 2: 8 of 8, E516), `stad.fetchN [rb,#k++], rs` stores them
  from `b + k` and moves `rb` by N once for `k` = 1 to 4 (`k` = 1 with N = 2, 4 and 16: 3 of 3,
  E482; `fetch4` with `k` = 2 and 3, `fetch8` with 2 and `fetch2` with 4: 4 of 4, E516: the step is
  the fetch width, not `k`), and `stad.fetchN [rb,++#k], rs` stores them from `b + k + 1` and moves
  `rb` by N for `k` = 1 and 2 (`fetch4` with `k` = 1 and 2 and `fetch16` with 1: 3 of 3, E516); the
  post- and pre-increment rules were read from those readbacks after the first predictions failed. A
  copy of 16 dwords is so `ldad.fetch16 rA, [rS,+#0], drc0; wdf drc0; stad.fetch16 [rD,+#0], rA`
  with `rD` one dword below the destination (1 of 1 case: 16 dwords in order). A fetch wider than
  16, `k` above 15 and a copy with `k` other than 0 were not run.
- **`.repeatN` of a store or a load steps the pointer register too [HW].** In
  `stad.repeatN [rb,...], rs` iteration `i` stores `r(s + i)` at the address held in `r(b + i)` (the
  data address read for every `i`: N = 2, 3, 4, 8 and 16 in E483, 5 to 7 and 9 to 15 in E515), and
  the pointer registers `r(b + i)` for `i` < N move by the form's own increment: `k` after its
  access for `[rb,#k++]`, `k` before it for `[rb,++#k]`, none for `[rb,+#k]`, and the other pointers
  stay (E483: 26 of 26 cases with 16 valid pointers `r40`-`r55`, N = 2, 3, 4, 8 and 16 plain, N = 2,
  4, 8 and 16 post-increment, N = 2 and 4 pre-increment, twelve after an `smlsi` and one copy, the
  movement read for `r40` to `r43`; E515: a marker past each of the sixteen pointers, N = 5 to 16
  post-incremented with `k` = 1 and N = 8, 12 and 16 with `k` = 2 (15 of 15), N = 8, 12 and 16
  pre-incremented with `k` = 1 and N = 8 with `k` = 2 (4 of 4), so `r44` to `r55` move as `r40` to
  `r43` do and the unused pointers stay). `ldad.repeatN rd, [rb,...]` loads likewise the dword
  `r(b + i)` addresses into `r(d + i)` (E483: 7 of 7 cases, N = 2, 4, 8 and 16, the pointer movement
  read for 2 or 4 pointers; E515: from `r(56 + i)` into `r(10 + i)` in 11 of 11 plain cases, N = 5
  to 7 and 9 to 16, and `r(56 + i)` moved for `i` < N in 10 of 10 post-incremented cases). A
  pre-incremented `ldad.repeat`, an `smlsi` before a repeat of five or more and N above 16 were not
  run. The model had N accesses from the one pointer `rb`. With only `rb` (and `r41` for the loads)
  holding an address, the registers after it are read as pointers too: the first run faulted the job
  in all 7 `ldad.repeatN` cases and in the 9 of 9 `stad.repeatN` cases with N of 4, 8 and 16, while
  `stad.repeat2` and `repeat3` completed, storing `r3` at the address `r41` held (E483). The
  one-pointer series is `smlsi #0, #0, #0, #1` first (*`smlsi` increments*):
  `stad.repeat16 [rb,#1++], r2` then stores `r2` to `r17` at 16 consecutive dwords and moves `rb` by
  16 (2 of 2 cases, two instructions, no one-dword shift).
- **Cache modes.** The firmware uses `.bpcache` on almost every access; `.fcfill` once.
  The SGX540 swaps the two cache-mode bits; `usse-dis --core 540` follows it. No mode, `eld`'s
  `.bypassl1` included, makes a reload miss a store, in one instance or across instances
  **[HW]** (E098). Nor does any mode keep an old dword when the host writes it while the job
  runs: every load mode, after a warming load of any mode, reads the host's value within one
  reload **[HW]** (E107). What the modes change is **[open]**; it does not show in the data
  a load returns.
- **`eldd`/`eldq d, [base, index, #offset], limit`** (class 29 with `enc[54]` set) load the
  dword (`eldd`) or four dwords (`eldq`) of element `index + offset` from the base when it is
  below `limit`, and zeros otherwise: a bounds-checked load **[HW]** (E098). Indices or limits
  with bit 31 set are **[open]**; the firmware does not use them.

**In the firmware [RE].** 598 loads and 349 stores, nearly all `ldad`/`stad` with `.bpcache`
on its control blocks through `sa0`-`sa2` or computed bases; 120 fetches; `ldaw` twice. Its
807 `wdf` (for 598 loads and 196 `ldr`) show the pattern: issue the loads, then wait on the
counter before the first use.

<!-- @prog use_vtx.s match='ldad' -->

<!-- @example usse ldad.fetch4 r3, [r2,+#1], drc0 -->

<!-- @example usse stad [r2,+#7], r9 -->

<!-- @group usse class=29,30 -->
