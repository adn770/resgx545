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
triangle and fault recovery on the laptop); questions Q005 and, on the control block's mapping in
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

`doc/open_questions.md` lists every open question, generated from `questions/`: Q001 to Q151, 127
open (the three ids between Q146 and Q150 are reserved, unused). Each has a kind. The work is
hardware knowledge, for a simulator and then our own firmware, so the 113 `hw` questions are the
work queue, each with a value (high 13, medium 59, low 41); the 10 `fw` questions (the closed
firmware's and driver's own behaviour: Q004, Q029, Q034, Q049, Q084, Q088, Q118, Q119, Q124, Q131)
and the 4 `kernel` ones (the design of our kernel driver: Q005, Q037, Q095, Q140) stay open, parked.
By unit: bif 4, dpm 5, edm 6, isp 10, mte 3, pbe 5, pds 16, platform 4, render 9, ta 9, texture 7,
transfer 3, usse 32, vdm 8, zls 6. A question is removed when a record answers it; one that mixed a
hardware part with a firmware or kernel part was narrowed to the hardware part or folded into the
hardware question that holds it (six so far: the control block's per-VM copy and the render context
count bound into Q076, the recovery's reset steps into Q003, the settle routine and the two faults
after a base-only fault or a kept owner into Q036 and Q045), and a fold is not an answer. What a
fold or a narrowing left of the closed firmware's own behaviour is a new parked question: how a kick
tells its directory is in no list (Q118, from the render context count) and whether a command with
both kick flags acts as two (Q119, from Q065).

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
  render is exact, while after bit 3 a later render faults (E458, E462, Q036, Q045).
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
- **VDM words.** The state word's open fields (Q037, Q047, Q102; E413 has the alternation of bits
  11:9 = 7) and the index list's first trailing word (Q042).
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
- **pds:** the pixel PDS pointer and size words (E343; E436); code-address words and bases of the
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
no-wait iteration never reaches `pa0` (E393) and E133's stale pixels do not recur (E392). Q021,
Q023, Q057 and Q008 had no run (the questions on a DOUTU's width, on the copy's buffers and on T0's
maximum level 15 were answered in 11.16: E428, E425, E441).

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
event sets which status bit (Q111), the index list's width bits (Q112), cube and volume textures
and anisotropy (Q113 to Q115), the region clip as a scissor (Q116) and points (Q117).

Sub-phase 11.22 ran three tables on the laptop with no kernel change, about the depth and stencil
load and store (ZLS): `zls/store-layout.toml`, `store-format.toml` and `load-copy.toml`. The tool's
`tri` gained a full-target triangle with a depth at each vertex (`--tri-full`, `--tri-z`), so that a
ramp makes every stored dword name its pixel, fills that encode the dword's index
(`--depth-fill index`, `bit:K`), and separate store and stencil buffers (`--depth-store`,
`--stencil`, `--stencil-store`). The store window of E461 is the arithmetic of the tile pitch,
control bits 11:3 (E465); bits 26:24 are the stored format (E466); bits 1, 13 and 14 load, the
stencil and the depth (E467); and what an overflowed job stores is the first row of macrotiles as
zeros and the rest negated (E468). Q088 stays open as a firmware question (its hardware half is
answered); Q071, Q101 and Q107 are narrowed; Q120 to Q122 are new.

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
runner's digest function). Records E469-E477; Q052 is narrowed, none retired; Q123 to Q127 are new,
Q124 for the firmware (`fw`).

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
not answered: two EDM tasks at once (Q131) and `str` then `ldr` (Q134). E489 and E490 recompute
E465 and E466 from the raw dumps, and E465 and E466 are carried forward with a dated note.
Records E478-E490; Q051, Q052, Q054, Q098, Q101, Q107, Q120, Q124 and Q125 are narrowed, none
retired; Q128 to Q134 are new, Q131 for the firmware (`fw`).

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
nothing seen except that bit 46 changed `r14` (3 of 3 jobs, open: Q135). `cie` adds bit 0 of `iN`
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
Q098, Q123, Q125, Q126 and Q127 are narrowed, none retired; Q135 to Q137 are new.

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
exactly at 96 x 48 and 128 x 64 and fault at 128 x 128 and larger (E511). Records E502-E511; Q030,
Q086, Q089 and Q100 are narrowed, none retired; Q138 to Q142 are new, Q140 for the kernel.

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
Q133, Q134, Q135 and Q137 are narrowed, none retired; Q143 to Q146, Q150 and Q151 are new (all hw,
Q143 medium, the others low).
