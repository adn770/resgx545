<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Predicates

There are four predicate registers, `p0`-`p3`, per instance **[RE]**. Most instructions take an
execution predicate in `enc[58:56]`, printed before the mnemonic:

| value | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|-------|---|---|---|---|---|---|---|---|
| prints | (always) | `p0` | `p1` | `p2` | `p3` | `!p0` | `!p1` | `Pn` |

The integer multiply-add, colour, dot-product and video groups have only a two-bit predicate
`enc[58:57]`: always, `p0`, `p1`, `!p0`; the dual-issue group has the same four in
`enc[57:56]`, and they act as printed on both operations **[HW]** (*Dual issue*).

- An instruction whose predicate is false does nothing for that instance (**[HW]**, if
  indirectly): our vertex and state programs issue a four-register load into `pa0`-`pa3`,
  predicated on `p0`, right after a test that leaves `p0` false; had it run, it would have
  replaced the vertex the PDS had just DMAed there, and the triangle renders exactly.
- Predicates are written by the **test group** (`p0`-`p3`, chosen by `enc[35:34]`), by
  `rlp` (a seven-bit predicate number) and by `atst8` (`p0`-`p3`, optionally negated)
  **[RE]**. **[HW]** `rlp`'s predicate numbers 4 and up alias `p0`-`p3` (*`rlp`*); whether
  `atst8` reaches more is **[open]**.
- `Pn` (value 7) **never runs** the instruction, whatever `p0`-`p3` hold **[HW]** (*`br`
  offsets and the `Pn` predicate*): the decoder prints it for value 7 of the
  full field and nothing in the firmware or the captures uses it.
- A repeated instruction tests its predicate once, for the whole instruction **[HW]**
  (*Predicates on repeated instructions*).
- **Predicates and control flow [HW].** `p0`-`p3` are not changed by `ba`, `br`, `ba.savelink`,
  `br.savelink`, `lapc` or a predicated one of these, taken or not (E477: 28 of 28 cases with the
  patterns 1010, 0101, 1111 and 0000, and 16 of 16 through `ba.savelink` and `lapc`). A routine's
  own tests change them for its caller: there is no save and restore of `p0`-`p3` around a call. A
  predicated branch is taken when its predicate is set (`!pN` when clear).
- **The predicates are not reset between jobs [HW].** A job that reads `p0`-`p3` before it sets them
  reads the pattern the job before it left, in 98 to 99 percent of its 2048 pixel instances (E477:
  2016 to 2032 pixels in each of the ten readers that followed a setter) and another pattern in the
  others. The probe table's model, "cleared at the start of a job", fails. A task sets `p0`-`p3` by
  a test before it reads them; across firmware tasks, p1 at the next entry was the writer's 0 and p0
  was not after a writer that called the closed task **[HW]** (E536, 3 of 3 rounds; p2 and p3
  equalled the flags but also move between readings with no writer, so they show nothing), and the
  rest is **[open]** (Q124, Q152). A second table agrees: `p0` and `p1` after a setter read the kept
  value in 96.3 to 100 percent of the pixels in 10 of 10 reader jobs (E484).

**In the firmware [RE].** The microkernel's predicates guard branches above all: 591 of its
954 `ba` are predicated (`p0` 318, `!p0` 94, `p2` 76, `p1` 72, `!p1` 26, `p3` 5). A few dozen
stores, moves, loads and bitwise operations are predicated too. A typical sequence tests a
flag into `p0` without writing a register and branches on it.
