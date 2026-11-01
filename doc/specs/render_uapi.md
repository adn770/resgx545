<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# SGX545 render node: the kernel and userspace interface

The linux fork's gma500 driver exposes the SGX545 of Cedarview to unprivileged processes through
a DRM render node, "sgxfive". This document specifies that interface as it landed: what each
ioctl does, its arguments and rules, the GPU address space a client sees, how jobs are submitted
and how faults are recovered, the limits, and the security model with the measurements it rests
on. Abbreviations of the hardware units (BIF, TA, DPM, OTPM, ZLS, PDS, USSE, ISP, TSP, PBE, EDM)
are terms of doc/glossary.md; a BO is a buffer object and a VM an address space, that is one page
directory. Register and field names in code font are the header's or libsgxfive's own names, or
registers of the glossary. The contract itself is `include/uapi/sgxfive_drm.h`; the header's
comments are normative for every field and this document does not repeat them. The host side is
`libsgxfive` (`userspace/libsgxfive`), which the tools use to submit fills, copies and renders.

Sources: the header, the fork's `drivers/gpu/drm/gma500/sgxfive*` and `gma_sgx.c` (branch
`resgx545`), and runs on the laptop through them (HW). What a submitted command means to the
firmware is in transfer.md (the transfer command and the kernel command queue) and fw_format.md
(the programs a transfer runs); the render job's register words are the 3D unit's and are
not yet specified; section 8.4 lists only what the kernel checks. Each section ends with its
evidence where records exist.

## 1. The node and its gate

The render node is off by default. The module parameter `gma500_gfx.sgx_render` (bool, mode
0444, so fixed at load) turns it on:

- off: the driver drops `DRIVER_RENDER` before it registers, so there is no `/dev/dri/renderD*`;
  the primary node (card0) answers `DEV_QUERY` and returns `-EPERM` for every other sgxfive
  ioctl before it looks at an argument. `DEV_QUERY` reports fixed device facts and nothing else;
- on: every ioctl is accepted on the render node and on the primary node alike.

The reason is the security model of section 11: a client's GPU programs can read device state, so
the node is for trusted users. All ten ioctls are `DRM_RENDER_ALLOW`. A device without the SGX
driver answers `-ENODEV`.

The interface is a draft, not stable until it is merged upstream together with its open-source
userspace (the header says so).

## 2. Conventions of the argument structs

These hold for every struct, as in the PowerVR Rogue UAPI:

- members are naturally aligned and each struct is padded to a multiple of 8 bytes, so i686 and
  x86-64 share one layout. Padding is explicit, named `_padding_<hex offset>`, and must be zero;
  it is always checked (`-EINVAL`);
- every `flags` field has a `*_FLAGS_MASK`; bits outside it are reserved and rejected with
  `-EINVAL`;
- GPU virtual addresses travel as `__u64` and must be below 4 GiB;
- a structure reached through `struct drm_sgxfive_obj_array` (`stride`, `count`, `array`) is
  versioned by its stride. A shorter (older) element is zero-extended; a longer (newer) one is
  accepted only if its unknown tail is zero. A non-zero count needs a stride of 1 to
  `DRM_SGXFIVE_OBJ_ARRAY_MAX_STRIDE` (256) bytes, otherwise `-EINVAL`, so a call reads little
  whatever it asks for. The job command structs (`transfer_cmd`, `render_cmd`) are versioned the
  same way by `cmd_stream_len`;
- an unknown ioctl number, query type or job type is `-EINVAL`. Numbers 0x0a to 0x0f are
  reserved.

## 3. Ioctls

| nr | ioctl | direction | does |
|---|---|---|---|
| 0x00 | `DEV_QUERY` | in/out | extensible device query (section 4) |
| 0x01 | `CREATE_BO` | in/out | a buffer object |
| 0x02 | `GET_BO_MMAP_OFFSET` | in/out | the fake offset for a CPU mapping |
| 0x03 | `CREATE_VM_CONTEXT` | in/out | a GPU address space |
| 0x04 | `DESTROY_VM_CONTEXT` | in | release the handle of one |
| 0x05 | `VM_MAP` | in | place a range of a BO in a VM |
| 0x06 | `VM_UNMAP` | in | remove one mapping |
| 0x07 | `CREATE_CONTEXT` | in/out | a context: a firmware queue bound to a VM |
| 0x08 | `DESTROY_CONTEXT` | in | wait for its jobs and release it |
| 0x09 | `SUBMIT_JOBS` | in/out | an array of jobs with sync operations |

Buffer handles are released with the core `DRM_IOCTL_GEM_CLOSE`. Synchronisation objects are the
core DRM syncobjs. No ioctl takes or returns a physical address, a firmware address or an address
in the kernel's alias region; the kernel owns the firmware.

## 4. DEV_QUERY

`type` names the output struct, `pointer` the buffer and `size` its length. With a NULL pointer
only the size the kernel knows is returned; a smaller buffer gets a truncated copy; a larger one
gets the known struct and `size` is set to what was written. Types are append-only:

| type | struct | content |
|---|---|---|
| `GPU_INFO` | `dev_query_gpu_info` | `CORE_ID`, `CORE_REVISION`, bridge revision, quirks |
| `FW_INFO` | `dev_query_fw_info` | the firmware's build, options, file format version and state |
| `HEAP_INFO` | `dev_query_heap_info` | the GPU address ranges of every VM (section 5) |
| `JOB_INFO` | `dev_query_job_info` | job types and the limits of `SUBMIT_JOBS` |
| `RUNTIME_INFO` | `dev_query_runtime_info` | pixel partitions 31, tile 32 x 16 |

Rules:

- `GPU_INFO` is answered from registers read at probe and the firmware's last reply to a misc-info
  request; the query never boots the firmware. `quirks` has `QUIRK_SAMPLE_CACHE` when the host
  bridge (PCI 00:00.0) is below revision 4, which is the Cedarview laptop's case: textures must
  then lie in the TEXTURE heap;
- the firmware's own core id, revision and `ddk_version` are valid only when
  `GPU_INFO_SW_VALID` is set. The kernel sends the misc-info request in every build, at the end of
  each boot of the firmware: right after the load at the first `CREATE_CONTEXT` and after each
  reset. An answer sets the flag; a reply that names another core or revision than the registers
  do, or a firmware built for a core other than 545, is kept and logged as a warning. No answer
  clears the flag and logs once until the firmware answers again; the boot does not fail for it.
  The flag is also cleared when the firmware stops, so while a reset restarts it `GPU_INFO` shows
  no firmware identity and `FW_INFO`'s `ddk_version` is 0, and a boot that fails leaves none of
  the firmware that is gone.
  Before the first boot the flag is clear and the three values are 0. The values taken from the
  firmware file (`ddk_build`, `build_options`, `fw_format`) are reported once the firmware is
  loaded, and the kernel loads the firmware at the first `CREATE_CONTEXT` of any type (the
  context needs kernel memory that only a loaded firmware provides; no other ioctl boots it):
  before that `FW_INFO` is all zeros with `state` OFF (`DRM_SGXFIVE_FW_STATE_OFF`). `state` is
  informational. Userspace may refuse a firmware build it does not know;
- `JOB_INFO` reports the limits of section 8.7 and `max_updates` 0.

The query on a fresh boot reads `ddk 0.0.0 build 0 options 0x0` and `fw_state 0`, and the first
context creation starts the firmware, so it has happened by the time the first job
completes (E022); the same creation asks the firmware for its identity, so the next `GPU_INFO`
has the firmware's own core and the `ddk_version` of `FW_INFO` (Q005, decided: the kernel asks in
every build, linux fork commit 32).

Evidence: E022, E017.

## 5. The GPU address space

### 5.1 Heaps

Each VM is one SGX page directory with 4 KiB pages and a 32-bit address space. The heaps are
reported by `HEAP_INFO`, one `struct drm_sgxfive_heap` (`base`, `size`, `flags`,
`page_size_log2` = 12) per `enum drm_sgxfive_heap_id`; every id is always reported, and
userspace never hardcodes a base. The kernel supports one layout, that of silicon with the
sample-cache quirk, and reports it whatever the host bridge revision. A heap a later
layout lacked would have size 0.

| id | heap | base | size | flags | holds |
|---|---|---|---|---|---|
| 0 | `GENERAL` | `0x3e000000` | `0xb1fff000` | | surfaces, background objects, streams |
| 1 | `TEXTURE` | `0xf0000000` | `0x0ffff000` | | textures (required there under the quirk) |
| 2 | `PDS_PIXEL` | `0x2e000000` | `0x01fff000` | | pixel PDS code and data; `PDS_EXEC_BASE` |
| 3 | `PDS_VERTEX` | `0x30400000` | `0x01bff000` | | vertex PDS code and data |
| 4 | `USSE_PIXEL` | `0x37000000` | `0x00500000` | fixed windows | pixel USSE code |
| 5 | `USSE_VERTEX` | `0x3c000000` | `0x00200000` | fixed windows | vertex USSE code |
| 6 | `KERNEL_CODE` | `0x30000000` | `0x0007f000` | reserved | alias of the firmware's code |
| 7 | `KERNEL_DATA` | `0x32000000` | `0x04fff000` | reserved | alias of the firmware's data |
| 8 | `PARAMETERS` | `0x10000000` | `0x10000000` | reserved | render contexts' parameter slots |
| 9 | `TA_DATA` | `0x20000000` | `0x0d000000` | reserved | render contexts' tiling data |

- **fixed windows**: the heap base is a USE code base, so a `DOUTU` reaches code only within the
  512 KiB window its `CBASE` field selects, counted from the heap base. `USSE_PIXEL` is the ten
  windows `USE_CODE_BASE_0..9`, `USSE_VERTEX` the four `USE_CODE_BASE_10..13`. These bases are
  programmed into global registers when the device boots, so they are the same in every VM;
- **reserved**: the kernel's. `VM_MAP` into a reserved heap fails with `-EINVAL`, so the
  firmware alias and the render slots can never be overwritten or probed by a client mapping;
- a mapping lies inside one non-reserved heap; it cannot straddle two. The last page of
  `GENERAL`, `TEXTURE`, `PDS_PIXEL` and `PDS_VERTEX` is never mappable (their sizes stop one page
  short); the two USSE heaps are whole windows;
- fields narrower than an address are the client's to respect: ISP stream and background object
  addresses are relative to `bif_3d_req_base` (a 1 MiB aligned window), `event_pixel_pds_exec`
  takes bits 31:4, pixel PDS pointers are relative to `PDS_EXEC_BASE`. The kernel validates
  only what protects other users (section 8.3).

### 5.2 Render slots

A render context takes the lowest free slot of its VM in `PARAMETERS` and `TA_DATA`; the 33rd
render context of one VM fails with `-ENOSPC`. The bus interface's TA request base and
`bif_3d_req_base` of its jobs are the slot base, which is 1 MiB aligned.

- parameter slot: 8 MiB at `0x10000000 + 8 MiB * slot`. Inside it the parameter buffer starts at
  `+0x1000` (page index 0 is never used) and holds `render_pb_pages` pages (`0x422` for a new
  context, `JOB_INFO`); the page table is at `+0x423000`, the scratch primitive block at
  `+0x463000` and the background object at `+0x464000`; the slot's mapped part ends at
  `+0x465000`;
- tiling data slot: 2 MiB of address space at `0x20000000 + 2 MiB * slot`, holding zeroed
  buffers sized for the largest target the context declares: tail pointers, then one page each
  of DPM control, OTPM and DPM state, then the region headers and the ZLS region headers, each
  rounded up to whole pages. The address space stays 2 MiB whatever the maximum; only the pages
  behind it shrink;
- all of it is mapped read-write in the context's VM, because the tiling accelerator, the DPM
  and the 3D pipe write it through the client's directory. A client's shaders can therefore
  write their own parameter buffer and page table; that corrupts only that client's own scenes.

Creating 32 render contexts of 64x64 targets in one VM took 4752 KiB of low memory each in one
run (E023). The pages are allocated with the creating process's memory accounting and are
below 4 GiB, write-combined.

### 5.3 The firmware alias

A VM that holds a render context maps the firmware's buffers at their kernel addresses
(`KERNEL_CODE`, `KERNEL_DATA`), because the firmware loads a render context's parameter buffer
through that context's page directory. The alias is created with the VM's first render context
and goes with its last; a VM with only transfer contexts has none. All of it is read-only except
the TA/3D control block, which the firmware writes in that window and which every render context
of the device shares. `VM_MAP` cannot reach these addresses, but the client's GPU programs can
(section 11). The block cannot be mapped read-only: with it so (the debug switch
`alias_ta3d_ro`) the first kick faults on its page before the parameter buffer load writes it,
and the job stalls (E319, one run). Whether a per-VM copy would do is Q006.

Transfers are different: a fill aimed at a page the context's directory maps read-only writes
nothing and faults (E021).

Evidence: E021, E023, E148, E319; Q006.

## 6. Buffer objects and VM contexts

### 6.1 CREATE_BO and GET_BO_MMAP_OFFSET

A BO is a shmem GEM object whose pages are below 4 GiB (the SGX MMU needs it) and are mapped
write-combined on the CPU. `size` must be non-zero and at most 1 GiB; it returns rounded up to
4 KiB. GPU access attributes belong to the mapping (`VM_MAP`), not the object.

- `flags` accepts `BO_ALLOW_CPU_ACCESS`; `BO_CPU_CACHED` is reserved (`-EINVAL`) until the cache
  coherency of GPU page-table entries is known;
- only a BO created with `ALLOW_CPU_ACCESS` can be mapped by the CPU. For any other
  `GET_BO_MMAP_OFFSET` fails with `-EINVAL`, and `mmap()` of a dma-buf exported from it fails
  with `-EACCES`. A handle that does not exist is `-ENOENT`.

### 6.2 VM contexts

`CREATE_VM_CONTEXT` returns a handle for a new, empty address space. An open file holds at most
32 (`DRM_SGXFIVE_FILE_MAX_VM_CONTEXTS`); the 33rd is `-ENOSPC`. `DESTROY_VM_CONTEXT` releases the
handle; the VM itself lives until the contexts bound to it are gone, and with it go its
mappings. An unknown handle is `-EINVAL`.

### 6.3 VM_MAP and VM_UNMAP

The client manages its VM. `VM_MAP` places `size` bytes of a BO, from `offset`, at `device_addr`:

- `device_addr` is 4 KiB aligned, non-zero and the range lies in one non-reserved heap;
  `offset` is 4 KiB aligned, `size` a non-zero multiple of 4 KiB, and the range lies within the
  BO; otherwise `-EINVAL`. A BO handle that does not exist is `-ENOENT`; an unknown VM handle
  is `-EINVAL`;
- a range that overlaps an existing mapping fails with `-EEXIST`;
- `MAP_READ_ONLY` sets the READONLY bit of the page-table entries: the GPU may read the mapping
  and a write faults. The bit holds for the writes of a transfer fill (E021) and of the triangle's
  pixel back end (E024); which unit wrote is not shown;
- the mapping is in the page tables when the ioctl returns, and the kernel invalidates the
  bus interface's cached translations before the next command reaches the firmware.

`VM_UNMAP` removes exactly one whole mapping: `device_addr` and `size` must equal a mapping's
(`-ENOENT` otherwise). The range is free for new mappings at once, but the pages stay pinned
until the GPU can no longer reach them: they are released only after a later firmware command
has made the bus interface drop its cached translations. The same holds for the page directory
of a destroyed VM, which is freed only then; the firmware keeps directory-list assignments by
directory address, so a directory freed early could be reused by another VM and run on stale
entries.

## 7. Contexts

A context is one firmware queue (a hardware context and its client command ring, all in kernel
memory) bound to one VM context for its lifetime. Its jobs run in submission order; the firmware
arbitrates between contexts.

`CREATE_CONTEXT` takes a `type`, `flags` (none defined, zero), `priority`
(`CTX_PRIORITY_NORMAL`, the only value; Q004 asks what others would do), the VM handle and,
for render contexts, `max_width` and `max_height`.

- `CTX_TYPE_TRANSFER`: for transfer jobs (blit, fill, copy). `max_width` and `max_height` are
  zero;
- `CTX_TYPE_RENDER`: for render jobs, one whole scene each. The kernel gives it a parameter
  buffer and the tiling data of one target, sized for `max_width` x `max_height` (1 to
  `render_max_width` and `render_max_height`, which are 4096 as the interface defines them; 0 is
  `-EINVAL`. The largest target any run drew is 256 x 256, E148), in the reserved
  heaps of its VM. It runs one of its jobs at a time: the next job of the context waits for the
  previous one's completion before it reaches the firmware;
- an unknown VM handle is `-EINVAL`; an open file holds at most 64 contexts
  (`DRM_SGXFIVE_FILE_MAX_CONTEXTS`), the 65th is `-ENOSPC`; at most 32 render contexts per VM;
- `DESTROY_CONTEXT` waits for the context's queued jobs, then releases it. A `SUBMIT_JOBS` call
  that reaches the context after it was destroyed fails at that job with `-EINVAL`. An unknown
  handle is `-EINVAL`;
- a context whose job faulted or hung is lost (section 10): its pending jobs complete with an
  error and further submissions fail with `-ECANCELED`.

Closing the file destroys its contexts before its VMs.

## 8. SUBMIT_JOBS

### 8.1 The call

An array of 1 to 16 jobs (`max_jobs`; a count of 0 is `-EINVAL`). Each job names a context, a type
that must equal the context's type, flags, a command (`cmd_stream`, 8-byte aligned, at most one
page of `cmd_stream_len` bytes), an array of at most 16 sync operations (`max_sync_ops`) and an
`updates` array, which must be all zero (`max_updates` is 0: memory updates are not supported and
any non-zero count, stride or pointer is `-EINVAL`).

The whole call is validated before any job is queued: the jobs, their commands, their contexts
and every sync operation. On a validation error of a job no job is queued and `jobs.count` is set to
the index of the failing job; errors in the job array itself (a count above 16, a stride of 0 or
above 256, a non-zero tail in a job struct) return before `jobs.count` is written. Only an error
while queuing (`-ENOMEM`, or a context destroyed by another thread in between) leaves the jobs
before that index queued, and `jobs.count` is then the index of the job that failed. There is no
buffer list: every mapped BO of the VM is resident, and dependencies are the explicit sync
operations.

A job whose context handle does not exist or does not match the job type fails with `-EINVAL`;
one whose context is lost, or whose file is banned, with `-ECANCELED`.

### 8.2 Sync operations

`struct drm_sgxfive_sync_op` is `{handle, flags, value}`. `flags` carry the handle type
(`SYNCOBJ` binary, 0; `TIMELINE_SYNCOBJ`, 1; larger is `-EINVAL`) and `SYNC_OP_FLAG_SIGNAL`
(wait if clear). `value` is the timeline point and must be zero for a binary syncobj.

- a signal syncobj must exist at the call (`-ENOENT`). A job signals its out-fence on every
  signal operation: a binary syncobj has its fence replaced, a timeline gets the point;
- a wait takes the fence its syncobj holds at the call (for a timeline, the fence at or before
  the point), or, if an earlier job of the same call signals that syncobj (the same binary
  syncobj, or the same timeline at the same point or a later one), waits for that earlier job.
  A wait on a syncobj with no fence and no earlier signal in the call is `-EINVAL`; a missing
  syncobj is `-ENOENT`;
- the job reaches the firmware once its waits have signalled and the earlier jobs of its
  context have been sent.

### 8.3 Transfer jobs

A transfer job's command is a `struct drm_sgxfive_transfer_cmd`: the register words of one
transfer, 0xa8 bytes in version 1, with GPU addresses of the job's VM encoded as each register
wants. The kernel builds the firmware command from it and fills what it owns: the size, flags,
fence status, the pixel partitions (31), the fence id and the updates. The firmware command and
what it does are in transfer.md.

Checks, all `-EINVAL`:

- `load_flags` has only `LOAD_YUV`, `LOAD_LUMAKEY` and `LOAD_FIR`; the register groups they name
  are loaded only with their flag;
- `double_pixel_partitions` is 0;
- `bif_3d_req_base` is 1 MiB aligned and in a user heap; `event_pixel_pds_exec` is in a user
  heap; `isp_rgn_base`, if non-zero, is in a user heap;
- `pds_exec_base` equals the base of `PDS_PIXEL`. The 3D pipe never sets that register, so a
  transfer that moved it would move the pixel programs of every later render, and the kernel
  keeps it at the heap base for every job, transfers included;
- `cmd_stream_len` is at least the known size (0xa8) and at most one page; a longer struct is
  accepted only if its tail is zero.

`SUBMIT_JOB_TRANSFER_DUMMY` makes a signal-only job: the firmware queues and completes it
without rendering, and `cmd_stream` and `cmd_stream_len` must be 0.

Transfers submitted from userspace are exact on the laptop: a chain of eight dummies, fills of a
whole surface, an inset rectangle, a rectangle across tiles and a single pixel, and copies of
three rectangles, each with every pixel as the CPU computes it and no dword outside the
rectangle changed (E022). The firmware side is E018 (dummies), E019 (fills) and E020 (copies).

Evidence: E018, E019, E020, E022.

### 8.4 Render jobs

A render job's command is a `struct drm_sgxfive_render_cmd`: the register words of one scene,
0x68 bytes in version 1. The firmware runs the TA over the VDM control stream, then the 3D pipe
over every tile; the fence signals once the pixel back end has finished. The kernel fills
everything that points into memory it owns or has device-wide effects: the parameter buffer and
tiling data of the context, the background object (built from `bgobj_words` and the size in
`mte_screen`), the pixel and vertex partitions, the depth and stencil controls (version 1 has
no depth or stencil buffer) and every firmware flag, sync and status word. The end-of-tile
program, written by userspace, holds the PBE state, so no colour buffer address appears in the
command.

Checks, all `-EINVAL`:

- `vdm_ctrl_stream_base` is 4-byte aligned and in a user heap; `event_pixel_pds_exec` is
  16-byte aligned and in a user heap. A render VM aliases the firmware, so a pointer into the
  kernel heaps would reach it;
- the target (`mte_screen`: width - 1 in 15:0, height - 1 in 31:16) is at most the
  `max_width` x `max_height` the context was created with;
- `isp_bgobj` sets no bit but 8 and 9;
- the tiling words `te_screen`, `te_mtile1`, `te_mtile2` and `te_mtile_stride` equal the layout
  of the `mte_screen` size, by which the kernel sets the context's tiling data. The layout of a
  target of width x height pixels is given in the header (tiles of 32 x 16; n = 4 macrotiles
  across and down at 640 x 480 or more, else 2; the macrotile is the tile count over n rounded up
  to a multiple of 4). A target smaller than the declared maximum uses the same buffers: the
  maximum's layout is the largest of all the sizes it covers.

The kernel does not check what the referenced memory holds: the VDM stream, the PDS and USSE
programs and the end-of-tile program are the client's, and run with the client's VM and no other.
libsgxfive sets bit 8 of the render context's `isp_ipfmisc` word, and every render of E148 is
exact with it set. What clearing the bit does to tiles no primitive touches above 64 x 64 is not
shown (Q029).

The first triangle submitted this way is exact: ten renders at 64x64, 128x96, 64x64 on a context
sized for 256x256 targets, and 64x64 after a faulting render, each with every pixel as the CPU
reference computes it and no dword outside the target changed. One loop iteration (build,
submit, wait, check) takes about 5 to 6 ms at 64x64 (E023). Thirteen target sizes from 64 x 64 to
256 x 256, up to sixteen tile rows and eight tile columns, are exact too, two renders each (E148).
The kernel's limit of 4096 x 4096 is not exercised by any run.

Evidence: E023, E148; Q029.

### 8.5 Scenes over several jobs

`SUBMIT_JOB_RENDER_GEOMETRY` makes a job tile its geometry into the context's scene and leave
the scene open, without rendering it: the TA kick is not the scene's last, and the job is done
when its TA is. The context's next render job adds to the same scene; the first job without the
flag renders everything the scene holds and closes it. A job after a closed scene starts a new
one.

Measured on the hardware (kernel pokes of the kick and render flag words, in a debug build):

- a kick that does not end the scene leaves its render waiting: a TA kick without the last-kick
  flag hangs the job and the context is lost (E051);
- two geometry kicks and a closing job store all their triangles; each kick adds its own (E052);
- rendering a scene empties it: a render after a closed scene stores only its own geometry, and
  a kick that appends to a closed scene with no new geometry stores only the background
  (E052, E053). The closing render's flag bits and a cleared first-kick bit on the next kick
  were tried and change nothing a later render holds (E051 to E053);
- the pixel-partition word of the kernel-built commands is the kernel's for a reason: of its
  bits, bit 1 and bit 2 and the value 0xffffffff hang the job, in a fill, a copy and a render
  alike (E049). The render flags word is the kernel's too (E050): a poke of bit 0 hangs the job,
  bits 1 and 4 complete it with no pixel, and bits 5, 9 and 0xffffffff fault. The kernel builds
  both words, and no client field reaches them.

**The scene's counts.** The kernel keeps a pending count for the context's RT data set and the
firmware an executed count in the set; the firmware cleans the set up, when the context is
destroyed, only once the two are equal. The firmware adds one when a kick that is not the scene's
last finishes, and one when a render with render flag `0x400` completes; the kernel raises its
count by the same at every kick it makes (a geometry job one, a render one, as the kernel always
sets `0x400`). Read on the hardware the two are equal after every job of scenes of one to four
kicks and every cleanup completes; one off either way, the cleanup times out and the kernel
resets the GPU (E314, E315, one run each). The kernel's earlier rule, one per scene, failed the
cleanup of every scene of several kicks (E303, E304). A recovery reset sets the count to the
sum of what the jobs it runs again add, by the same rule: a render whose `0x400` a debug poke
cleared adds nothing when it runs again, and the set's cleanup completes (E356, two rounds).

Evidence: E049 to E053, E303, E304, E314, E315, E356.

### 8.6 Out-fences and errors

A job's out-fence signals once the firmware reports completion, after the job's memory writes
are visible to write-combined CPU mappings. A job that does not complete signals its out-fence
with an error, which the fence status reports (a `sync_file` exported from the signalled syncobj
and `SYNC_IOC_FILE_INFO`); a syncobj wait itself succeeds. The job's memory writes may be
partial.

| error | meaning |
|---|---|
| `-EIO` | a GPU fault was blamed on the job |
| `-ETIMEDOUT` | a hang without a fault was blamed on the job |
| `-ECANCELED` | behind the blamed job, its context lost, or cancelled at a hold's end |
| `-ENOSPC` | a render whose scene needs more than the context's parameter buffer |

The last case completes, but the firmware had to run partial renders, which the kernel does not
support: the image is undefined. Nothing is reset, the context is not lost and its later jobs are
unaffected.

Other contexts' unfinished jobs run again after a recovery and signal without an error (E024),
except that the reset which ends a held recovery (a debug aid, section 10) does not run again the
jobs of a context that was destroyed meanwhile: they fail with `-ECANCELED`.

### 8.7 Limits

| limit | value | where |
|---|---|---|
| jobs per `SUBMIT_JOBS` | 16 | `JOB_INFO.max_jobs` |
| sync operations per job | 16 | `JOB_INFO.max_sync_ops` |
| memory updates per job | 0 | `JOB_INFO.max_updates` |
| command size | one page; known sizes 0xa8 (transfer), 0x68 (render) | `*_cmd_size` |
| array element stride | 256 bytes | `OBJ_ARRAY_MAX_STRIDE` |
| render parameter buffer | 0x422 pages | `JOB_INFO.render_pb_pages` |
| render target | 4096 x 4096 at most | `render_max_width`, `render_max_height` |
| BO size | 1 GiB | `CREATE_BO` |
| VM contexts per file | 32 | header |
| contexts per file | 64 | header |
| render contexts per VM | 32 | section 5.2 |
| jobs in flight per scheduler | 64 (one credit each; back-pressure, not an error) | kernel |

## 9. Scheduling

One scheduler serves the device and each context has an entity on it, so a context's jobs reach
the firmware in submission order. Running a job copies its firmware command into the context's
client ring, advances the write offset, creates the job's hardware fence and kicks the
firmware's queue for the context: the kernel command queue and the client ring are described in
transfer.md. All of it happens under the device lock, so a recovery never sees half a
submission. The firmware runs one transfer at a time and has no preemption: a job that holds the
GPU is a denial of service for the others until the hang rules of section 10 end it.

For the firmware's timing, the microkernel's tick lasts host-control dword 6 cycles of a
399.0 MHz clock, 997.48 Hz as the kernel boots it (E084). The host's timeouts below are the
kernel's own and do not follow it.

Evidence: E084.

## 10. Faults and recovery

Two detectors find a hang.

- **Fault**: while a job is in the firmware, a 50 ms watchdog polls the bus interface's
  interrupt status. When a fault is flagged it reads the faulting directory list, maps it to the
  page directory it names (the firmware's own list names none), and takes the oldest unfinished
  job of that directory as the suspect. It recovers only when the same job is still the oldest
  and unfinished at the next poll, because a fault at page 0 during dummy transfers does not
  stop the firmware;
- **Timeout**: each job has a 500 ms scheduler timeout. A job may only be waiting behind other
  contexts' work, so the kernel takes the GPU for hung when the device's oldest unfinished job
  is the same at two timeouts in a row. A job that runs for about a second or longer therefore
  fails, even if it would have finished.

A recovery blames the suspect: its context is lost, the suspect fails with `-EIO` (fault) or
`-ETIMEDOUT` (timeout) and the jobs queued behind it on that context with `-ECANCELED`. Then the
kernel halts the firmware without asking it to power off, rebuilds every firmware buffer from
the firmware file in place (the buffers keep their pages and addresses, so every context's
kernel memory stays where it is), rewrites every other context's client ring with its unfinished
jobs and boots the firmware again; those jobs then run again. A reset with no suspect (a
context's cleanup that the firmware did not answer) blames no one.

Measured on the laptop: a fill to an address mapped only in another VM, a fill queued just ahead
of a good fill on a second context, a write to a read-only mapping and a render with its stream
page unmapped each fault; each fault is a bus interface fault, reported in the kernel log as
stalling the job. The kernel stops the core, boots again in place and the firmware answers its
kick within 152 to 684 microseconds (upper bounds). The faulting job's wait fails 111 ms after
the submit, with `-EIO`; a later submit to its context returns `-ECANCELED`; the job on the
other context runs again and holds its colour; later jobs on new contexts are exact (E024).
Before recovery existed, a fill aimed at a read-only mapping left the core unable to power off
until the firmware's buffers were reloaded and it was booted again (E021, Q003: which event the
fault raises and what bit 5 of the interrupt status means are open).

**Ban.** Each fault or hang is counted against the open file that owns the guilty context. The
third within a minute bans the file: `CREATE_CONTEXT` and `SUBMIT_JOBS` on it fail with
`-ECANCELED`, while jobs it already queued on contexts that are not lost still run. The budget
and the ban belong to the open file; a new open of the render node starts afresh. E024 shows
the ban after the third fault: both creating a context and submitting to one that never faulted
return `-ECANCELED`.

**Error state.** A recovery that resets captures an error state (registers, control blocks and
the unfinished jobs of every context) and emits it as a devcoredump.

**Debug views** (`CONFIG_DRM_GMA500_SGXFIVE_DEBUG`, debugfs `dri/N/sgx/`, root only). `kpoke`
arms one-shot changes of the next job's words: `ta:N` and `rd:N` (the render's TA command and
render details) and `tq:N` (a transfer command) at its submit; `ctx:N`, `rtds:N`, `pb:N` and
`kw:N` (the render context's HW context, RT data set and PB descriptor, and the kernel's own words
for it: the access word, the pending count, the render target's status and the background update
list) at the next render's kick, after the kernel's own writes. `render_words` shows every word
of those structures and of the render details of the newest render context, a line each as the
poke that would set it. `hold_recovery` makes both detectors leave a hung job in the firmware,
its memory as the GPU left it, until `reset` is written; the kernel logs the detector's line and
a warning that recovery is held, then nothing until the reset (E354). A `reset` written while a
recovery is held is that recovery: the held job fails with its detector's error (`-EIO` for a
fault, `-ETIMEDOUT` for a timeout), the jobs behind it on its context are cancelled and the other
contexts' jobs run again, one reset in all; once the held job has finished a `reset` blames no one
(E354). The reset a failed render context cleanup asks for is not done while a recovery is held:
the hold stays and the context's memory waits for the reset that ends it (E355). `rtds_keep`
makes renders leave the RT data set's size words and out-of-memory counters as the previous job
left them.

Held on the laptop, a render that faulted on its unmapped stream page stops the firmware, not
only its job: the firmware answers no kernel command (the kernel's 500 ms wait for GETMISCINFO
ends the query, about 0.65 s from the shell), another context's fill does not run, the
firmware's tick no longer advances, and the bus interface keeps the fault until the reset; a job
given up by its client stayed queued and ran after the reset (E317, one run; since linux fork
commit 35 the reset that ends the hold cancels it with `-ECANCELED`, see below). Jobs hung without
a fault and a fault of the firmware's own write leave the firmware's commands unanswered too
(E318, E319, one run each; the tick was read for the fault only). A job hung in its pixel task
has finished its TA: before recovery its render memory holds the object and the control streams,
and the recovery zeroes the TA data and keeps the parameter buffer (E318, one run; the pixel
task's hang held twice).

The jobs another context queued while a recovery was held run again after the reset that ends it,
and the pending count the reset sets for each context is the sum of what its jobs run again add
(section 8.5): a render without render flag bit 10 run again adds nothing, and its cleanup
completes (E356, two rounds). The EDM gives each context's page directory one of the bus
interface's 15 client directory lists at its first kick (the 16th is its own) and the next one
again when another context has taken it; a fault's `CR_BIF_FAULT` names the list, and the kernel
reads the directory back from it (E360).

E024 does not show the timeout path, other kinds of fault or the core's behaviour without
recovery; every fault in its run was recovered.

Evidence: E021, E024, E317, E318, E319, E354, E355, E356, E360; Q003, Q028.

## 11. Security model

The node is for trusted clients (section 1). What holds, as implemented:

1. **One page directory per VM**, given to the firmware per job. The requestors of a fill and of
   a triangle translate through the context's directory: a fill into an address mapped only
   there lands, and a fill to an address mapped only in another VM faults without touching it. A
   client cannot address another process's memory or physical memory, since no mapping of either
   exists in its directory (E021, E024).
2. **Read-only entries are enforced** for the writes the fill and the triangle do: a write to a
   read-only mapping faults and writes nothing (E021, E024). The firmware's code and data are
   mapped read-only in render VMs, which by the same mechanism protects them, except the shared
   control block of section 5.3; no record writes to the alias itself.
3. **Kernel-owned firmware structures**: hardware contexts, client rings, control blocks, fence
   and status words and the kernel command queue are allocated, written and validated by the
   kernel only, except that the TA/3D control block is also mapped writable into every render VM
   (section 5.3). Raw firmware pointers, firmware sync objects and memory updates do not exist in
   the interface.
4. **Command words are reduced to rendering state**: addresses that the pixel pipe fetches from
   or runs code at must be in a user heap, and the registers with global effects
   (`PDS_EXEC_BASE`, partitions, the render flags) are the kernel's (section 8.3, section 8.4,
   E049, E050).
5. **Faults and hangs are recovered** (section 10) and bounded per open file by the ban, so a
   faulting client cannot hold the GPU past about a second on one hold; but the ban belongs to
   the open file, so reopening the node resets it and a client can fault again, each recovery
   costing about 20 to 27 ms of reset (E024).
6. **Some resources are bounded**: the per-file counts of VMs and contexts, the render contexts
   per VM and the size of one BO (section 8.7), and render context memory is charged to the
   creating process. The number of BOs, mappings per VM, opens and sync objects, and the total BO
   memory, are not bounded by the interface.

What it does not hold, and the reason the gate exists:

- a client's pixel program reads at least two SGX registers: `ldr` by register index reads
  `CORE_ID` (0x01150000) and `CORE_REVISION` at indexes 7 and 8 (E090). The kernel does not validate
  client programs, so the device's state is the client's to read;
- a render client's VM maps the firmware read-only, so its programs read the firmware's code
  and data, and writes the TA/3D control block, which all render contexts share. A client can
  corrupt that block, stalling or misdirecting other clients' renders; the block cannot simply be
  mapped read-only, since the firmware writes it through the client's directory (E319, Q006);
- a client's programs can write their own parameter buffer and page table (section 5.2);
- one client can hold the GPU for about a second before the timeout ends it (section 10).

Evidence: E021, E024, E049, E050, E090, E319; Q006.

## 12. UAPI header

`include/uapi/sgxfive_drm.h` is the contract: ioctl numbers and direction, every struct with its
fields, flags and masks, the enums, the sync operation encoding, the render target layout rule and
the sizes of the known command versions. libsgxfive's `sgxfive.h` wraps the ioctls
(`userspace/libsgxfive`); its mock (`sgxfive_mock.h`) runs the interface without a device, and the
kernel's KUnit tests (`sgxfive_job_test`, `sgxfive_vm_test`, `sgxfive_drv_test`) cover the
checks of sections 2, 6 and 8.

## 13. Open questions

- Q028: which of the recovery's reset steps a later job needs, now that a held fault is seen to
  stop the firmware (section 10);
- Q029: what the render context's own cleanup waits for once its RT data set is cleaned up,
  and which cleanup releases the parameter buffer (sections 8.5 and 10; a held job's cleanup now
  completes after the reset that blames it, E355);
- Q003: which event a bus-interface fault raises, and which requester each fault bit of the
  interrupt status names;
- Q004: what a transfer context's flag bits 1 and 4 and a priority above 0 do (the interface
  accepts only priority 0);
- Q006: whether a render client's VM can carry its own copy of the control block instead of a
  writable mapping of the device's (section 5.3).

The kernel follow-ups the 11.10 runs listed are done in linux fork commits 30 and 31 (b5a86838ae59,
the laptop's module since 11.12) and checked on the laptop:

- a `reset` written while a recovery is held recovers with the held job as its suspect: the held
  fault fails once with `-EIO`, the held hang once with `-ETIMEDOUT`, one reset each, no second
  fault or hang (E354);
- a recovery reset sets the RT data set's pending count by the per-kick rule; a render without
  `0x400` run again ends with both counts 0, a scene whose geometry kick ran again with equal
  counts after every kick, and every cleanup completes (E356); KUnit covers a render without
  `0x400` (commit 30);
- while recovery is held the detectors log one line and the hold's warning, then nothing until the
  reset (E354, 11.2 s of a held fault);
- a failed cleanup while recovery is held keeps the hold (E355);
- KUnit (commit 31) checks a render's words with the kernel pokes applied once on top of the
  kernel's own, the RT data set `rtds_keep` leaves as it was, and every line of `render_words`.

Q005 is decided: the kernel asks the firmware for its identity (GETMISCINFO) in every build, at
the end of each boot, so after the firmware load and after each reset, and `DEV_QUERY` reports it
without the debug option (section 4; linux fork commit 32, which also logs the answer). KUnit, in
builds with and without the debug option, checks an answer, a reply for another core, no answer,
the clear when the firmware stops, and `GPU_INFO` and `FW_INFO`'s `ddk_version` before and after
each.

The follow-ups found while writing E355 are done in linux fork commits 33 and 34: a failed render
context cleanup logs "no reset while recovery is held" instead of "resetting" when the reset is
dropped, decided under the device lock together with the reset (`__sgxfive_recover`, with KUnit
for the outcome; the log line is not captured), and the hold check reads the field with
`READ_ONCE` through `sgxfive_recovery_held()` at its three sites.

Decided (2026-11-07): a hold still lets a client give up on a job it queued
behind the held one, by destroying its context or closing its file, and the job's context stays
on the device's list until the job's fence signals. There were three rules for what the reset does
with such a job: run it again, as for any context's unfinished job (section 10); cancel it at
every reset; or cancel it only at the reset that ends a hold. The kernel takes the third: at the
reset that ends a held recovery the unfinished jobs of a closed context fail with `-ECANCELED`
(linux fork commit 35, `sgxfive_fence_cancel_closed`) instead of running again over memory their
client has gone from, where they faulted (E317). A reset with no hold keeps the old rule: they run
again. The fence of a cancelled job can be a sync dependency of another client's job, which then
fails with `-ECANCELED` where it would have waited; that follows from the rule and holds only for
a context that was closed during a hold. KUnit checks the cancel on closed contexts with and
without jobs and on an open one, the error an earlier blame gave being kept, and the debug reset
reporting the hold it ends; the reset itself needs the hardware. On the laptop (one run before the
commit, one after; a held fault, a fill on another context whose client is killed behind it, then
`reset`): before, the closed context's job ran again and the second stop of the firmware saw 1
event; after, the kernel logs "the hold ends: 1 job(s) of closed contexts cancelled", the second
stop sees 0 events, no bus fault follows and the GPU runs a fill and a triangle exactly. No client
reads the cancelled fence's status, so the `-ECANCELED` itself is KUnit's.
