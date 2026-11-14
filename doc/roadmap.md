<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# resgx545 roadmap

resgx545 is published in phases, from the records and the firmware container up to the 3D state of a
render. Each phase brings its tools, its probe tables, its evidence records, its glossary terms and
its specification together, and the forks of Linux, radare2 and IGT gain the commits that pair with
it. This document says what each published phase holds, what the last phase, the pipeline simulator,
will need, and what is still open, unit by unit.

Note 2026-11-09: the phases below were built one by one from a notebook by a rewrite kit that is
retired now; their 61 commits keep the dates the kit fixed (2026-11-01, an hour a phase) and are
not rewritten. From 2026-11-09 work is committed directly, with real dates, under the workflow in
`HACKING.md`. The clean-room guard that section 2.0 lists for phase 0 was not in the repository
until now: it landed in 6b6f410 (`tools/clean-room/guard.py`), with its data in the private data
repository. Entries below that speak of overlays or of a build describe the kit's way of working
and are kept as they were.

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
triangle and fault recovery on the laptop); the question on the firmware's identity (answered by
E402) and, on the control block's mapping in
a client's VM, Q076. Sub-phase 6.1 brings the probe
tables by unit (`probes/<unit>/<feature>.toml`), the campaign runner that runs them on a clean GPU
and records the environment, the sweep runner with the ISP visibility counters around every case,
and what the runs show: evidence E025 to E124 on the platform, the EDM, the transfer, PBE, texture,
PDS, render, TA, ZLS, VDM, MTE, ISP and USSE, and questions Q008 to Q017 (and one on the copy's
buffers; the colour left in an output register is E373's).

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
Questions Q003, on what a fault leaves, and Q029.

### 2.10 Phase 10: the 3D state

`doc/specs/3d.md` gives the TA and 3D paths of the EDM and the state a render runs on: the render
context, TA command, render details, RT data and PB descriptor; the pick, the kick and the finish of
the TA; the scheduling, kick and completion of the 3D; the parameter buffer, the DPM and partial
renders; the VDM stream, the MTE state and the TA's output (objects, region headers, control
streams); the ISP words, depth, stencil, ZLS, multisampling, sample positions and punch-through; the
pixel-event program and iteration. Evidence: 85 records, E149 to E245 (RE for the firmware's paths,
HW for the state words, with `pbdump.py`, `pixels.py`, `region_tiles.py` and `vtx_tasks.py` to read
what the hardware wrote); questions from the sample-layout one
(answered by E1010 on 2026-11-13) to Q039.

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

The simulator is built in sub-phases 12.0 and on, as the crate `crates/sgx-pipe` over `sgx-sim`
(which stays as it is): a module for each unit above, each refusing, by the open questions that
block it, what no record measured, and a replay that holds it to unit vectors and scene vectors in
the data repository (`doc/specs/vectors.md`). A result by a rule a record states as a fit is
reported fitted, never matched. The paragraphs at the end of this document say what each
sub-phase did.

## 4. Open work by unit

### 4.1 Open questions

`doc/open_questions.md` lists every open question, generated from `questions/`: Q001 to Q192, 155
open (the two ids between Q132 and the test-field question, answered since by E1062, are reserved,
unused, and so is the one between Q181 and
Q183, and the six between Q183 and the layered-object question, answered by E971 on 2026-11-13;
the six ids after Q168 belong to phases not in this
tree). Each has a kind. The work is hardware knowledge, for a simulator and then our own firmware,
so the 139 `hw` questions are the work queue, each with a value (high 13, medium 68, low 58); the 10
`fw` questions (the closed firmware's and driver's own behaviour: Q004, Q029, Q034, Q049, Q084,
Q088, Q118, Q119, the one on the state between EDM tasks, answered later by E809, and the one on
two EDM tasks, answered by E752) and the 6 `kernel` ones (the
design
of our kernel driver: the firmware-identity one, answered later by E402, the one on the hung
job's object, answered later by E422, and Q095, the 4x fault question (since folded into Q003),
the one on `CR_EVENT_HOST_CLEAR`, answered later by E857, and the one on the module load, answered
later by E828) stay open, parked. By unit: bif 4, dpm
7, edm 13, isp 11, mte 3, pbe 5, pds 16, platform 5, render 9, ta 14, texture 14, transfer 3, usse
36, vdm 9, zls 6. A question is removed when a record answers it; one that mixed a hardware part
with a firmware or kernel part was narrowed to the hardware part or folded into the hardware
question that holds it (seven so far: the control block's per-VM copy and the render context count
bound into Q076, the recovery's reset steps into Q003, the settle routine and the two faults after a
base-only fault or a kept owner into Q036 and the state-page question (answered by E1080), the
points question into Q161), and a fold is
not an answer. What a fold or a narrowing left of the closed firmware's own behaviour is a new
parked question: how a kick tells its directory is in no list (Q118, from the render context count)
and whether a command with both kick flags acts as two (Q119, from Q065).

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
  (E164, E166), and no image changes with it (E051, E052); bit 2 keeps its owner through a
  later live context's job (E451); through a gone context bit 2 alone keeps it and the next
  render is exact, while after bit 3 a later render faults (E458, E462, Q036; the state-page
  question, answered by E1080).
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
- **VDM words.** The state word's open fields (Q047, Q163; E413 has the alternation of bits
  11:9 = 7) and the index list's first trailing word (Q042).
- **Units.** `MADD`, the unit beside each USSE pipe's iterator and texture unit, has two readings
  (Q048).

Some open readings have no glossary row, so `doc/open_rows.md` does not list them: register 0x0740
(the state-page question, answered by E1080), the render context's dword 7 (Q049), and dword 6 of
the TA command, which changes nothing
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
- **pds:** the pixel PDS pointer and size words (E343; E436); code-address words and bases of the
  vertex-side programs (E344); the pixel-side programs the MTE state names (E345).
- **render:** the render context (E323), the closing kick of each frame (E324), the RT data set
  (E325), a one-triangle job against ours (E326; answered later by E408, the rest in Q099).
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
registers, in all 114 captured fetching primaries (E364; E436 ran the hardware check), and our
own probes' textures, all in the general heap on the laptop's revision-3 bridge, sample as
expected, so the misplaced half of the sample-cache test shows no erratum (Q096 keeps the
texture-region half). The rest of 11.12 needed no capture host: the linux fork's held-recovery
and replayed-count follow-ups (E354-E356), the event, DPM, clock-gate and HWPerf registers
(E357-E359, E365), the BIF directory lists behind TA/3D control block dword 49 (E360) and
single-word pokes of a render's run (E361-E363).

Sub-phase 11.13 needed no capture host either: the USSE batch ran on the laptop over the cable,
14 probe tables (`probes/usse/destination-bank6*.toml`, `idiv-enc47*.toml`,
`encoding-gaps-end.toml`, `moe-faults.toml`, `moe-state.toml`, `hazards.toml`, `g19.toml`,
`globals.toml`, `leftover-o0.toml`, `idf-modes.toml`, `emit-flags.toml` and `loop-short.toml`).
The two words the simulator stopped on are settled: a bank 6 destination with no index bit
writes nothing a fill reads (E366), and `idiv`'s enc[47] is its repeat count's high bit
(E367), now a field the decoder prints and the simulator runs. A word no form decodes
ends the program when its enc[50] is set (E368, Q080); the MOE faults come from the template's
stores (E369, Q016) and the MOE state ends with its job (E370, Q051); a result is readable by
the next instruction with or without `.nosched` (E371, Q052); `g19` reads by the instruction
that reads it (E372, Q017); an unwritten output register keeps the last job's value, the
0xff00ff00 of the leftover-colour scene being the baseline triangle's (E373); the global registers
of a triangle's pixel task (E374, Q053), `idf`'s other modes (E375, Q055), the vertex emits' incp
and `.cut` (E376, Q054) and a fill's instruction cost, 0.3203 us per 2048 instances (E377,
Q002). The simulator matches 271 of the batch's 340 vectors and differs on none (E378). Q050 had no
run.

Sub-phase 11.14 needed no capture host either: the PDS, PBE and texture batch ran on the laptop
over the cable, 20 tables (`probes/pds/mov128-bit15.toml`, `douta-primary.toml`,
`fetch-pc-pad.toml`, `vertex-specials.toml`, `input-flags-overlap.toml`, `attribute-room.toml`,
`shade-order.toml`, `no-wait.toml`, `tile-slots.toml`, `pixel-event-word2.toml`,
`store-totals.toml`, `reg-0a78-timing.toml`; `probes/pbe/emit-transforms.toml`,
`sideband-channels.toml`, `reg-0400-alpha.toml`, `emit-twice.toml`, `pack-floats-channels.toml`,
`pack-floats-ramps.toml`; `probes/usse/store-sources.toml`; `probes/texture/copy-followup.toml`).
The PDS word the simulator stopped on is settled: `mov128`'s bit 15 writes the `ds0` pair the last
`mov32` or `movs` read from a data row (E379), which the simulator now runs after the instructions
measured (E400). A store takes `pa` and `sa` as its data source (E380; Q098 opened on a fill's
shared `pa`/`sa`); EMIT2 bits 29:28 rotate the stored image and bit 31 scales it by two (E382);
SIDEBAND bits 8:6 pick the channel in pack modes 7 and 8 only (E383); `CR_REG_0400`'s low byte is
ARGB1555's alpha threshold (E385); a double emit hangs a job of several tiles and on one tile
disturbs the later jobs until a reset (E386); T3 bits 7:0 are two signed texel offsets (E397); a
no-wait iteration never reaches `pa0` (E393) and E133's stale pixels do not recur (E392). The
four-component question (folded since into Q180), Q023, Q057 and Q008 had no run (the questions on
a DOUTU's width, on the copy's buffers and on T0's maximum level 15 were answered in 11.16: E428,
E425, E441).

Sub-phase 11.16 added the tool options the stuck questions needed to `sgxfive-test` and `probe.py`
and ran them with the fourth batch, on the laptop over the cable: `--blk` and `--cmd` with `N^=V`,
the VDM stream's words of a second object, `--pbe`, the background object's slots `bgpixel` and
`bgpds`, `probe --place` and `--scratch-heap texture`, `copy --ramp`, `--print-addrs` and
`--page-before`, and `tri --scratch-at`. Fourteen tables ran (`probes/ta/psg-state.toml`,
`vdm/state2-fields.toml`, `pds/doutu-place.toml`, `pds/no-wait-where.toml`,
`pbe/pack-floats-o23.toml`, `texture/copy-addresses.toml`, `luma-ramp.toml`,
`sampler-cache-texheap.toml`, `platform/event-steps.toml`, `event-fine.toml`, `hwperf-vary.toml`,
`render/bg-pds-map.toml`, `flag-bit0-timeline.toml` and `flag-bit0-dense.toml`). The copy's buffers
lie where the tool prints them (E425), and a DOUTU's bits 21:20 and CBASE both address (E428): both
questions are answered. The RT data's state bit 8 is reached by the existing kernel poke rtds:19 and
marks region headers as the command's bit 21 does (E424).

A second batch of 11.16 added to the tool probe --tri's wide scenes (`--vertices` up to 1500, the
rig's extra gen pages), the second object's primary PDS program (`--obj2-pixpds`), the target's
address for a replacement program (`0x5CB0nnnn`), the target's colours after an overflow, and probe
`--scratch-pages`, and `tex_words.py` an eight-level chain whose texels are the scratch buffer's own
dwords. Eight tables ran (`pds/iter-wait-textured.toml`, `dpm/partial-reload-pos.toml`,
`partial-wide.toml`, `partial-wide-timelines.toml` and `partial-reload.toml`, `isp/msaa-pbe.toml`,
`vdm/state2-consts.toml` and `texture/mip8-fields.toml`). In a textured primary the fetch wait
delivers the iterated coordinate set and the texel and `DOUTU1` bit 24 adds nothing (E436;
E454 and E460 found the same with the vertex colour and with coordinate sets on vertices that carry
their dwords, E459; 4 of 126 jobs with both bits hung, Q093), a `douti` of source 0
with two components is the pixel's x and y (E437), scenes of 100 to 500 triangles leave STATUS2's
high halves at 0 and set `TA3DCtl` dword 36 but hang small parameter buffers (E438, E443, a new
question), the 4x render through our
end-of-tile task with the closed driver's PBE words stores plain samples and does not resolve
(E439), a second state block's constant load reaches few pixels (E440), T0's maximum 15 reads level
0 while 8 to 14 clamp at the last level and MIPFILTER blends two levels byte for byte (E441: the
question on the maximum level is answered, non-square chains are a new one), and a background object
that reads the target back gives an overflowing scene's triangle its full pixel count (E442; the
depth readback stays open).

Sub-phase 11.21 made no run and no kernel change. It sorted the open questions by what they ask:
hardware (the work queue), the closed firmware's own behaviour, or the kernel's design, with a
value (high, medium, low) for each hardware question, and shows the two groups apart in the
generated view. Six mixed questions were folded into hardware questions, three narrowed to their
hardware part (Q033, Q094, Q096), Q065 was narrowed to the 3D's wait, two parked firmware questions
were split off (Q118, Q119), and ten new hardware questions open the gaps the specs left:
the page table flags and page sizes and the bus interface's tiled ranges (Q108 to Q110), which
event sets which status bit (Q111), the index list's width bits (Q112), cube maps (answered since
by E844), volume textures and anisotropy (Q114, Q115), the region clip as a scissor (answered since
by E1060) and points (folded into Q161 in 11.31; E544 answers its size and footprint).

Sub-phase 11.22 ran three tables on the laptop with no kernel change, about the depth and stencil
load and store (ZLS): `zls/store-layout.toml`, `store-format.toml` and `load-copy.toml`. The tool's
`tri` gained a full-target triangle with a depth at each vertex (`--tri-full`, `--tri-z`), so that a
ramp makes every stored dword name its pixel, fills that encode the dword's index
(`--depth-fill index`, `bit:K`), and separate store and stencil buffers (`--depth-store`,
`--stencil`, `--stencil-store`). The store window of E461 is the arithmetic of the tile pitch,
control bits 11:3 (E465); bits 26:24 are the stored format (E466); bits 1, 13 and 14 load, the
stencil and the depth (E467); and what an overflowed job stores is the first row of macrotiles as
zeros and the rest negated (E468). Q088 stays open as a firmware question (its hardware half is
answered); Q071, the bit-19 question (folded into Q069 since) and Q107 are narrowed; Q120 and the
stencil order's question (answered since by E988) are new, and so was the question of
the pixels past the target, answered since by E831.

Sub-phase 11.23 ran 15 probe tables on the laptop with no kernel change and no tool change, for the
integer and flow-control forms a compiler for our own firmware needs (`probes/usse/ima32-full.toml`,
`ima32-neg`, `imae-neg`, `compare32`, `compare32x`, `rot-imm`, `link`, `pclink`, `pflow`, `risky`,
and the programs placed in the code heap, `place`, `place-ctl`, `place-ctl2`, `place2` and
`place-link`). `ima32` is the low 32 bits of `a * b + c` on registers, 7-bit immediates and
constants, 826 of 826 cases (E469); a 32-bit subtract is one `ima32`, `.neg` on its sources 2 and 3
is a plain negation, and `cie, iN` adds bit 0 of `iN` only (E470); `imae` writes and takes a carry
and two chain into a 64-bit accumulate (E471). A test of a 32-bit register through source 2 tests
all its bits, but `iadd32`'s `n` and `p` and `iaddu32`'s nonzero test read the true 33-bit sum, and
a 32-bit compare is a six-instruction formula (E472, 64 of 64 pairs each); tests with an immediate
act on 32 bits (E473); the bitwise immediate is its 16-bit field rotated left by the five-bit
rotation field (E474). `pclink` holds 18 bits, a call stores the index of the instruction after it,
a predicated call with a false predicate still writes it (E475), and `lapc` lands on every index
run, which count from the code base the task started with (E476); no branch changes p0-p3, and p0-p3
and `pclink` are not reset between jobs (E475, E477). Planned cases that the tool refuses, programs
of over 256 words, were dropped (12), and the failed first runs of the placed tables are kept in the
data (`usse-place`, `usse-place-ctl`; the manifest of the first was written by hand with the
runner's digest function). Records E469-E477; Q052 is narrowed, none retired; Q123, Q125 to Q127 and
one for the firmware (`fw`, the state between EDM tasks, answered later by E809) are new.

Sub-phase 11.24 ran 14 probe tables on the laptop (355 cases, one campaign run each) and repeated
two ZLS runs by hand with their raw depth dumps kept, for the fence, store, register and emit
behaviour a compiler for our own firmware needs (`probes/usse/fence-batching.toml`,
`fence-growth`, `task-state`, `store-repeat`, `store-repeat-regs`, `store-repeat-regs2`,
`temps-max`, `temps-sparse`, `temps-past`, `temps-wrap`, `temps-bound`, `temps-bound2`,
`temps-bound3` and `emitpds`). The tool gained two changes for `emitpds` (a limm that names the
fill's PDS secondary, and `--pds` with `--coords`), copied forward with its tests. One `wdf drc0`
covers every load outstanding on `drc0`, up to 100 distinct `ldad` on one counter and 16
`ldad.fetch16` (128 to 200 `ldad` over eight registers reissue the same loads and cannot show a
lost reload), but a `wdf drcN` does not wait for the loads of the other counters (E478-E480; E479's
10 of 10 and 2 of 10 are scratch runs, one run being in the data), and a `stad` then a `ldad` of
one dword returns the stored value with no `idf`, all 2048 instances storing the same value to it,
so one instance's own store is not isolated (E481, Q134). `stad.fetchN` stores N registers to N
consecutive dwords; `stad.repeatN` and `ldad.repeatN` take `r(b + i)` as the pointer of iteration
`i`, the pointer movement read for `r40` to `r43` only (E482, E483). The temporaries sampled up to
`r123` are separate storage, a register at or past the allocation reads as the register modulo it
in most instances (88 to 99.6 percent) and a write was not seen to reach it, and of the `phas`
requests run 8 to 192 ran and 196 to 224, 252, 256, 508 and 1020 hung the job (12 values each, not
an interval; `r123` is the only register a request above 124 exercised) (E485-E487). Between two
fills the
temporaries, `i0`-`i2`, `p0`, `p1` and for one job an `sa` are what the job before left (E484). An
`emitpds` in a client fill starts the PDS program it names and ends the job in a fault or a hang
in all 24 cases (E488). These are fills, proxies for what firmware tasks do, and two requests are
not answered: two EDM tasks at once (answered by E752) and `str` then `ldr` (Q134). E489 and E490
recompute
E465 and E466 from the raw dumps, and E465 and E466 are carried forward with a dated note.
Records E478-E490; Q051, Q052, Q054, Q098, the bit-19 question (folded into Q069 since), Q107, Q120,
Q125 and the one on the state between EDM tasks (answered later by E809) are narrowed, none
retired; Q128 to Q134 are new, the one on two EDM tasks (answered by E752) for the firmware (`fw`).

Sub-phase 11.25 ran 13 probe tables on the laptop (1526 cases, one campaign run each, the false-call
table twice) with no kernel change and no tool change (the sgxfive-test of 11.24), for the open
cases of the 11.23 review (`probes/usse/callfalse.toml`, `callfalse2`, `place-more`, `ima32-forms`,
`compare32-pad`, `iaddu32-pairs`, `pclink-repeat`, `pa-dest`, `raw25`, `rawcond`, `rawcond2`,
`ima32hi` and `ucmp2`). A call that is not taken writes `pclink` (16 of 16 not-taken calls of a
fill, 3 of 3 in a chain, 10 of 10 jobs of five placed programs: E491), where the model said it does
not; the code base moves in steps of 0x80000 bytes at ten placements, seven of them not multiples of
it (E492). `ima32.u d, iK, a, b, c` writes the high 32 bits of the product with the addend to `iK`
(15 of 15 cases of five `.u` register triples), where the model kept the `i` registers, so a
subtract gives its borrow in one `ima32` and an unsigned compare is two instructions on the 64 pairs
of eight values run, unsigned and not padded (E493, E501); the raw words run for that field changed
nothing seen except that bit 46 changed `r14` (3 of 3 jobs, open: Q127). `cie` adds bit 0 of `iN`
for `i0` to `i2` and eight values (E494); 17 more immediates, `.neg` on `.s` immediates and
constants and dependent readers up to 8 nops are exact (E495); `ima32` writes `sa0`, `o0`, `i1`,
`i2` and the six r-bank destinations run (r0, r9, r18, r28, r30, r31) but not `pa0`, as `mov` does
not, and its sa0 write persisting to the next job is not separated from the colour rule (E496); the
signed compare is exact padded (E497); `iadd32`'s `n` and `p` read the true sum and `iaddu32` reads
the carry (E498). Bit 43 of a class 9 test word is the `pat` bit of the test field, not an invert;
the field's two parts are ANDed under the `a` join on chan0, the only join and channel in all 732
raw words run (a rule read out of 90 cases and then predicted 450 of 450 on other forms; the `o`
join was not run: E499). Four runs of the `pclink` readers show 64 pixels of 0xeb3 in 29 of 40 jobs
and quads that repeat in part (E500). The records state the pairs and values that ran and count
programs and jobs apart where one program ran twice. E469 to E473, E475 and E476 are carried forward
with dated corrections where 11.25 answers what they listed as not run. Records E491-E501; Q052,
Q098, Q123, Q125, Q126 and Q127 are narrowed, none retired; Q136, the ima32 high-word question
(folded into Q127 since) and the test-field question (answered since by E1062) are new.

Sub-phase 11.26 ran seven script tables on the laptop (the identity maps of multisampling, the TA
output under the TE anti-aliasing bits, the macrotile words at six sizes, the 4x render of our stack
and the sideband bits under it; `probes/isp/msaa-ident.toml`, `msaa-te-dumps`, `msaa-resolve`,
`probes/ta/mtile-fields.toml`, `mtile-fields-risky`, `mtile-msaa`, `mtile-msaa-risky`) with no
kernel change and one tool change (`probe --tri --tri-full`, the sgxfive-test of 11.26). 531 of the
552 declared jobs ran, one run each; 21 did not (20 poked 4x cases at 320 x 160 and larger and the
1024 x 768 render, since the unpoked 4x render faults from 320 x 160, E507), and three of the
scripts ran in a resume with a longer recovery path. The pixel program's iterated position is x +
0.375 and y + 0.125 in modes 0, 1 and 2 (E502). A multisampled render stores in each 32 x 16 tile a
half window of the tile's own area, chosen by `CR_TE_AA` bits 31 and 30, each pixel twice in x and
in y in mode 2 (E503): a rule read post hoc from the 64 x 64 runs after the declared test decoded
nothing (0 of 48), which then agrees with all 634 tiles of the sizes declared held out (E503), and
E415's "4 pixels" were the doubling [infer] (E415 is carried forward with a dated correction). Bits
30 and 31 change 76 and 132 dwords of the parameter buffer and TA data, the closed driver's 4x
setting stores 1024 distinct pixels of a 64 x 64 target, and no single bit of the end-of-tile
sideband resolves (E504, E508, E510). At two macrotile columns the second boundary of the macrotile
words decides, at four B1, B2 and B3 are all read, the stride must be the rule's, and none of the
declared readings PA, PB and PC fits both (E505, E506, E509); the closed driver's 64 x 64 words draw
exactly at 96 x 48 and 128 x 64 and fault at 128 x 128 and larger (E511). Records E502-E511; the
sample-layout question (answered by E1010 on 2026-11-13), Q086, Q089 and Q100 are narrowed, none
retired; Q089 to Q142 are new, one for the kernel's 4x faults (since folded into Q003).

Sub-phase 11.27 ran 32 probe tables on the laptop (2027 cases, one campaign run of each, no probe.py
run first) with the sgxfive-test of 11.26 and the 11.19 linux fork, no kernel change, for the open
cases of the 11.24 and 11.25 reviews. A first batch (16 tables, 291 cases:
`probes/usse/store-own*.toml`, `repeat-ptrs`, `load-readers`, `reload-growth`, `phas-low*`,
`phas-high-*`, `phas-mod`, `emit-addend*`) followed up the memory, repeat, load, `phas` and emit
records. An instance sees its own unfenced `stad` and its store changes the dword the host reads
with no fence (2048 of 2048 pixels in each of nine cases, E512); a branch on a test of `pa0` is
taken by a whole 2 x 2 quad from its top-left lane, so the one instance selected that way was four
lanes (E513); another instance's store is read by a later load when that instance ran earlier and in
part when it runs later, and no case needed an `idf` (E514). On a repeat of 5 to 16 the pointers
`r(b + i)` move by the form's increment, `r44` to `r55` included, and the others stay (50 of 50
cases, E515); `stad.fetchN` stores from `b + k + 1` (plain and pre-increment) or `b + k`
(post-increment) and moves `rb` by N (E516). An ALU reader sees a load's old value up to 48 `nop`s
and a load lands over an earlier `mov` (E517); up to 192 distinct-line `ldad` on one counter, with
no reload seen lost in the 4 or 5 reloaded registers read per job (7 of 7 jobs, E518). A `phas`
request runs when it is 4 to 192 modulo 256 and hangs the job when it is 0 or 196 to 252, predicted
for 15 of 15 requests from 512 up (E519). The addend of an `emitpds` control word matters (0xFFF to
0x2000 leave the fill's own value in 12 of 12 probes), and all 39 emitting jobs faulted or hung
(E520). A second batch (16 tables, 1736 cases: `ima32hi-generic`, `ima32hi-signed`, `ucmp2-random`,
`ucmp2-pad`, `scmp`, `rawjoin-o*` and `rawchan-1` to `7`) ran the cases of the 11.25 review. The
high word of `ima32` is bits 63:32 of the exact product with the addend on generic register
operands, `.u` and `.s` (282 of 282 jobs each: E525, E526); the unsigned two-instruction compare is
exact on 252 of 252 seeded pairs and padded with 0, 1 and 3 `nop`s (E527), and a signed one from
`ima32.s` on 164 of 164 pairs (E528). Under the `o` join the two parts of a test field are ORed and
an absent part counts true, a rule read from 90 readbacks and predicted on 270 of 270 more (E529);
the chan field 1 to 7 is not ignored by a test of a 32-bit value, so write `chan0` (E530: 252 cases
that fit the Test channels rule when read after the data). 17 probe runs read NONE (the table's
hypotheses did not fit; each is stated in its record, the first runs kept), and the records say
which rules were read after the data and which were predicted. Records E512-E520 and E525-E530
(E521-E524 are kept for a later phase); E478, E480-E483, E487, E488, E493, E499 and E501 are carried
forward with dated corrections where 11.27 answers what they listed as not run. Q051, Q052, Q128,
Q133, Q134, the ima32 high-word question (folded into Q127 since) and the test-field question
(answered since by E1062) are narrowed, none retired;
Q143 to Q146 and two more, since answered by E1062, are new
(all hw, Q143 medium, the others low).

Sub-phase 11.28 made no run and no kernel change, and the data repository's raw readbacks are the
ones 11.27 left. It brings the USSE model of `crates/sgx-sim` up to what 11.15 to 11.27 found and
checks it against every usse run that had no vectors: 338 vector files (5815 vectors, 5750 of the
USSE and 65 of the PDS) of 74 tables of 11.23 to 11.27, converted by
`tools/usse-asm/convert_extra.py` from the recorded `bins/` and the tree's own probe tables, into x.
Over the 34510 USSE vectors the replay gave before the change 28002 matches, 218 mismatches (all in
the new files) and 2873 stops; it gives 30260 matches, 1112 fitted, 908 stops and 0 mismatches, 175
skipped, 1925 left out of the replay (the triangle host's readback, mixed pixels, a failed job) and
130 jobs that hung, 48 of which the simulator now predicts by stopping on the `phas` request that
hangs (E519). Of the new files' 5750 USSE vectors 5406 match, 135 stop, 9 are skipped (another
instance's unfenced store, E514), 156 are left out and 44 jobs hung (42 predicted); the data
repository's own 28760 are unchanged. One vector went from a match to a stop on purpose
(`usse-ima32-forms-dest__20`: a write to a `pa` is lost in a fill, E496, so the read back of it
stops). The 65 PDS vectors of the `emit-addend` and `emitpds` runs are skipped: the job faulted or
hung in the task an `emitpds` started (E488, E520), which the simulator does not model. The model
gains: the integer forms `ima32` and `imae` with `cie`, `.neg` and the high word (unsigned and
signed), the `o` join of the test field, `iadd32` and `iaddu32` tests on the true and the carried
sum, `pclink` of 18 bits and the unset predicates and `pclink` of a task, `phas` with the wait
`none` and the request modulo 256, `stad` and `ldad` repeats and fetch stores, a program placed in
the code heap with its code base, and refusals for what no run covered (the `vcull` and `pt` waits
in a pixel task, a write to `pa1`-`pa4`, a `.neg` on an immediate, and others). `sgx-sim` takes
`--task vertex` and `--set pclink=N`, and `examples/replay` lists the outcome of every vector. E522
records the replay (the simulator against the vectors, offline); E521, found in it, shows that the
value `iaddu32` writes zero-extends source 1 (16 pairs in two datasets run before, seven of which a
sign extension writes otherwise): Q126 is narrowed to the extension its test reads and to the forms
not run, none retired; Q132 is new (hw, medium: where a write past a task's allocation goes, which
E486 and E519 do not settle together, 30 vectors stop on it). The two ids between Q132 and the
test-field
question stay reserved. The ZLS and the multisampling are not in the model: they stay for phase 12.

Sub-phase 11.29 ran our own firmware (EDM) tasks on the laptop for the first time, over the cable,
with the linux fork tip d614af574cc6 (three debug-only commits, 43 to 45, on 6ee9501832af, reworked
since to tip 3d9b8bdefe94: series check 6 of 6, KUnit 106 of 106 with the debug option off at each
commit and 157, 164 and 172 with it on), module srcversion 7ED723C25D78D7FCB3C08C1: 16 run
directories in the data repository, a start dword of PDS #13 pointed at a page of our code at load
time, the general slot only, 32 temporaries, two registers written (0x0814 and 0x0a78). They are
firmware tasks, not client pixel tasks. The wrapper that only jumps to the closed general task left
the EDM as it was (E531); a `stad` from a task lands, and the tick hands the task `pa0` = 2, `pa1` =
0x02000000 and `pa2` = 0x01061a70 (2 of 2 runs; the prediction that `pa1` is 0 was falsified, kept
apart from the stage's own criteria, E532); `ldr` reads `CORE_ID` and `CORE_REVISION` as the host
does, and the tick stopped after a writer that wrote `sa`, `r`, `i`, `p` and `pclink` state and
ended with `nop.end` instead of the closed task (1 run, the stage's trigger; one reset recovered;
the skipped closed task and the writes are not separated; E533). The answer for the toolchain's 9b:
for 0x0814 and 0x0a78, `str` then `ldr` was ordered with no fence in 318 of 318 runs, four fresh
loads (228 of the 306 matrix runs could tell a landed `str`, 138 on 0x0814 and 90 on 0x0a78; E534).
Not measured, because the stage for item 12 stopped on its trigger: persistence between tasks
(answered later by E809),
task overlap, the largest allocation, and the event words of a kick and a job (Q033). The simulator
models `ldr` and `str` for a firmware task only: `str` to those two registers (inside their 17 and 6
bits, the immediate index only) and `ldr` of them and of `CORE_ID`, `CORE_REVISION` and `CR_TIMER`
as a vector seeds them (the timer never advances; no vector of the 318 reads the first two, so unit
tests alone cover those), and refuses the register-index forms and an index above 14 bits; it
replays the 318 runs as vectors (`vectors/nokernel/usse/fwtask-9b`, tracked in the data repository
from b5075fa3); its replay of the other vectors is unchanged. `tools/fwtask` and `asm/fwtask` are
ours, with the clean-room checks of HACKING.md. The kernel's verifier in the module of these runs
had bypasses, found afterwards by a review of the fork commits and fixed in later ones; the tasks
that ran contained none of the forms, so the runs stand. The recheck on the rebuilt module
(srcversion 5AD04F33F6BCDA7B880E238, tip 3d9b8bdefe94) is done: the tasks passed the fixed verifier,
the code page read-only in the EDM's page directory was fetched from, and the 9b repeat read the
same, 34 of 34 (E549; the module-load KUnit failures on the laptop were a kernel question, answered
later by E828). Records E531-E534 and
E549; Q134 and the one on two EDM tasks (answered by E752) are narrowed (Q134's client `str` and
`idf`
parts, the overlap) and none retired; the one on the state between EDM tasks (answered later by
E809) and Q033 gain their evidence and stay open; the one on the end of a pass (answered later by
E836), one answered later by E746 and Q154 are new (hw: medium, low, medium), and one kernel
question (the module load, answered later by E828).

Sub-phase 11.30 ran more firmware (EDM) tasks of ours, and the client rerun of Q132, on the laptop
with the module and fork tip of 11.29 before the verifier fix (module 7ED723C2, tip d614af574cc6;
data commit b5075fa3, which does not hold its vectors): 7 run directories of firmware tasks (stage
B, stage B2, three runs of the event stubs, the slow task, the temporaries) and 2 of client fills
(E535), and an eighth directory of firmware-task data for the stock check after the last stage. They
are firmware tasks except E535. The runs used the module whose verifier had bypasses, fixed
afterwards (the overlay was reviewed before the 11.29 re-check): the fixed verifier was not used for
any run, and 21 of the 22 blob names of the 11.30 runs reassemble here to their recorded hashes and
are accepted when checked offline (`state.blob`, the 11.29 task that wrote `pclink`, was not
reassembled: its source as it ran is not in the tree, and that the fixed verifier refuses it is
[infer] from its rule on `mov pclink`). A writer that called the closed general task after writing
`sa`, `r`, `i` and `p` left the tick running, and the next task read what it wrote for `sa100`,
`sa127`, `sa20`, `sa24`, `r20`, `r21`, `i0` and `i1` at the next event and after 1200 ms, and for
all but `r20` and `r21` after a client fill (E536: 3 of 3 rounds; the stage passed on its own
criteria and of its 10 frozen rows 4 held on their claim, 1 formally and 5 failed: `sa64` did not
take the write, `r20` and `r21` persisted, `pclink` was 6 at the next entry, the value of the
writer's own tail triple [infer], and p1 was the writer's; p2 and p3 move between readings with no
writer and show nothing). The stage's tool crashed after the hardware part and the rows were judged
again offline from the saved data. A second writer, which also wrote `sa63` and `sa65` and called
the closed task, was not followed by its armed reader within 100 ms (E537: one run; HostCtl dword 12
advanced 6 in that window and then did not move; the stage stopped at its first writer and the 11
other writers of its plan did not run). Together they narrow E533's stop only this far: the `sa`,
`r`, `i` and `p` writes alone do not stop the tick when the closed task follows, and a task that
calls the closed task can stop it too; E533's arbitrary `pclink` write, its p values (1, 0, 1, 0)
and the missing closed task are still not separated (answered later by E836). A host kick reached
the general
slot only, with `pa1` = 0x03000000 (E538: 3 of 3 runs; the frozen prediction 0x100 failed, which
E746 later read as the tick after the kick, see E538's correction) and 50 ms
of ticks logged nothing with bit 25 masked. A slow task of up to 6.9 ms was never found busy by a
second pass that started after its busy store (E539: 10 of 10, a tick-only stream in one slot). TRC
8 to 31 gave real storage up to the top register and the register past the allocation did not hold a
marker written to it (E540: 6 of 6, 0 of 5, one job and one read per T); TRC 32 and above, and
Q033's TA event, were not run (the arm of 32 failed with its error cut off, [infer] at the fork's
hazard gate, and arming with the hazard word was not made). The client rerun (E535, 36 jobs with a
marker of its own per job) shows that a write to `r123` is not seen under a request of 100 or less
(0 of 12 jobs: all pixels of run a's six, the listed pixels of run b's) and lands under 124 or more
(24 of 24), so E519's read-back was a landed write, E486 and E519 do not disagree, and, [infer], a
request of 260 to 376 allocates at least 124 registers and not its value modulo 256; Q132 stays open
(two of its three runs, and where a dropped write goes, were not run). The simulator gains the entry
state of a firmware task (`sa`, `r`, `i`, `pa`, p and `pclink`), its temporaries and the state it
must leave, and refuses a read of `sa64` after a write of it, a state key that is no register and a
wrapper that runs past 3 000 000 steps; 31 more firmware vectors replay exactly (349 in all; the
readers' vectors are seeded with their own readback, so they say nothing of persistence, and the
writers' readback lists only p1 of the predicates) and so do 14 of the 36 vectors of E535 (12 are
left out for their mixed pixels and 10 stop on `r123` past the allocation, which the simulator takes
from the modulo rule); the replay of the other vectors is unchanged (30081 scalar and 193 pixel
matches, 1112 fitted, 918 stops, 175 skipped, 1937 left out, with 0 mismatches). Records E535-E540;
the one on the state between EDM tasks (answered later by E809), the one on two EDM tasks (answered
by E752), Q133, Q132, the one on the end of a pass (answered later by E836), the one on bit 25 of
pa1 (answered by E746) and Q033 are narrowed and none retired; Q158 and the one on bit 24 of pa1
(answered by E746) are new (hw: low, low), and two more new hw questions (medium, medium) were
folded into the one on the end of a pass and are now part of Q294.

Sub-phase 11.31 ran seven script tables on the laptop with no kernel change, all in the 11.26 tool
(sgxfive-test-1126): the TA's object format and its vertex dwords (`ta/object-format`), the region
test of triangles at tile boundaries (`ta/tri-region`), lines (`ta/line-point`), points and OUTSEL
(`ta/points`), the vertex task's capacity (`vdm/vtask-capacity`), VDM_STATE1 in a two-block stream
(`vdm/state-units`) and the event bits of ordinary jobs (`platform/event-bits`): 732 jobs in all.
Eight evidence records (E541 to E548): the vertex dwords and masks follow the coordinate size and
format words (E541); the triangle region test holds at every tile boundary tried (E542); lines run
and their region list is a thickened segment (E543); a point's size is the vertex's first coordinate
output under OUTSEL bit 8 and the 3D covers a square of it (E544); the VDM_STATE1 fields flipped
move the marks of a block together and a job's completion is not a function of its state word
(E545); a vertex task keeps its vertices when R * V <= 32 and loses or repeats some at 36 or more,
at 33 by program (E546); the short pulses of the event bits are 4.2 to 6.1 microseconds, held by the
firmware's acknowledgement [infer], and seven of them raised a host interrupt of their own in a
triangle (E547, E548). The points question is folded into Q161 and retired (E544 answers its size
and footprint for our program; the closed driver's row is Q161); Q070, Q047, Q092, Q094 and Q111 are
narrowed; eight questions open (Q159 to Q165 and the one on `CR_EVENT_HOST_CLEAR`, answered later by
E857; hw: medium, low, low, low, medium, low, low for Q159 to Q165, and that one kernel, parked: it
needs a kernel change). The TA and VDM models of the simulator
(region test, object format, points, vertex-task capacity) wait for phase 12; nothing here touches
the USSE, PDS or texture models, so sgx-sim is unchanged and the vectors are the same. The roadmap
counts the questions from the built `doc/open_questions.md`: 143 open (ids up to 167), 127 hw (high
13, medium 65, low 49), 10 fw and 6 kernel; ta 14, vdm 9, platform 5.

Sub-phase 11.32 ran the sampler of the texture unit in a fill of our own, 456 jobs of 2048 pixels
(2026-11-09, one program, each pixel one `smp` of a texture whose dwords name themselves), and ten
firmware-task jobs with `trc_hazard=1` (E550). The sampler tables: the first `smp` in a coordinates
fill read the declared image in 4 of 4 controls (E560); twiddled 32-bit textures with a side above
16 lie in tiles of 16 x 16, interleaved as before, the tiles in raster order with x first, a law fit
on 28 of 28 windows that also gives E441's levels 0 to 2 (E561); a non-square chain halves both
sides down to 1x1 and the T0 fields read it as a square chain (E562: 8 of 8 fit and 49 of 49
held-out jobs); the LOD of a gradient is a logarithm of a footprint that fits the largest component
on some cases and the Euclidean length on others, its fraction truncated except at one column
(E563); the declared bilinear baseline failed its control, so no anisotropy result stands (E564);
address modes 6 and 7 clamp and 4 and 5 repeat along v while modes 4 to 7 along u read other texels
(E565); T3 bits 0 to 7 are offsets in `smp` at every value tried and bits 10, 14, 18, 27 and 28 act
by position (E566); `smp3d` ignored the third coordinate on the types and sizes it ran on and
TEXTYPE 2 does not (E567); the YUV formats read black in a fill whether or not the colour-space poke
was given, and of three block orders only one fits format 27 (E568); 28 triangle jobs of the
four-component probes all hung (E569, Q180). The firmware task armed with TRC 32 to 48 and the
hazard word ran in 10 of 10 jobs and read its marker back through `r123`, a register that exists at
TRC 31; nothing above `r123` was tested (E550, Q168). Records E550 and E560-E569. The simulator
(`crates/sgx-sim`) gains the E276 and E441 level fields, the tile law for 32-bit twiddled textures
in the 14 sizes run, the non-square chain in the five sizes run, `smp3d` as `smp2d` only on the
point-sampled textures it ran on (the rule refuses TEXTYPE 2 itself), TEXTYPE 7 at 16x16, and the
YUV formats as black only for a job whose recorded pokes leave the colour-space set unloaded
(`init.job.pokes`); everything else of these tables stays unsupported with a reason. Of the 425
vectors (456 jobs less the 28 triangle jobs and 3 that failed) 241 replay exactly, 184 stop and none
mismatches (the draft's 241 of 425 is the figure; `plan.md`, which is kept as declared, still says
141 of 428 for the state before the simulator patches); the replay of the landed vectors is
unchanged (30623 pass, 1112 fitted, 918 stops, 175 skipped, 1937 left out, 82 and 48 hung, 0
mismatches), the eight YUV texels of the landed formats-other vectors still stop. The mip-chain
question (answered since by E1052) is narrowed to the 1D, side-of-1 and non-32-bit cases, the T3
bits
question (answered since by E1067), Q050, Q115, the cube-map question (answered since by E844), Q114
and the four-component question
(folded since into Q180) are narrowed or carry their evidence and none is retired; Q168,
Q177 to Q181 and two more (the gradient footprint, answered later by E721; the T3 address bits,
folded later into the T3 bits question, answered by E1067) are new (hw, low). The roadmap counts the
questions from the built
`doc/open_questions.md`: 151 open (Q001 to Q181), 135 hw (high 13, medium 64, low 58), 10 fw and 6
kernel; edm 13, texture 14. The replay of the tree's data, with the 17 new vector files in the data
repository: 30864 pass, 1112 fitted, 1102 unsupported, 175 skipped, 1937 left out, 82 and 48 hung, 0
mismatches.

Sub-phase 11.33 ran 14 script runs on the laptop with no kernel change and no tool change, all in
the 11.26 tool (sgxfive-test-1126): where the output registers o1 to o3 of a pixel task land
(`usse/output-room-tiles`, 68 jobs), the global registers of a vertex task and of the end-of-tile
task (`usse/globals-vertex-eot`, 65 jobs), the buffers the client directory's alias needs
(`bif/alias-skip`, 30 case runs) and the DPM status registers through overflowing scenes
(`dpm/bit2-grid`, 36 jobs): 199 jobs in all. Five evidence records (E570 to E574): o1 lands at the
pixel's own place in the tile one position later in the raster order of the target's tiles in 91
percent of 6995 pairs, the order of the region headers in 87 percent, and neither is a rule at every
shape (E570); a vertex task's global registers, 125 of 126 vertices read in full in each of 12 jobs,
are constants, a mask pair and rules of the task and the lane (E571); a store of a global register
in the end-of-tile task lands and the job then faults, at one of three addresses (E572); only buffer
0 of the EDM's buffers faults the first job when left out of the client directory's alias (E573);
STATUS2's high halves and register 0x0740 read 0 in 36 jobs and 0x0748 bit 2 clears in 5 of them,
one reading each, about 29 microseconds apart (E574). Q053 is narrowed to what has no rule (a vertex
task's g18 and g21, each tile's end-of-tile registers), Q183 is new (the fault after a store in the
end-of-tile task); Q023, Q036, the state-page question (answered by E1080) and Q076 are narrowed.
Not run: Q066, the state page's reader
and page 0x20003000 (now Q191), the client directory against BASE1 in Q076. sgx-sim gains a vertex
task's global registers (twelve hardware vectors; it refuses the registers and draws not measured);
the fixed-function DPM and BIF models wait for phase 12. The roadmap counts the questions from the
built `doc/open_questions.md`: 152 open, 136 hw (high 12, medium 66, low 58), 10 fw and 6 kernel.

Sub-phase 11.34 is a kernel sub-phase and the laptop batch that waited for it: three debug-only
commits of the linux fork (46 the kpoke space `bg`, 47 debugfs `render_keep`, 48 debugfs
`render_kept`, series check on the laptop 6 of 6) and 213 job runs in 7 scripts with the 11.26 tool,
no clock-gate register written. Three evidence records (E590 to E592): in a 64x64 one-triangle
render no poke of the words 3 to 16 of the background object, ten values a word, changes the image,
so the ISP is not shown to read them in that scene, and the words 0 to 2 can be shown neither read
nor not read (E590, Q066); with the first context's mappings, slot and memory kept the render after
a kept DPM owner is exact (13 of 13) and the kept pages hold words stored after it (E591; the
state-page question, answered by E1080); the
page-directory word of a render context equals the list register the kick wrote in 15 of 15 jobs,
BASE1 after a reset (E592, Q076), which also corrects the landed statements that it was not
comparable. Q066, the state-page question (answered by E1080) and Q076 are narrowed and none is
retired, the kernel question on the module
load is narrowed (the amended module's load failed three cases on an order-5 allocation failure, the
first kernel line for the allocation reading; no load was on a fresh boot), and three questions are
new
(hw: the object with texture layers, answered by E971 on 2026-11-13; Q191, the stored words; Q192,
the partial owner's page). The kernel switch
that would fill the second context's state page between two contexts' renders stays open
(`tadata_fill` is taken by the first kick after it is armed). The roadmap counts the questions from
the built `doc/open_questions.md`: 155 open, 139 hw (high 13, medium 68, low 58), 10 fw and 6
kernel.

Sub-phase 11.35 is a tool and records sub-phase after the audit of the laptop capture path, with two
short laptop runs and no kernel change (the module of 11.34's amended tip, sgxfive-test-1135, a new
build of the tool). Tool fixes, each with its test: stdout line-buffered so that a failure message
on stderr no longer lands inside a dump's rows, `probe` and `probe --tri` exit 3 on a failed job,
the campaign runner prints, records and compares the installed and the loaded module's srcversion
and refuses a mismatch, a check that flags tables writing the same marker to the same register in
more than one job (14 tables, the audit's list), the tool's `more changed` count readable and
statable in a table, the repeated-label reset of `parse()`, and a reset between jobs. Two reruns
with a marker of its own per job and the predictions hashed first: E485's 25 jobs in both orders
read their own markers in every register read, 742 of 742 values a run (the 8 to 30 registers past
the 32 shown in the 10 temps-max jobs with T >= 80 were counted, not read; E593: E485 stands for the
registers read, and the declared falsification criterion of the stale-read prediction fired in 2 of
the 50 jobs), E487's 8 jobs that could have been stale reads read their own (E594), and the job that
reads a register it does not write read earlier jobs' values after a GPU reset in front of it (Q193,
new). Corrections with measurements kept: E511 (the 47 pixels are the tool's edge tolerance, not
pixels lost to the inserted message), E507, E485, E487 and E512. The replay of the tree's data with
the 28 new vector files, from the coverage json by name (pass, unsupported, mismatch): scalar 30137,
2013, 0 (30081, 2012, 0 before), pixels 434, 202, 0, PDS 1305, 98, 0, firmware 349, 0, 0, 1112
fitted; on 11.34's basis 30920 pass (30864 at 11.34). The roadmap counts the questions from the
built `doc/open_questions.md`: 156 open, 140 hw (high 13, medium 68, low 59), 10 fw and 6 kernel.

Sub-phase 11.36 is a records sub-phase with laptop runs and no kernel change, for the items 7 to 13
of the firmware toolchain's second requests: 678 client pixel jobs (compares, predicated forms, the
high word of `ima32` with repeated registers, narrow memory) and 124 jobs in firmware tasks of ours
(test immediates, predicates, one `wdf` over many loads, registers r0 to r123), the predictions
hashed before the first run, 15 of 19 rows run (the other four not run) and one failed (the control
of E602, Q194). The client results hold on every case run (E595 to E599); in a firmware task the
test immediate is exact for n = 0 to 127 (E600), `p0 mov r, #n` and `p0 br` follow p0 (E601), loads,
one `wdf` and stores is sufficient for 2 to 100 loads without the `wdf` being shown to wait or to be
needed (E602), and every register r0 to r123 is storage for `ldad` and `stad` (E603). The simulator
models the narrow memory forms as run and refuses what did not run (flags, banks, negative or
register offsets); by name in the coverage json (pass, unsupported, mismatch): scalar 30815, 2013,
0, pixels 434, 202, 0, PDS 1305, 98, 0, firmware 470, 0, 0, 1112 fitted; on 11.34's basis 31719 pass
(30920 at 11.35). The roadmap counts the questions from the built `doc/open_questions.md`: 159 open
(Q001 to Q196), 143 hw (high 13, medium 68, low 62), 10 fw and 6 kernel; usse 38, edm 15.

Sub-phase 11.37 is a records sub-phase with laptop runs and no kernel change: the last two stages of
the firmware-task requests (f15, f14a) and a sweep of 1536 random sub-pixel triangles with vertices
in 1/256 pixel (3112 jobs, plus a fine set of 874 and a second fine set of 422 for the vertex
rounding). In a firmware task `str` then `ldr` of the two allow-list registers read back across the
start of a client fill (E604, the overlap itself not measured) and the four-slot task with a held
slot 0 gave no overlap flag and no pass in slots 1 to 3, with the pass-against-tick count not
decided (E605). The ISP covers a pixel iff its centre is inside the triangle, the edge test exact
and left and top edges owning a sample on them, 0 of 14368768 pixels wrong inside the envelope
tested (E606: vertices about -9% to +124% of a target of power-of-two half-size up to 256 x 128, w =
1, a single sample); the depth and the iterated coordinate set equal the exact plane at the pixel
centre up to an absolute error in units of 2^-23, not bit-exact and systematically low; and the ISP
rounds every window coordinate (x >= 0) to the nearest 1/256 pixel, ties up, before it tests the
centres (E607). The simulator is unchanged. The roadmap counts the questions from the built
`doc/open_questions.md`: 165 open (Q001 to Q202), 147 hw (high 15, medium 69, low 63), 12 fw and 6
kernel; usse 38, edm 17, isp 15.

Sub-phase 11.38 is a records sub-phase with one laptop batch (225 jobs over the direct cable) and
no kernel change, on the dynamic parameter management and the partial renders. A one-triangle
scene overflows exactly when the first abort's status is below its whole-buffer page need (19
pages at 1024x768, 287 at 4096x4096, measured), the partial-render count fits that need plus a
constant k of 2 to 13, and the threshold raise by 0x20 follows a rule read after the runs (E625);
the pool's page table walks to all pages after every render and a render writes the head pages of
the previous walk (E626); the state page holds the abort's lists when the threshold is not raised
and, approximately, the lists built after the last partial render when it is (E627). In a job that
overflows the depth store holds the load buffer whatever the control, the load buffer comes back
zero in the first row of macrotiles, the zero rows are not one rule across sizes and the depth
test runs across the partial render (E628); the stored depth's sign follows the raise, a
correlation with P and the scene (E629). Two of E438's three hang cases log the kernel's hung line
with the recovery held and end as overflows (E630, the watchdog reading an inference), and a kept
partial owner's state page is zero after the second context's run, cause not separated (E631, Q192
narrowed, not retired). The simulator is unchanged. The roadmap counts the questions from the
built `doc/open_questions.md`: 167 open (Q001 to Q211), 149 hw (high 17, medium 69, low 63), 12 fw
and 6 kernel; usse 38, edm 17, isp 15, dpm 9.

Sub-phase 11.39 is a records sub-phase with three laptop batches (the coverage envelope sweep, 1822
jobs; a vertex side, DPM, EDM and USSE verification batch, 157 jobs; a texture, ISP and
multisampling batch, 140 jobs) and no kernel change. The ISP's coverage rule holds on ten more
targets up to 4096 x 4096 and its half-up rounding at the tie on seven, the edge function is exact
for edges up to 2052 pixels and a far vertex to 2^21 pixels is drawn exact within 6e-4 pixel of an
edge line, while negative vertices with a sub-grid fraction are not rounded half up (E680 to E684,
Q260 to Q262). A counter predicts which VDM_STATE1 job hangs, for one job shape (E700, E701), a
vertex task's capacity and forced rows were probed (E702, E703), a 1500-vertex scene's threshold
does not move with the page count (E704), the page need of one triangle depends on its position
(E705), the kernel's hang recovery ends a long partial-render sequence (E706), and an end-of-tile
store is not reproduced (E707 to E709, Q163 to Q278). The sampler's bilinear result is the two-stage
form of E720, and the simulator `sgx-sim` takes it, tests first, with 8 new vectors; the gradient
footprint, the T3 address chain, sRGB, ETC1, the texture types and the cube are findings the
simulator keeps refused (E721 to E726, Q280 to Q284), and the multisample, TE bit, the 4x health
triangles (Q003), ZLS band and depth plane results are E727 to E731 (four questions opened then, up
to Q288; E829 answered the first), E732 the accounting. Four questions are
folded into Q163, the one on two EDM tasks (answered by E752) and the one on the end of a pass
(answered later by E836, the two folds now in Q294), the state-page question (answered by E1080) is
split (Q277 for the
firmware) and the kernel part of the wide-scene question (since folded into Q211) is
Q278; no question is answered. The roadmap counts the questions from the built
`doc/open_questions.md`: 184 open (Q001 to Q288), 165 hw (high 20, medium 76, low 69), 12 fw and 7
kernel; isp 20, usse 39, texture 19, pds 17, edm 15, ta 15, dpm 12, vdm 11.

Sub-phase 12.0 is the first of the pipeline simulator (section 3), a records and tooling sub-phase
with no laptop run and no kernel change: the crate `crates/sgx-pipe` beside `sgx-sim`, with a module
for each fixed-function unit that refuses, naming its open questions, the formats of unit vectors
and scene vectors (`doc/specs/vectors.md` sections 5 and 6, in directories of the data repository
outside `vectors/`) and the first four unit vectors, from rules that records state as fits: the ZLS
store address (E465, E615: 3415552 dwords, 3225000 at the rule's address and counted fitted, the
dwords past the target refused then, matched since by E831's band, and those in the overflowed
jobs' tiles refused as Q107), the TA's region test (E542, E616: 14656 pairs, 2414 of them by
presence only), the object layout (E541, E617: 56 layouts, the three failed jobs refused as Q165,
not predicted) and the multisample window rule
(E503, E618: 786 tiles, 13 refused, the seam holes E953 answers). Every verdict is fitted, none
matched. The inventory of
the recorded data (E619, `doc/specs/pipe-inventory.md`): 2464 triangle-host vectors, 65 with a
render dump, and 197 dump directories sorted by what each waits for. The simulator `sgx-sim` is
unchanged. A question on the arithmetic of coverage, depth and iteration for an arbitrary triangle
is new (since folded into Q200).
The roadmap counts the questions from the built `doc/open_questions.md`: 185 open (Q001 to Q288),
166 hw (high 21, medium 76, low 69), 12 fw and 7 kernel; isp 21.

Sub-phase 12.1 is the first whole job of the pipeline simulator, the transfer (a fill or a copy), a
tooling sub-phase with no laptop run and no kernel change: `sgxfive-test fill` and `copy` write the
words they build (`--emit-scene`), and `sgx-pipe` runs the pixel-event program of each tile, the
end-of-tile task and the PBE through `sgx-sim` from them. 13679 scenes of the transfer sweeps,
rebuilt and not captured, give 5079 matches and 8600 refusals by question (63 percent refused), none
mismatching and none fitted; the matches are a development set whose first version's 143 mismatches
became refusals (E620), and they show the hardware agreeing with the model on 45 unpoked jobs and on
poked words, 2433 of which the model reads. 74 unit vectors of the PBE's pack modes give 14 matches
and 60 refusals. Q206 (transfer words with no record) and Q207 (PDS programs and inputs no record
measured) are new. The simulator `sgx-sim` is unchanged. The roadmap counts the questions from the
built `doc/open_questions.md`: 187 open (Q001 to Q288), 168 hw (high 21, medium 78, low 69), 12 fw
and 7 kernel; pds 18, transfer 4.

Sub-phase 12.2 is a render job's vertex side and the TA's output, a tooling sub-phase with no laptop
run and no kernel change: `sgxfive-test probe --tri --emit-scene` writes the words of a triangle
job, and `sgx-pipe` runs the VDM stream, the vertex tasks on `sgx-sim`, the MTE and the TA over
them. Of 355 jobs built from 599 dumped (244 replace a vertex or PDS program, a limit of the
builder), 89 reproduce the saved parameter buffer and TA data byte for byte and are fitted, none
matched, because the TA's rules are fitted; 266 (75 percent) are refused by question and none
mismatches (E650 to E652: the object's vertex block, the region headers and the order of the
streams). All 89 are the library's pass-through vertex program. Q230 (a triangle the clip cuts or
the packed block cannot hold) and Q231 (the VDM and command words no record reads) are new. The
simulator `sgx-sim` is unchanged. The roadmap counts the questions from the built
`doc/open_questions.md`: 189 open (Q001 to Q288), 170 hw (high 21, medium 79, low 70), 12 fw and 7
kernel; ta 17.

Sub-phase 12.3 is the ISP and the first triangle's image, a tooling sub-phase with no laptop run and
no kernel change: `sgx-pipe` takes E606's coverage rule and E607's vertex rounding into the ISP,
runs the pixel programs, the end-of-tile task and the PBE after it, and reproduces 2752 of 2752
recorded images of the E606 and E607 jobs pixel for pixel, 1566 on which the rule was found and 1186
held out, the stored depth within 3 units of 2^-23 where the gradient is below 0.03 and refused
above it (Q200), and the clip z within 4 units (E660, E661). It reproduces the first triangle's
image hash at the three sizes E606 ran and refuses the rest (E662 shows the rule gives it at all 16
sizes; the model's envelope is three, Q240). Of the 2464 triangle-host vectors, 2281 rebuilt, 47
reproduce, 1 predicts a hang and 2233 (97.9 percent) are refused, none mismatching; the census is a
development set (71 first-run mismatches were removed by rules and refusals), and every image rests
on the fitted coverage rule, so none is matched. Q240 (random triangles on other targets) and Q241
(ISP words and depth compares no probe separated) are new. The simulator `sgx-sim` is unchanged. The
roadmap counts the questions from the built `doc/open_questions.md`: 191 open (Q001 to Q288), 172 hw
(high 21, medium 80, low 71), 12 fw and 7 kernel; isp 23.

Sub-phase 12.4 is the ZLS's store and load of the depth, a tooling sub-phase with no laptop run and
no kernel change: `sgx-pipe` decodes CR_ISP_ZLSCTL as the records read it, stores the depth in the
float, 24-bit and 16-bit formats at E465's address rule where the integer formats were measured (the
ramp's 0.25 to 0.4166 and the clear value 1.0), counts the dwords a store writes, clears the sign of
a loaded depth and runs a flat triangle over a loaded depth under the depth test never or less (E663
to E665). 88 unit vectors (`zls-format` 11, `zls-load` 30 and `zls-ctl` 47) replay with no mismatch:
15 matched, 59 fitted, 12 refused by question and 2 empty (formats 4 and 7 store nothing without a
stencil buffer); every result by a fitted rule is fitted. What no run measured stays refused:
formats 3, 5 and 6 (Q120), other 16-bit pitches and depths off the ramp (answered since by E977 and
E1041), a load of an integer
format at another address and a loaded NaN under a compare (answered since by E995 and E1040) and
the control bits no run
separated, with bit 0 modelled for one control (Q071); several objects over a loaded depth are not
modelled (no data). E466 and E467 are carried forward with dated corrections (the ramp runs 0.25 to
0.4166, not to 0.75; the label of the control 0x0011d10a). The questions E1041 and E1040 answered
and a
third are new (the
third, on the control bits and bit 0, folded into Q071 on 2026-11-12). The simulator
`sgx-sim` is unchanged. The roadmap counts the questions from the built `doc/open_questions.md`: 194
open (Q001 to Q288), 175 hw (high 21, medium 80, low 74), 12 fw and 7 kernel; zls 10.
