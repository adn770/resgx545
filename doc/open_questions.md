<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# Open questions

*Generated from `questions/` by `tools/records/questions.py`; do not edit.*

## edm

- `Q002` (phase 3): is the laptop's SGX core clock 399.0 MHz rather than the DDK's 400 MHz, or do TIMER and the EDM tick run from a reference other than the core clock? (E009)

## platform

- `Q001` (phase 3): what do 0x0810, 0x0814 and 0x0818, set once by the init script to 0x1, 0xffff and 0x7ff, control? (E006)

## transfer

- `Q003` (phase 4): why does a transfer render that faults on a read-only page raise no BIF-fault interrupt the host sees, and how does a host recover the EDM in place afterwards? (E021)
- `Q004` (phase 4): what do a transfer context's flag bits 1 and 4 and a priority other than 0 do on the hardware? (E015)
