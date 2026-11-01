<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# SGX545 PDS instruction set reference

The **PDS** (programmable data sequencer) of the SGX545 runs small programs that prepare and
start USSE tasks: they DMA vertex data and state into the USSE attribute registers, issue
iterator and texture work, and start a task on a code address with `doutu`. Every USSE task
starts this way, the microkernel's own included (`doc/specs/hw_spec.md`). The
USSE instruction set has its own reference, `doc/specs/usse_isa.md`.

This reference covers the PDS instruction set as our disassembler `tools/usse-dis/pds-dis`
decodes it and our assembler `tools/usse-asm/pds-asm` writes it. The decoder was derived
by black-box probing of the layouts and decodes every word of the firmware and the captures
(`tools/usse-dis/README.md`); the assembler describes the same layouts as forms in
`tools/usse-asm/pds_forms.c` and checks each word it builds against the decoder. The
generated parts of this document read those forms.

No simulator models the PDS and no hardware probe has been run on it: **[HW]** here means that
one of our own programs depends on the behaviour and works, as the transfer and fill paths do
(`doc/specs/transfer.md`).
