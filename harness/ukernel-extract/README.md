# Ukernel extraction harness (mock-and-intercept)

A mock-and-intercept harness: runs the closed srvinit on an x86 Linux host under a fake libdrm
and captures what it writes to device memory, so the firmware format can be verified. It needs
no GPU and no kernel module, and nothing it runs can harm the host: the SGX545 USSE
**microkernel** is pulled out of the closed Cedarview usermode library
(`libsrv_um.so.1.7.862890`) as the driver copies it into "device" memory.

Why this works (the hardware spec, `doc/specs/hw_spec.md`, arrives with the firmware boot unit and
discusses it): the ukernel is static data in the usermode lib; init *allocates a GPU-mapped
buffer, `memcpy`s the ukernel in, writes a few registers, kicks once, and polls one memory flag*.
No per-chunk HW handshake. So a fake `libdrm` and an interposed `PVRSRVMemCopy` make the driver
reveal the ukernel into a buffer we own.

## Pieces

- `fakedrm.c` → `fakedrm.so` (LD_PRELOAD): the entire kernel interface is `libdrm`
  (`drmOpen` + `drmCommandNone`/`drmCommandWrite`). The shim fakes a device fd, logs the PVR
  **bridge-command sequence**, zeroes each bridge call's OUT buffer so it reads `PVRSRV_OK`, and
  **interposes `PVRSRVMemCopy`** to log/flag large copies (the ukernel upload).
- `loader.c` → `loader`: `dlopen`s `libsrv_um` + `libsrv_init`, calls `PVRSRVConnect` (and will
  drive the SGX device init once connect succeeds).

## Build & run (any x86-64 Linux with 32-bit multilib)

Both programs use one staging directory, `$SGX_UK_DIR` (default `~/resgx545-uk`, see
`ukdir.h`): the closed libraries go in its `lib/`, and the shim writes `drm.log` and `dump/`
there. The libraries come from the user's own copy of the closed Cedarview userspace package
(`$RESGX545_CDV_LIBS`, its `usr/lib/`; `tools/fwcutter/get-firmware.sh` fetches it); this
repository contains none of them.

```sh
export SGX_UK_DIR=~/resgx545-uk
mkdir -p $SGX_UK_DIR/lib
for l in libsrv_um libsrv_init; do
    cp $RESGX545_CDV_LIBS/$l.so.1.7.862890 $SGX_UK_DIR/lib/
    ln -sf $l.so.1.7.862890 $SGX_UK_DIR/lib/$l.so     # the unversioned sonames
done
gcc -m32 -shared -fPIC fakedrm.c -o fakedrm.so -ldl
gcc -m32 loader.c -o loader -ldl
LD_LIBRARY_PATH=$SGX_UK_DIR/lib LD_PRELOAD=./fakedrm.so ./loader
cat $SGX_UK_DIR/drm.log
```

## Result: the extracted microkernel

`SrvInit` runs to completion (returns 0) and uploads the microkernel; the harness captures it.
The output is the **53096-byte (0xCF68) SGX545 USSE microkernel** and its 5 auxiliary programs
(the PDS programs). The ukernel is a static blob in **`libsrv_init.so` at file offset
`0x2080`**, patched at init in 9 instructions (E002). The captures are kept in
resgx545-data-private (manifest `datasets/firmware-layout.toml`). The cut microkernel image
used by the other tools comes from `$RESGX545_UKERNEL`.

### How the init path works

- **Command numbering:** the bridge ID's low byte is the absolute command index. The closed
  library is built with PDUMP and OVERLAY disabled, so `SGX_CMD_BASE=83` and
  `INITSRV_CONNECT=67`; the commands that crash a naive stub decode to `INITSRV_CONNECT(67)`,
  `SGX_GETMISCINFO(97)` and `SGXINFO_FOR_SRVINIT(98)`.
- **Fault pinpointing:** `loader.c` installs a `SIGSEGV` handler that prints the faulting PC,
  the accessed address and the library bases.
- **Heaps:** `SGXINFO_FOR_SRVINIT` answers with `asHeapInfo[32]` (24-byte entries); srvinit
  needs 7 real heaps there, IDs 0..6 in the low 24 bits of `ui32HeapID`, with the IDs and bases
  of `sgxapi_km.h` / `sgxconfig.h` (**ID 2 = KERNEL_CODE**, where the ukernel goes). The
  layout captures show srvinit placing its buffers in the heaps it is given (`layout_moved`
  moves every base).
- **The mmap dance:** per buffer, srvinit does `ALLOC_DEVICEMEM(6)`, then
  `MHANDLE_TO_MMAP_DATA(11)`, then **`syscall(SYS_mmap2)`** (libsrv_um imports `syscall` and
  `munmap`, **not** `mmap`). The shim fills the 76-byte ALLOC OUT (`hMappingInfo` is at
  `o[11]`; `sCpuPAddr` is 64-bit), answers
  MHANDLE with a cookie, and **interposes `syscall`** to serve a real anonymous buffer per
  allocation.
- **Capture:** `PVRSRVMemCopy` into the KERNEL_CODE buffer fires; allocation #9 (heap
  `beef0002`, 0xCF68) is the ukernel. Buffers are dumped at `munmap` and at exit. The static
  carve from `libsrv_init.so+0x2080` matches the runtime image except the 52 patched bytes (E002).

The ukernel is disassembled with `tools/usse-dis/` (arrives with the disassembly unit) and its
EDM structure is decoded in the hardware spec (arrives with the firmware boot unit).

## Init-info capture & decode

`fakedrm.c` also dumps the IN buffer of `SGX_DEVINITPART2` (bridge nr 99), the complete
`SGX_BRIDGE_INIT_INFO` srvinit builds, to `$SGX_UK_DIR/dump/devinitpart2_in.bin`. The capture
tables keep it per layout, with the control-block buffers `alloc00..08_*.bin`.

```sh
../../.venv/bin/pytest -q test_initinfo.py              # layout + capture checks
../../.venv/bin/python initinfo.py layout_base/devinitpart2_in.bin
```

`initinfo.py` decodes the control-block handles, the per-command EDM handler addresses, the
three register init scripts (with register names), EDM task / clock-gating registers, MKIF
struct sizes and init memory. `sgx545_labels.r2` holds the hand-written ukernel labels and
comments. `make_r2.sh` joins them with the handler labels from `initinfo.py` and a
register-access comment per firmware MMIO access into `sgx545_ukernel.r2`, the combined
radare2 annotation script. That script annotates closed code, so it is not in this
repository: make it from your own firmware with

```sh
RESGX545_UKERNEL=.../00_ukernel.bin ./make_r2.sh      # needs usse-dis (disassembly unit)
```

The init info defaults to the `layout_base` capture in resgx545-data-private. That repository
also keeps a copy made from the Cedarview build, `firmware/r2/sgx545_ukernel.r2`, SHA-256
`ca9d1d48a6e2271d0fc690cee15a564b381d946c53ea4c4f15c3d4a50becb286`; your output should equal
it.

`edmtrace.py` (tested: `test_edmtrace.py`) traces what a range of EDM code reads and writes.
Given seeds for the registers that point at known structures when the range starts (a
`kick3d.py` layout, `cmd_ta`, or the glossary's prefix, `CMDTA`), it follows values linearly
through moves, adds and loads. A word `kick3d.py` names as a structure's address types what is
loaded through it, so one seed reaches the structures it points at: `sa0`, the TA/3D control
block, reaches the command, render details, RT data, context and PB descriptors the kicks
record there. It names every SGX register and structure word with its glossary term, or with
its offset (`0x0abc`, `CMDTA+0x0f8`) when the glossary has none:

```sh
../../tools/usse-dis/usse-dis "$RESGX545_UKERNEL" > uk.txt
../../.venv/bin/python edmtrace.py uk.txt 95a 985 --seed r1=cmd_ta
# 0x095e  W CR_TE_AA <- cmd_ta.te_aa ...
../../.venv/bin/python edmtrace.py uk.txt 7b1 7fb --seed r0=cmd_ta
# 0x07b5  st hw_render_details.frag_flags <- cmd_ta.frag_flags ...
```

The exhaustive dataflow analysis of the ukernel is `edm_dataflow.py`, which writes
`doc/specs/edm_dataflow.md`.

## Layout captures (for the fwcutter loader)

`fakedrm.c` takes two more knobs: `MOCK_HEAP_START` (where the first buffer of each heap goes;
default `0x1000`) and `MOCK_PDPADDR` (the page directory's physical address), and
`MOCK_HEAP_BASE_<id>` (heap base override, `sgxapi_km.h` heap ids). Two captures are taken:
`layout_base` (defaults) and `layout_moved`. The capture table `captures/firmware/layout.toml`
runs `templates/layout.sh` on a build host (the campaign runner arrives with the probes unit)
and the dataset manifest `datasets/firmware-layout.toml` pins the result in
resgx545-data-private. The moved layout by hand:

```sh
MOCK_HEAP_START=0x5000 MOCK_PDPADDR=0x2345000 MOCK_HEAP_BASE_2=0xE8100000 \
MOCK_HEAP_BASE_3=0xF0100000 MOCK_HEAP_BASE_4=0xF4100000 MOCK_HEAP_BASE_5=0xFC100000 \
MOCK_HEAP_BASE_6=0xE4100000 LD_LIBRARY_PATH=$SGX_UK_DIR/lib LD_PRELOAD=./fakedrm.so ./loader
```

`tools/fwcutter/test_fwload.py` replays both layouts through the reference loader and checks
the result against these dumps, byte for byte.

## Transfer captures (for the transfer templates)

The same shim runs the closed OpenVG stack, whose fills and copies go through the transfer
queue: `fakedrm.c` dumps each `SGX_SUBMITTRANSFER`'s IN buffer and a snapshot of every live
device object (`dump3d/xferNN_in.bin`, `dump3d/xferNN/`). Two more pieces:

- `fakewsegl.c` → `libpvrFAKEWSEGL.so`: our own window-system module, a WSEGL (interface
  version 2: a version word and the entry points the closed modules export) with one
  configuration and no native drawables. libIMGegl loads the module named by the
  `WindowSystem` app hint; `fakedrm.c` redirects `/etc/powervr.ini` to `$SGX_UK_DIR/powervr.ini`.
  A pbuffer needs nothing else from the window system.
- `xfer.c` → `xfer`: loads libEGL and libOpenVG with `dlopen` and runs its arguments as steps
  through the Khronos API only: create an image (which fills it), `vgClearImage` (a fill),
  `vgCopyImage` (a copy). Each step is marked in the bridge log.

`xfer` reads the init info srvinit leaves (`devinit.bin`), so the loader runs first. The
capture table `captures/firmware/transfer.toml` runs `templates/transfer.sh` on a build host
with the whole closed `usr/lib/` in `$RESGX545_CDV_LIBS` (default `~/resgx545-uk/lib`): one
run per line of `templates/transfer_runs.txt`, each with its own `MOCK_*` variables, kept
trimmed by `tools/fwcutter/tqcapture.py trim` to what each transfer's programs touch. The
dataset manifest `datasets/firmware-transfer.toml` pins the result in resgx545-data-private,
and `tools/fwcutter/test_tqcapture.py` reads it (E004). One run by hand:

```sh
gcc -m32 -shared -fPIC fakewsegl.c -o $SGX_UK_DIR/lib/libpvrFAKEWSEGL.so
gcc -m32 xfer.c -o xfer -ldl
cp $SGX_UK_DIR/dump/devinitpart2_in.bin $SGX_UK_DIR/devinit.bin     # after ./loader
printf '[default]\nWindowSystem=libpvrFAKEWSEGL.so\n' > $SGX_UK_DIR/powervr.ini
LD_LIBRARY_PATH=$SGX_UK_DIR/lib LD_PRELOAD=./fakedrm.so \
    ./xfer img=a:8888:64x64 img=b:8888:64x64 fill=a:0xff336699:3,5,40,30 copy=b:0,0:a:0,0,64,64
ls $SGX_UK_DIR/dump3d      # xfer00_in.bin xfer00/ ...
```

## 3D capture

The same shim drives the closed GLES stacks: each TA and 3D kick a program submits is dumped
with a snapshot of every live device object, so the state the closed driver writes for one
piece of GL state can be read word by word. Two programs make the kicks:

- `tri.c` → `tri`: draws one constant-colour triangle with EGL and GLES2 into a 64x64 pbuffer
  and calls `glFinish`. Its `key=value` options (`triopts.h`) change one piece of state each:
  size, pixel format, colours, depth, stencil, blending, culling, colour mask, scissor,
  viewport, primitive type, vertex positions, a varying colour, textures and render to texture,
  uniform values and attribute layouts, and shaders loaded from files (`vsfile=`, `fsfile=`).
- `tri1.c` → `tri1`: the same for GLES1, through the closed fixed-function library, so a
  capture holds the USSE and PDS programs the driver generates for the fixed-function state
  its options (`tri1opts.h`) set.

Both load the closed libraries with `dlopen` from `$SGX_UK_DIR/lib` and declare the few
Khronos constants and prototypes they use, so they build without closed headers. They need the
window-system module and the init info of the transfer captures above.

```sh
gcc -m32 -shared -fPIC fakedrm.c -o fakedrm.so -ldl
gcc -m32 -shared -fPIC fakewsegl.c -o $SGX_UK_DIR/lib/libpvrFAKEWSEGL.so
gcc -m32 tri.c -o tri -ldl
gcc -m32 tri1.c -o tri1 -ldl
cp $SGX_UK_DIR/dump/devinitpart2_in.bin $SGX_UK_DIR/devinit.bin     # after ./loader
printf '[default]\nWindowSystem=libpvrFAKEWSEGL.so\n' > $SGX_UK_DIR/powervr.ini
LD_LIBRARY_PATH=$SGX_UK_DIR/lib LD_PRELOAD=./fakedrm.so ./tri
ls $SGX_UK_DIR/dump3d      # kickNN_in.bin, kickNN/ (objects.txt, objNNN_<dva>.bin)
```

### Differential captures

A list file holds one run per line, `name option...`, each changing one piece of state against
a base run of the same list. `capture3d.sh` runs a list, each run in its own directory
`$SGX_UK_DIR/var/<name>/` that links `lib/` (or `$SGX_UK_LIB`), `devinit.bin` and
`powervr.ini`; a word `ini:Key=Value` is appended to that run's copy of `powervr.ini` (a closed
driver app hint), and `prog:tri1` runs `tri1` instead of `tri`. Run names repeat across lists
(`base` is in most of them), so give each list its own `SGX_UK_DIR`, or move `var/` away before
the next list.

The lists:

- `variations3d.txt`: one piece of GL state each;
- `sizes3d.txt`: the render-target size, 1x1 to 4096x4096;
- `textures3d.txt`, `samplers3d.txt`, `formats3d.txt`: textures, render to texture, filters
  and wraps, texture formats;
- `shaders3d.txt`: one shader per feature, written with `shaders/` by `gen_shaders3d.py`;
- `inputs3d.txt`: uniform values and vertex attribute layouts;
- `gles1_3d.txt`: GLES1 fixed-function state, with `prog:tri1`;
- `isp3d.txt`, `gaps3d.txt`, `lines3d.txt`, `streams3d.txt`: render-details registers the
  other lists leave alone, line widths, YUV texture streams;
- `track3d.txt`: several draws, flushes and frames, depth and stencil buffers kept in memory,
  small parameter buffers.

```sh
SGX_UK_DIR=~/resgx545-uk3d ./capture3d.sh variations3d.txt          # or: ... list name...
../../.venv/bin/python state3d.py ~/resgx545-uk3d/var/base          # every state word
../../.venv/bin/python diff3d.py --all ~/resgx545-uk3d/var          # each run against base
../../.venv/bin/python tiling3d.py ~/resgx545-uk3d/var              # the size rule, per run
```

`kickwalk.py` decodes a kick's VDM control stream and follows its pointers to give every
object a role, with the structure layouts of `kick3d.py`; `summary3d.py` lists one kick's
objects with their roles and cross references and disassembles the PDS and USSE programs they
reach (with `tools/usse-dis`); `state3d.py` names every state-carrying word of both kicks under
a stable path; `diff3d.py` compares two captures word by word, hiding the words that differ
only because the object they point into moved; `tiling3d.py` holds the render-target layout
rule the size captures show and checks it against every capture. The captures themselves are
closed-driver output and are kept in resgx545-data-private, not in this repository.
