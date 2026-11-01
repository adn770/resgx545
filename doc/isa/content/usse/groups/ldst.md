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
