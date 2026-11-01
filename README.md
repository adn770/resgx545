# resgx545

resgx545 (reverse-engineered SGX545) documents the Imagination **PowerVR SGX545** GPU of
Intel's Cedar Trail platform (Atom N2600/N2800/D2500/D2700, sold as "GMA 3600/3650") and is
building the tools to drive it under a modern mainline Linux kernel. Mainline's `gma500`
driver does display only. Linux 3D support only ever came as Intel's out-of-tree driver: a GPL
kernel module for long-dead kernels, plus closed user-space libraries and firmware. The test
machine is a Cedarview laptop (Atom N2600, 2 GB, i686).

It is a for-fun, learning-driven project: firmware boot, GPU MMUs, command rings, `drm_sched`,
recovery, UAPI design, and the disassemblers, assemblers and simulator that reverse engineering
needs. It is not a promise of 3D acceleration.

## Status

Published so far: the record formats and their checkers, and the firmware container: the
cutter and reference loader (`tools/fwcutter`), the C loader (`tools/sgx_fw`), the extraction
harness (`harness/ukernel-extract`), the firmware capture tables (`captures/firmware`) and the
first evidence records. The remaining specs, records and tools arrive unit by unit, in the order
of the roadmap below.

## How the repository is organised

The work is published unit by unit, in the order of a roadmap (`doc/roadmap.md` once it
lands): foundations, the firmware container, disassembly, firmware boot, the transfer queue, the
assembler, the probes, the PDS (the programmable data sequencer), the simulator, the render
path, 3D, and the open questions. Once published, every claim can be traced:

- **specs** (`doc/specs/`) cite **evidence records** (`evidence/<unit>/E<nnn>-<slug>.md`), one
  finding per file;
- evidence records cite **dataset manifests** (`datasets/<id>.toml`), which pin the measured
  data by hash, and **glossary terms** (`glossary/<group>/<NAME>.toml`);
- glossary terms cite their **sources** (`cites/<source>.toml`), an external one through a
  **citation record** (`citations/<source>/C<nnnn>-<slug>.md`: where, a link at the pinned
  version, the line quoted);
- what is not settled is an **open question** (`questions/<unit>/Q<nnn>-<slug>.md`), removed
  once a record answers it.

The data itself lives in two companion repositories with the same layout,
`<unit>/<feature>/`, published alongside the units that need them: **resgx545-data**
(public; every readback of our own probe campaign) and **resgx545-data-private** (data derived
from the closed driver, which cannot be published; its manifests are checked here for form
only). The kernel driver is developed in a fork of mainline Linux, which arrives with the
firmware-boot unit; this repository holds the documentation, the tools and the shared UAPI
header.

## Clean room

- This repository contains **no Imagination code** and no bytes cut or captured from the
  closed driver. The firmware is never distributed: each user cuts it from their own copy of
  the closed package.
- Hardware facts come from open SGX kernel sources (GPL or MIT), Imagination's open Rogue code
  as an analogue, published patents and patent applications, Imagination's and TI's public
  documents, and measurements on our own laptop.
- Closed user-space libraries are run or probed only as black boxes: their strings and
  exported symbols, and captures of the closed stack running. The one exception: srvinit's
  x86 code was disassembled only to locate the firmware and the values it patches, for
  interoperability under Art. 6 of Directive 2009/24/EC (`HACKING.md`); only those facts are
  recorded, and black-box captures back them wherever they reach. The closed firmware is
  disassembled only to learn the interface our driver must meet; none of its code or bytes
  enters this tree, and what it shows never names anything.
- Every name for a register, field or structure comes from the glossary, with its source.

## Licence

MIT (`LICENSE`); files that differ say so in their `SPDX-License-Identifier` line. The tree
follows the [REUSE](https://reuse.software/) specification.

## How it was made

Much of the code, the tests and the documents were written by an AI coding assistant (Claude
Code) working under the author's direction and review, with the author choosing the design and
running the hardware. Commits carry a `Co-Authored-By:` trailer; kernel commits carry
`Assisted-by: LLM` instead.

## Trademarks

PowerVR is a trademark of Imagination Technologies Limited. Intel and Atom are trademarks of
Intel Corporation or its subsidiaries; Cedar Trail and Cedarview are Intel code names. Linux is
a registered trademark of Linus Torvalds. Other names are the property of their owners and are
used here only to identify the hardware. resgx545 is an independent project, not affiliated
with, endorsed by or sponsored by Imagination Technologies or Intel.
