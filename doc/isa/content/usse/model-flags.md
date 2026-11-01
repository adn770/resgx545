<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Scheduling flags

Most groups carry a handful of one-bit flags printed after the mnemonic. Their bit positions
are in each group's field list in the reference; what is known of their effect:

- **`.end`** ends the program after this instruction **[HW]** (*Program counter, calls and
  the end of a program*).
- **`.skipinv`** skips invalid instances **[HW]** (E104). In a triangle's pixel shader an
  instruction with it runs only for covered pixels. One without it also runs for some of the
  uncovered pixels in the quads the triangle covers, and their `o0` reaches the tile. The
  closed compiler's pixel and state programs (and ours, which follow them) set it on nearly
  every instruction. The same reading explains an end-of-tile task where a `mov.skipinv` did
  not run but the plain `mov` did, if that task's instance is invalid **[infer]**. It is
  Rogue's default turned into a flag: Rogue's instructions run only for enabled instances
  unless they carry `(ignorepe)` ("PowerVR Instruction Set Reference", pp. 20, 66). Without it an
  instruction runs for all four instances of every
  quad the triangle touches, the same in every run **[HW]** (E111). Whether an uncovered
  instance's `o0` lands varies, by whole quads: of 102 helper pixels, 26 to 43 land at 0 to 16
  `nop`s,
  71 at 32 and 53 to 59 from 64 on, mostly quads whose instance 0 is covered (E113);
  what decides it per quad is **[open]**.
- **`.nosched`** is a scheduling hint, probably "do not switch to another task after this
  instruction" **[infer]**; it changes nothing a fill's pixels see **[HW]** (*`.tpres`,
  `.partial`, `.nosched`, `.syncs`*). Our programs carry it only where the captured programs do
  (`nop.nosched` before the DMA wait); the firmware uses it once, in the same idiom.
- **`.syncs`** decodes in most groups; **in a fill it hangs the task** **[HW]** (on `mov` and
  `fmad`), so it waits for something a fill never gives; what is **[open]**. Unused by the
  firmware and by us.
- **`.partial`** (the bitwise group) changes nothing a fill sees **[HW]**. **`.quadlead`** runs the
  instruction for instance 0 of each 2x2 quad only, the others keeping their destination **[HW]**
  (E088). The closed compiler sets it on a fragment loop's exit test, so only the quad's lead
  instance computes the predicate the loop's branch follows **[CAP]**; `.partial` on the
  test group is **[open]**.
- **`.freep`** on the emits frees the task's resources once the emit is done **[infer]**:
  every final emit of our pixel and state programs carries it, as the captured ones do.
- **`.tog`** and **`.trigger`** (`nop`), **`.tpres`** (single-source floats), **`.gpiext`**
  (`efo`), **`.twopart`**/**`.cut`** (the vertex and MTE emits) and
  **`.tasks`**/**`.taske`** (`emitpds`) are discussed with their groups; most are **[open]**.

The radare2 emulation of the firmware assumes that `.skipinv`, `.syncs`, `.nosched` and `.end`
do not change what one instance computes, and ignores them (`tools/usse-dis/r2/README.md`);
nothing contradicts that so far.
