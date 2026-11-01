<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
## Conventions

### Where each fact comes from

This is a reconstruction, not a vendor document. Every statement about what an instruction
*does* carries a tag, as in `doc/specs/hw_spec.md`:

- **[HW]** measured on the laptop: our own programs or probes ran and behaved as stated.
- **[CAP]** captured from the closed driver running under the extraction harness (its
  programs, the words it writes), so exact for that build.
- **[RE]** read from the closed microkernel's code with our disassembler, or established by
  black-box probing of the layouts (bit flips and value sweeps). Encodings and assembler
  spellings are **[RE]** in this sense: our decoder decodes every word of the firmware and the
  captures, and nothing more is implied about behaviour.
- **[DDK]** read in the GPL DDK sources (register names, structure layouts).
- **[infer]** an inference from names, context or how the firmware uses an instruction;
  verify before relying on it.
- **[open]** not known. Said plainly rather than guessed.

Two tags joined by a slash (**[CAP/HW]**, **[RE/CAP]**) mean both kinds of evidence agree, the
first being the primary one. The design documents also use **[patent]** and **[decide]**
(HACKING.md).

**Names.** Most spellings are the decoder's **[RE]**; where a public
source (the Rogue ISR, Mesa, Rogue's register headers) spells the same thing, the tables take its
spelling. The rest keep their names when the hardware confirms what the name says or a public source
outside PowerVR uses the same word for the same thing, and carry a name of ours where the
name would mislead: `sop3c`, `lrp`, `alrp`/`alrpc`, `latch`, `usub8`, `usub16`, `.quadlead`
(a quad's first instance, E088) and `.twopart` (bit 42). Eight names stay without a measured
meaning, so
they are kept as printed and marked **[open]** where they appear: `bexception` (its bit 51), `setm`,
`.bypassl1`, `.dm_nomatch`, `moest`, `setfc`, `twosided` and `optdwd`. `perinstance` (E112) and
`.pcff16` (E116) have one.

Facts asked of the hardware with our probe programs are collected in one section, one snippet
per fact, marked *Measured on the hardware (2026-10-22)* (with what stays undecided) or *Not
probed yet*.

### Clean room

Everything here was written from our own decoders, our own programs, the GPL DDK and our
hardware runs. No vendor ISA text is quoted. Examples are either our own programs
(`asm/`) or instructions assembled fresh for this document; no instruction
word of the closed firmware appears. Where the firmware's use of an instruction is described,
it is described in words and counts, not quoted.
