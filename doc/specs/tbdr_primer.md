# PowerVR SGX545 architecture primer

This is the conceptual machine behind the GPU in the Intel Cedarview (Atom N2600/N2800/D2500/D2700,
sold as GMA 3600/3650), drawn from expired Imagination and VideoLogic patents and public
architecture material. It stops at the architecture: what the hardware does and why. The
register map, the command layout and the USSE instruction set are not here, because patents do
not disclose them; they are in `doc/specs/hw_spec.md` and the specs that follow it. Read this
first, and the DDK reads as an implementation of ideas you already know.

Claims taken from a patent are marked `[patent]`; claims extrapolated from general PowerVR
knowledge are marked `[infer]`.

## 1. The hardware

Cedarview's GPU is not an Intel design. It is a PowerVR SGX545 core licensed from Imagination
Technologies. Consequences:

- Intel never owned the 3D design, so no open 3D driver came from Intel.
- Imagination did not publish SGX programming documentation (instruction set, registers).
- Mesa has no SGX driver to extend.

The SGX545 belongs to Series 5XT, whose shader cores run the USSE instruction set (Imagination's
PowerVR Series5 Architecture Guide for Developers). The open PowerVR driver in mainline Linux
(the `imagination` DRM driver, merged in Linux 6.8) and Mesa's `pvr` Vulkan driver target Series
6 and later, the Rogue cores, with a different instruction set (USC) and command stream. Rogue
shows PowerVR's approach and a modern driver's structure, but it does not decode the SGX545's
instructions or commands.

*Based on imgtec-series5-arch-guide-2019; linux-imagination.*

## 2. Kinds of source

| source | what it gives |
|---|---|
| expired patents (§6) | architecture, algorithms, data flow: the mental model |
| GPL DDK for Cedarview (sgx545-ce, 1.7.862890) | registers, kernel services, firmware ABI |
| public architecture guides | unit names, the pipeline, performance behaviour |
| our own hardware | runs and captures: what the core actually does |

sgx545-ce is the DDK for the same core: an SGX545, though the board it was ported to reports core
revision 1.0.14 (sgx545-ce `Kbuild`) and ours 1.0.13 (`doc/specs/hw_spec.md` §8; Evidence:
E007). The patents explain, the DDK implements, the hardware decides; each
covers what the others leave out.

*Based on sgx545-ce `Kbuild`; E007.*

## 3. The tile-based deferred renderer

PowerVR is a tile-based deferred renderer (TBDR). Two words, two ideas.

### 3.1 Tile-based: divide the screen, not the work

The screen is split into rectangular tiles, and for each tile only the geometry that falls in it
is processed `[patent]`. The foundational patent's example: splitting a 20 x 20 region into four
10 x 10 tiles cut processing from 16,000 to 4,000 cycles, a 75% drop `[patent, EP0725367]`.
Geometry is not copied per tile; each tile holds a list of object pointers into shared surface
data, with position and size data at the head of each tile list `[patent]`. In SGX terms this
per-tile store is the parameter buffer: the intermediate store of transformed geometry and tile
lists between the geometry phase and the pixel phase `[infer]`.

### 3.2 Deferred: know visibility before shading

A conventional GPU shades a pixel and may overwrite it when a closer surface arrives (overdraw,
wasted bandwidth). PowerVR defers all texturing and shading until visibility is resolved for
every pixel of the tile. The original scheme casts a ray from the viewpoint through each pixel's
elementary area and finds the nearest intersecting surface `[patent]`: a ray-cast, "inverse-Z"
hidden-surface removal instead of a read-modify-write depth buffer. Surfaces are described by
plane coefficients (the patent gives 96-bit surface parameters with coefficients A, B, C)
`[patent]`. In SGX this removal happens on chip, per tile, so only the winning fragments reach
texturing and shading `[infer]`.

### 3.3 The pipeline stages

```
         GEOMETRY PHASE                       PIXEL PHASE (per tile)
vertices -> [TA]                     [ISP] -> [TSP] -> [USSE] -> tile buffer -> framebuffer
            transform, bin into tiles,
            write the parameter buffer
```

- **TA (tile accelerator):** transforms geometry and bins primitives into per-tile lists in the
  parameter buffer: the tile-based write phase.
- **ISP (image synthesis processor):** the deferred hidden-surface engine. It resolves which
  surface wins at each sample of the tile before any shading. Historically a master/slave chain
  of ISP cells sharing a 96-bit instruction word, each working on a different line of the same
  tile `[patent]`.
- **TSP (texture and shading processor):** texture addressing and fetch, and parameter iteration,
  for the surviving fragments.
- **USSE (Universal Scalable Shader Engine):** the unified programmable array that runs vertex
  and fragment shaders.
- **Tile buffer to framebuffer:** a tile is resolved on chip and then written out, so no large
  external depth buffer is read and written `[patent]`.

The unit names are the DDK's: `SOFT_RESET` and `CLKGATECTL` have one field per unit (`TA`, `ISP`,
`TSP`, `USE`, `DPM`, `PBE` among them; `doc/specs/hw_spec.md` §5), and Imagination's
architecture guide describes the same stages. The DPM, the parameter memory manager, allocates
the parameter buffer's memory; the PBE, the pixel back end, writes the tiles out.

### 3.4 Why it stays fed `[patent]`

Tiles vary widely in complexity. To keep the pixel pipeline from stalling on a heavy tile, rows
from tiles of different complexity are interleaved, so the post-processing units see a steady
data rate without an expensive full framebuffer. Worth remembering when reasoning about
scheduling and timing.

*Based on patent-EP0725367; sgx545-ce `src/services4/srvkm/hwdefs/sgx545defs.h`;
imgtec-series5-arch-guide-2019.*

## 4. How the architecture maps onto the Linux stack

| part | Linux component |
|---|---|
| display controller and scanout (Intel's own, not PowerVR) | the `gma500` DRM/KMS driver |
| command submission, memory contexts, synchronisation | the SGX driver inside gma500 |
| TA, ISP, TSP and USSE programming, shaders | user space; Mesa has no SGX driver |

The split is clean: the display is Intel silicon, and gma500 drives it independently of the
GPU, while everything that renders is PowerVR. The SGX driver is modelled on the DDK's kernel
services.

*Based on linux-gma500; sgx545-ce.*

## 5. What patents do not give

Patents describe methods, not the programming interface. Missing, and where it comes from:

- **Register map and offsets:** the GPL DDK.
- **Command-stream layout:** the DDK, and captures of the command stream on our hardware.
- **USSE instruction set:** our disassembly of the firmware, for interoperability, and programs
  run on our hardware.

Understanding is built from expired patents, public documents and GPL source; behaviour is
captured from our own hardware.

*Based on the sources of §2.*

## 6. Patent shelf

**Expired or lapsed:**

- `EP0725367B1` / `GB2298111A`: *Computer 3D rendering method and apparatus* (priority
  1995-01-31). The foundational TBDR text and the main source for §3.
- `WO2001095257A1`: *Tiling and compression for rendering 3D images* (priority 2000).
- `EP1351195A2` / `GB2378108A`: *3-D computer graphics rendering system* (priority 2002-03-26).
- `US7834872B2`: *Tiling system for 3D rendered graphics* (priority 2003-03-27, expired
  2024-03-26): tile-binning arithmetic, conservative reduced-precision edge tests, culling of
  small primitives against sample points.
- `GB2404316A`: *Visibility determination in 3D graphics rendering* (priority 2003-07-25).

**In force, public to read, to be practised with care (SGX era):**

- `US7978199B2`: *Parameter compaction in tile based rendering device* (priority 2006). About
  parameter buffer management.
- `US8368691B2`: *Untransformed display lists in a tile based rendering system* (priority
  2008-03-19).
- `US8502829B2`: *Multi-core geometry processing in a tile based rendering system* (priority
  2007-11-30).
- `US9633405B2`: *Tile based computer graphics* (priority 2012-09-12).

*Based on patent-EP0725367, patent-WO2001095257, patent-EP1351195,
patent-US7834872, patent-GB2404316, patent-US7978199, patent-US8368691, patent-US8502829,
patent-US9633405.*
