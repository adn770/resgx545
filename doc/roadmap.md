<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# resgx545 roadmap

resgx545 is published in phases, from the records and the firmware container up to the 3D state of a
render. Each phase brings its tools, its probe tables, its evidence records, its glossary terms and
its specification together, and the forks of Linux, radare2 and IGT gain the commits that pair with
it. This document says what each published phase holds, what the last phase, the pipeline simulator,
will need, and what is still open, unit by unit.

## 1. How to read it

A phase is one commit, or a few where a sub-phase finishes what its phase began (sub-phases 2.1 to
2.3, 6.1 and 10.1). Its records cite their data by dataset manifest; the evidence tiers are those of
`HACKING.md`: GPL kernel sources (DDK), black-box captures of the closed stack (CAP), our
disassembly of the firmware for interoperability (RE, facts only), runs on the laptop through the
linux fork (HW), and our inferences (infer). What one follow-up run did not settle is not published
as evidence: it is an open question (`questions/`), listed in section 4 with the glossary rows still
inferred.

## 2. The published phases

### 2.0 Phase 0: foundations

The repository's base: README, HACKING, the licences under REUSE, the clean-room guard, and the
formats every later phase writes in. Evidence records hold one finding each, dataset manifests pin
the measured data in the companion data repositories by hash, glossary terms hold every name with
its sources, `cites/` records the external sources and citation records quote them at a pinned
version. The tooling in `tools/records/` checks each format and generates the views under `doc/`;
the records themselves arrive phase by phase.

### 2.1 Phase 1: the firmware container

How the SGX545 firmware is cut from the vendor's libraries, described, parsed and loaded:
`tools/fwcutter` (the cutter, the container reader and writer, the reference loader; formats v1 to
v4), `tools/sgx_fw` (the same loader in C, kernel style), `harness/ukernel-extract` (srvinit run
without a GPU, the init-info decoder and the CCB model) and the firmware capture tables. The
specification is `doc/specs/fw_format.md`; the evidence, E001 to E004, rests on captures of srvinit
under the harness and on reading the firmware file (CAP, RE).

### 2.2 Phase 2: disassembly

The USSE and PDS instruction sets are described once, as kinds and forms under `isa/`, and generated
into the tables of the C decoders (`tools/usse-dis`) and the Rust crates `usse-isa` and `pds-isa`,
held identical on random words. Every form is pinned by one made-up word, generated since
sub-phase 2.1. The
radare2 fork's resgx545 branch carries the decoder core as an in-tree plugin (2.2), and every opcode
class has an operation type for radare2's analysis (2.3), which also brings the generated evidence
log, `doc/evidence_log.md`.

### 2.3 Phase 3: platform and boot

How the SGX545 in Cedarview starts. `doc/specs/hw_spec.md` gives the platform part of the hardware
(core identity, features, register map, MMU and BIF, reset, init scripts, boot chain),
`doc/specs/boot_sequence.md` the host boot sequence register by register, and
`doc/specs/tbdr_primer.md` tile-based deferred rendering from the public patents. `tools/bringup`
builds and boots test kernels on the laptop. The linux fork gains the firmware parser, the GPU's
page tables, firmware load and boot, and a register snapshot behind the debug option. Evidence E005
to E011 (DDK, CAP, RE and the first HW runs); questions Q001 and Q002.

### 2.4 Phase 4: the host protocol

The host-to-firmware protocol and the transfer queue. `doc/specs/transfer.md` gives what a host must
build to run a transfer and what the EDM does with it; `doc/specs/edm_dataflow.md` every structure
word the microkernel reaches through a typed pointer and every register it touches, rendered from a
forward dataflow over its whole code. The
linux fork gains the kernel command queue and transfers. Evidence E012 to E021 (RE and DDK, with
captures and HW runs of dummy transfers, fills and copies); questions Q003 and Q004.

### 2.5 Phase 5: the assemblers

`usse-asm` and `pds-asm`, in C on the decoders' form tables read backwards and in Rust in
`crates/sgx-tools`, identical on every program: a text assembles only to a word the disassembler
prints back as that text. `asm/` holds our transfer-queue programs, equal to the firmware file's
templates bit for bit, and `doc/specs/usse_tutorial.md` walks through them.

### 2.6 Phase 6: the client path

Userspace places its own programs in its own GPU address space and submits jobs to the render node:
`include/uapi/sgxfive_drm.h` (pinned to the linux fork's header), `userspace/libsgxfive` with
`sgxfive-test`, and the first triangle's programs. Evidence E022 to E024 (fills, copies, the first
triangle and fault recovery on the laptop); questions Q005 and Q006. Sub-phase 6.1 brings the probe
tables by unit (`probes/<unit>/<feature>.toml`), the campaign runner that runs them on a clean GPU
and records the environment, the sweep runner with the ISP visibility counters around every case,
and what the runs show: evidence E025 to E124 on the platform, the EDM, the transfer, PBE, texture,
PDS, render, TA, ZLS, VDM, MTE, ISP and USSE, and questions Q007 to Q018.

### 2.7 Phase 7: the PDS

What the PDS does on the laptop: douta into the secondary attributes, the pixel-event and
end-of-tile words, loads, stores and fences, the special moves, iteration and its fetch wait, the
task registers, the fault register fields, and the firmware's PDS event and request programs.
`tools/usse-asm/pds_tables.py` models the PDS operations behind the tables' hypotheses. Evidence
E125 to E146 (HW, with RE for the firmware's programs); questions Q019 to Q027.

### 2.8 Phase 8: the core simulator

`crates/sgx-sim` is a simulator of the USSE, the PDS and the texture unit that boots the firmware;
29137 instruction vectors converted from the probe runs (`doc/specs/vectors.md`) show no mismatch
against it (E147). `doc/isa` and the USSE and PDS references, the programmer's guide and the
tutorial are generated from the form tables and runs of the simulator.

### 2.9 Phase 9: the render path

`doc/specs/render_uapi.md` specifies the render node as the kernel and libsgxfive implement it: the
node and its gate, the ioctls, the GPU address space, buffers, VMs and contexts, job submission and
its checks, scheduling, faults, recovery and the security model. The first triangle renders exactly
on targets from 64x64 to 256x256 (E148); IGT's copy of the library is checked against ours.
Questions Q028 and Q029.

### 2.10 Phase 10: the 3D state

`doc/specs/3d.md` gives the TA and 3D paths of the EDM and the state a render runs on: the render
context, TA command, render details, RT data and PB descriptor; the pick, the kick and the finish of
the TA; the scheduling, kick and completion of the 3D; the parameter buffer, the DPM and partial
renders; the VDM stream, the MTE state and the TA's output (objects, region headers, control
streams); the ISP words, depth, stencil, ZLS, multisampling, sample positions and punch-through; the
pixel-event program and iteration. Evidence: 85 records, E149 to E245 (RE for the firmware's paths,
HW for the state words, with `pbdump.py`, `pixels.py`, `region_tiles.py` and `vtx_tasks.py` to read
what the hardware wrote); questions Q030 to Q039.

Sub-phase 10.1 carries the names and layouts these records established into the tools. In
`harness/ukernel-extract`, `edmtrace.py` takes its structure names and pointer fields from
`kick3d.py`, whose TA/3D control block gains the job words the kicks record for each pipe (to offset
0xec), and `edm_dataflow.py` checks its pointer words against those layouts. In `tools/usse-asm`,
`pbdump.py` names the object, region header and control-stream words by their glossary fields and
reads the control stream's 3-dword blocks. 41 glossary rows name the record-backed words of the TA
command, render details, RT data, render context, PB descriptor, PB block and TA/3D control block.

### 2.11 Phase 11: the open questions

This roadmap, and the questions Q040 to Q049 on the readings that rested on inference only: the
EMIT2 value that writes nothing, what the render flags' bit 2 keeps, the index list's first trailing
word, registers 0x0148, 0x0400 and 0x0740, the sideband's bits 8:6, the VDM state word's open
fields, the MADD units and the render context's dword 7. Each names the run that would settle it.
The generated views of section 4 cover every question and every inferred row.

The phase also reruns the EDM dataflow with every pointer word of `kick3d.py`'s client layouts
given (`probes/firmware/edm-dataflow-11.toml` and its dataset), so it types the words
`edmtrace.py` types; E013 is updated to its counts (346 structure words, 379 memory accesses
unresolved). The comments of `sgx545_labels.r2` name structure words only by the glossary's and
`kick3d.py`'s names, checked by `test_labels_r2.py`; `region_tiles.py` keys on
`CSTREAM.PRIM_TILES` (E180); and the glossary gains the `MADD` unit's row (Q048).

## 3. Phase 12: the pipeline simulator

Phase 8's simulator runs one program at a time: of the vectors it is given, 19217 scalar USSE, 26
pixel and 235 PDS vectors stop as unsupported (E147). Phase 12 extends it to a render, from the VDM
stream to the stored pixels, so that a job runs in the simulator as on the laptop.

What it will need, with the records it starts from:

- **Vertex side.** The VDM stream's state and index-list blocks (E060, E185, E188, E191) and vertex
  tasks (E189, E190); the MTE's viewport (E061, E193), culling (E062), w clamp and 1/w floats (E194,
  E197), provoking vertex (E195), window coordinates (E196) and user clip planes (E198).
- **The TA's output.** The object in the parameter buffer (E176, E178, E181), the region headers and
  control streams (E177, E180) and the macrotile rule of the target size (E174, E175).
- **Iterators.** The fetch wait (E131), perspective-correct iteration (E048), the components and
  sizes of coordinate sets (E132, E236), half precision (E237) and vertex colours (E133).
- **The ISP.** Pass types (E065), the depth compare, exact to the ulp (E072), polygon offset (E071),
  the stencil test (E216), sample positions and ISP word 0 bit 28 (E214, E215), the multisample
  modes (E210, E211) and the visibility counters (E070).
- **Pixel-event and end-of-tile tasks.** The end-of-tile task's fields (E043, E044, E126), the tile
  position the pixel-event program reads (E130), and the emits and pack modes (E030, E031, E239).
- **Punch-through and depth feedback.** The feedback that keeps a pixel (E217, E218, E226), the
  depth `depthf` replaces (E244), the stencil a punch-through pass does not write (E234), and the
  colour phase after a pt phase (E082); Q032 asks what `pcoeff` hands the ISP.
- **ZLS and the translucent pass.** The ZLS control word's bit 0 and the load and store bases (E057,
  E058), and the colour a translucent pass reads (E077).

Exit: the simulator reproduces the first triangle pixel for pixel (E023) and the readbacks of the
probe and sweep tables that the units above cover.

## 4. Open work by unit

### 4.1 Open questions

`doc/open_questions.md` lists every open question by unit, generated from `questions/`: Q001 to
Q049, 49 in all. By unit: dpm 2, edm 5, isp 3, mte 1, pbe 4, pds 10, platform 1, render 5, ta 1,
texture 4, transfer 4, usse 4, vdm 5. A question is removed when a record answers it.

### 4.2 Inferred glossary rows

`doc/open_rows.md` lists every glossary term whose status is `inferred`: its reading is a hypothesis
to test, and its name stays neutral (`REG_xxxx`, `BITSn_m`) until a test settles it. The groups
below gather those rows by what they rest on; `doc/open_rows.md` is the full list, with each row's
reading and records.

- **TA command words that load zero registers** (`CR_TA_REG_02B0`, `02B4`, `02D0`, `02D4`,
  `CR_TE_REG_02A8`, `CR_REG_0324` and `0364` to `0374`, `CR_USE_REG_0A04` and `0AA0`, with the
  `cmd_ta` words that load them). No value of any of them changes a triangle (E054); none is used
  as an address (E056) or disables culling (E182); the firmware writes all but `CR_TE_REG_02A8` at
  one site each (E245). They read as state a TA saves and resumes when it is interrupted (E183), a
  reading no run has tested, since none interrupts a TA. `CR_DPM_REG_074C` and its `cmd_ta` word
  are the exception: bit 8 faults the job, at the same BIF address for seven of eight values
  whatever the other bits, which fits an enable (E203, E206).
- **ISP registers and words.** 0x04e8 and 0x0800 change no transfer, depth scene or textured
  triangle at any value tried (E067, E068, E073), and 0x0800 bits 5:0 are not a pixel-task limit
  (E225). `CR_ISP_MSAA`'s mode gives three images at 0, 1 and 2 and hangs at 3, and its enable
  bit is needed at mode 2 (E210, E211, E220). The polygon offset factor (0x0420, render details
  word 6) at 4.0 leaves a flat triangle's depth as it is (E071). The render details word that loads
  0x0520 reads as the four sample positions (E214, E224).
- **Registers the init script sets.** 0x0810, 0x0814 and 0x0818 change no job (E006, E026; Q001);
  0x0a78 changes no image and its effect on time is unsettled (E045, E141; Q024); 0x0abc hangs every
  job when its bits 4:1 are 0, and our reading is a count of PDS task slots (E134, E140).
- **Per-job register words.** `CR_REG_0148` (Q043), and `CR_REG_0400` with the render details and
  transfer command words that load it: bit 25 inverts byte 3 of every pixel (E029), the other bits
  are Q044.
- **Render flags.** Bit 10's only test in the firmware adds one to the RT data set's executed count
  (E164, E166), and no image changes with it (E051, E052); bit 2 is Q041.
- **Words read from the firmware alone.** The per-render-target strides of the TA command, the
  render details and the RT data (E158, E163) and a PB block's first page (E200, E201) rest on what
  the kicks and the page-table builder do with them.
- **PDS and PBE words.** `DOUTU1.BIT2` changes no image, set or clear (E137, E138); `PDS_SIZE` bits
  17:16 move where o1 to o3 land (E139; Q023); EMIT2 bits 15:8 are Q040; the sideband's bit 9 is
  read as marking an emit that counts against a PBE tile (E239, E240), and its bits 8:6 are Q046.
- **Shader-side, texture and tiling words.** The punch-through feedback control (E083, E218), ISP
  word 1 and its line width (E117, E178), the user clip-plane enables (E096, E198), the pixel-event
  program's input bit 3 (E083), the scheduler's slot and task ids (E086), the sampler's `T3` bits
  26:23 (E034, E242), an object vertex's 1/w (E176, E196), the TPU's luma-key words and
  colour-space set 1 (E038, E039, E040), and the TE's macrotile stride (E159, E175).
- **VDM words.** The state word's open fields (Q015, Q037, Q047) and the index list's first trailing
  word (Q042).
- **Units.** `MADD`, the unit beside each USSE pipe's iterator and texture unit, has two readings
  (Q048).

Some open readings have no glossary row, so `doc/open_rows.md` does not list them: register 0x0740
(Q045), the render context's dword 7 (Q049), and dword 6 of the TA command, which changes nothing
at any value (E054).

### 4.3 Work that needs a capture host

Sub-phase 11.11 ran it. The laptop's Arch Linux 32 runs the closed GLES stacks natively under the
extraction harness, so it serves as the capture host: the 13 capture tables
(`captures/<unit>/<feature>.toml`, written from the harness's variation lists by
`cap3d_tables.py`, run by the campaign runner with `--target build`) hold 604 runs in
resgx545-data-private, the 28 `track3d` variations no earlier capture recorded among them. Each
topic below now has a record (E323-E351, tier CAP, with a run of our own stack on the laptop
beside the closed job where one word can be compared, `probes/render/closed-compare.toml`), and
what the captures leave open is a question:

- **texture:** YUV streams through colour-space set 0 or the USE coefficients (E341); the texture
  words per filter, wrap, format and size (E342).
- **pds:** the pixel PDS pointer and size words (E343; Q093); code-address words and bases of the
  vertex-side programs (E344); the pixel-side programs the MTE state names (E345).
- **render:** the render context (E323), the closing kick of each frame (E324), the RT data set
  (E325), a one-triangle job against ours (E326; Q085).
- **vdm:** index lists and vertex tasks (E346; Q092, Q094); block types (E349).
- **mte:** the presence word and `DOUTD1` (E347); region clip, viewport and cull (E348).
- **isp:** ISP words under depth, stencil and colour mask (E332); the background object (E334);
  the render details' 3D registers (E330); polygon offset (E338); 4x multisampling (E339; Q089);
  pass types and line widths (E340).
- **dpm:** the PB descriptor and block (E327; Q084).
- **ta:** the TA command (E328); the registers that move (E329); the macrotile rule over 222
  sizes (E331; Q086).
- **pbe:** the end-of-tile words (E333).
- **zls:** depth kept across frames (E335); the update list (E336); the control values (E337;
  Q088).
- **usse:** of the 46 open instruction forms the closed compilers use 14 (E350,
  `harness/ukernel-extract/opscan3d.py`); every vertex program opens with a load predicated
  never to run and a wait on it (E351, `opscan3d.py --guard`).

Three spec claims the ledger named without a topic are settled too: srvinit makes the same calls
and the same boot payload whatever `SGX_GETMISCINFO` answers (E352,
`captures/firmware/miscinfo-replies.toml`, srvinit under the harness on the laptop); the EDM
clears the interrupt flags itself (E353, from the EDM dataflow); and whether the EDM's own page
directory or the firmware's part in the sample-cache erratum matter is open (Q095, Q096).

What is still closed-stack only: the closed transfer and copy programs' words and the
pixel-event program the earlier phases left (no 11.11 table runs the OpenVG stack).

Sub-phase 11.12 settles two of the questions the captures left with an offline reading and the
laptop: `DOUTU1` bit 24 goes with an attribute the primary iterates into the attribute
registers, in all 114 captured fetching primaries (E364; Q093 keeps the hardware check), and our
own probes' textures, all in the general heap on the laptop's revision-3 bridge, sample as
expected, so the misplaced half of the sample-cache test shows no erratum (Q096 keeps the
texture-region half). The rest of 11.12 needed no capture host: the linux fork's held-recovery
and replayed-count follow-ups (E354-E356), the event, DPM, clock-gate and HWPerf registers
(E357-E359, E365), the BIF directory lists behind TA/3D control block dword 49 (E360) and
single-word pokes of a render's run (E361-E363).
